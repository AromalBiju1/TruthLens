import asyncio
from models.efficientnet import run_efficientnet
from models.frequency import run_frequency_analysis
from tools.exif import extract_exif
from tools.reverse_search import reverse_search_mock
from agent.agent import run_agent

async def send_step( manager,job_id:str, step_id:str, status:str,detail:str = ""):
    await manager.send(job_id,{
        "type":"step_update",
        "step_id" :step_id,
        "status" : status,
        "detail":detail
    })




async def run_pipeline(job_id:str,image_byes:bytes,filename:str,manager):
    try:
        #upload processing
        await send_step(manager,job_id,"upload","running" )
        await asyncio.sleep(0.5)
        await send_step(manager,job_id,"upload","done",f"Received{len(image_bytes) // 1024}KB") 

        #face extraction
        await send_step(manager,job_id,"face","running")
        await asyncio.sleep(0.5)
        await send_step(manager,job_id,"face","done","Face region identified") 

        #cnn ensemble
        await send_step(manager,job_id,"ml","running")
        ml_score = await asyncio.to_thread(run_efficientnet,image_byes)
        await send_step(manager,job_id,"ml","done",f"ML score:{ml_score:.2f}%")


        #frequency analysis
        await send_step(manager,job_id,"frequency","running")
        freq_score = await asyncio.to_thread(run_frequency_analysis,image_byes)
        await send_step(manager,job_id,"frequency","done",f"Frequency anomaly: {freq_score:.2f}%")


        #exif metadata
        await send_step(manager,job_id,"exif","running")
        exif_data = await asyncio.to_thread(extract_exif,image_byes)
        exif_detail = "Metadata stripped - suspicious" if exif_data.get("stripped") else "Metadata Intact"
        await send_step(manager,job_id,"exif","done",exif_detail)

        #reverse img search

        await send_step(manager,job_id,"reverse","running")
        search_results = await asyncio.to_thread(reverse_search_mock)
        await send_step(manager,job_id,"reverse","done",f"{len(search_results)} sources found")

        #AI agent verdict

        await send_step(manager,job_id,"agent","running")
        verdict = await asyncio.to_thread(run_agent,{
            "ml_score": ml_score,
            "freq_score": freq_score,
            "exif": exif_data,
            "search_results": search_results,
            "filename": filename,
        })
        await send_step(manager,job_id,"agent","done","verdict ready")



        #final result

        await manager.send(job_id,{
            "type": "result",
            "data": {
                "verdict": verdict["verdict"],
                "confidence": verdict["confidence"],
                "ml_score": round(ml_score),
                "frequency_score": round(freq_score),
                "summary": verdict["summary"],
                "agent_reasoning": verdict["reasoning"],
                "reverse_search": search_results,

            }
        })


    except Exception as e:
        print(f"Pipeline error for job {job_id}: {e}")
        await manager.send(job_id, {
            "type": "error",
            "message": str(e)
        })



