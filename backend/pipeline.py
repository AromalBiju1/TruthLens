import asyncio
from models.efficientnet import run_efficientnet,get_model_and_transform
from models.clip_classifier import run_clip
from models.frequency import frequency_analysis
from tools.exif import extract_exif
from tools.reverse_search import reverse_search
from agent.agent import run_agent
from models.face_extractor import extract_face, face_to_bytes
from models.gradcam import generate_heatmap
from functools import partial

WEIGHTS = {
    "efficientnet": 0.40,
    "clip":         0.35,
    "frequency":    0.25,
}

def compute_ensemble(efficientnet_score: float, clip_score: float, freq_score: float) -> float:
    return round(
        efficientnet_score * WEIGHTS["efficientnet"] +
        clip_score         * WEIGHTS["clip"] +
        freq_score         * WEIGHTS["frequency"],
        2
    )

async def send_step(manager, job_id: str, step_id: str, status: str, detail: str = ""):
    await manager.send(job_id, {
        "type": "step_update",
        "step_id": step_id,
        "status": status,
        "detail": detail
    })

async def run_pipeline(job_id: str, image_bytes: bytes, filename: str, manager):
    try:
        # upload
        await send_step(manager, job_id, "upload", "running")
        await asyncio.sleep(0.3)
        await send_step(manager, job_id, "upload", "done", f"Received {len(image_bytes) // 1024}KB")

        # face extraction
        await send_step(manager, job_id, "face", "running")
        face_array, face_meta = await asyncio.to_thread(extract_face, image_bytes)

        if face_array is None:
            await send_step(manager, job_id, "face", "done", face_meta["message"])
            analysis_bytes = image_bytes
        else:
            await send_step(manager, job_id, "face", "done",
                f"{face_meta['faces_found']} face(s) — confidence: {face_meta['confidence']}%")
            analysis_bytes = face_to_bytes(face_array)

        # EfficientNet + CLIP running concurrently
        await send_step(manager, job_id, "ml", "running", "Running EfficientNet-B7 + CLIP...")
        efficientnet_score, clip_score = await asyncio.gather(
            asyncio.to_thread(run_efficientnet, analysis_bytes),
            asyncio.to_thread(run_clip, analysis_bytes),
        )
        await send_step(manager, job_id, "ml", "done",
            f"EfficientNet: {efficientnet_score:.1f}% | CLIP: {clip_score:.1f}%")
        
        #gradcam heat map

        await send_step(manager, job_id, "ml", "running", "Generating Grad-CAM heatmap...")
        model, transform, device = get_model_and_transform()
        loop = asyncio.get_event_loop()
        heatmap_b64 = await loop.run_in_executor(
            None,
            partial(generate_heatmap, model, transform, device, analysis_bytes)
        )

        # frequency
        await send_step(manager, job_id, "frequency", "running")
        freq_score = await asyncio.to_thread(frequency_analysis, image_bytes)
        final_ensemble = compute_ensemble(efficientnet_score, clip_score, freq_score)
        await send_step(manager, job_id, "frequency", "done", f"Frequency anomaly: {freq_score:.1f}%")

        # exif
        await send_step(manager, job_id, "exif", "running")
        exif_data = await asyncio.to_thread(extract_exif, image_bytes)
        exif_stripped = exif_data.get("stripped", True)
        exif_expected = exif_data.get("stripped_expected", False)
        fmt = exif_data.get("format", "")
        if not exif_stripped:
            exif_detail = f"Metadata intact (camera: {exif_data.get('camera') or 'unknown'})"
        elif exif_expected:
            exif_detail = f"No metadata ({fmt}) — normal for web images, not suspicious"
        else:
            exif_detail = "Metadata stripped — moderate manipulation signal"
        await send_step(manager, job_id, "exif", "done", exif_detail)

        # reverse search
        await send_step(manager, job_id, "reverse", "running")
        search_results = await asyncio.to_thread(reverse_search,image_bytes,filename)
        await send_step(manager, job_id, "reverse", "done", f"{len(search_results)} sources found")

        # agent
        await send_step(manager, job_id, "agent", "running", "Synthesizing all signals...")
        verdict = await asyncio.to_thread(run_agent, {
            "efficientnet_score": efficientnet_score,
            "clip_score": clip_score,
            "freq_score": freq_score,
            "ensemble_score": final_ensemble,
            "exif": exif_data,
            "search_results": search_results,
            "filename": filename,
        })
        await send_step(manager, job_id, "agent", "done", "Verdict ready")

        # final result
        await manager.send(job_id, {
            "type": "result",
            "data": {
                "verdict": verdict["verdict"],
                "confidence": verdict["confidence"],
                "efficientnet_score": round(efficientnet_score),
                "clip_score": round(clip_score),
                "ml_score": round(final_ensemble),
                "frequency_score": round(freq_score),
                "summary": verdict["summary"],
                "agent_reasoning": verdict["reasoning"],
                "reverse_search": search_results,
                "heatmap":heatmap_b64
            }
        })

    except Exception as e:
        print(f"[TruthLens] Pipeline error for job {job_id}: {e}")
        await manager.send(job_id, {
            "type": "error",
            "message": str(e)
        })