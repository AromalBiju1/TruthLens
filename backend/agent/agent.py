import os
import json
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage


def run_agent(signals: dict) -> dict:
    """Takes all analysis signals and uses Groq LLM to synthesize a final verdict."""
    # FIX: typos in key names were causing silent 50.0 defaults
    efficientnet_score = signals.get("efficientnet_score", 50)
    clip_score         = signals.get("clip_score", 50)
    freq_score         = signals.get("freq_score", 50)
    ensemble_score     = signals.get("ensemble_score", 50)
    exif               = signals.get("exif", {})
    search_results     = signals.get("search_results", [])
    filename           = signals.get("filename", "unknown")

    # EXIF summary — differentiate between "expected no EXIF" (webp/png from web)
    # vs genuinely suspicious stripping on camera-format files
    stripped = exif.get("stripped", True)
    stripped_expected = exif.get("stripped_expected", False)
    if not stripped:
        exif_summary = (
            f"EXIF intact — camera: {exif.get('camera')}, "
            f"software: {exif.get('software')}, date: {exif.get('date_taken')}"
        )
    elif stripped_expected:
        exif_summary = (
            "No EXIF metadata — expected for this file format (WebP/PNG from web). "
            "Not a manipulation signal on its own."
        )
    else:
        exif_summary = "EXIF metadata completely stripped — moderate manipulation signal"

    search_summary = (
        f"{len(search_results)} web sources found matching this image"
        if search_results
        else "No matching sources found on the web"
    )

    system_prompt = """You are TruthLens, a media forensics AI agent specialized in detecting AI-generated and manipulated images.

Your job is to holistically weigh multiple imperfect signals and reason to a calibrated verdict.

SIGNAL INTERPRETATION GUIDE:
- EfficientNet CNN Score: trained visual artifact detector. <35% = likely real, >65% = likely AI, 35-65% = uncertain
- CLIP Zero-Shot Score: semantic similarity. <40% = likely real, >60% = likely AI, 40-60% = uncertain  
- Frequency Anomaly: DCT/FFT physics artifacts. <30% = clean, >60% = suspicious, 30-60% = ambiguous
- Weighted Ensemble: aggregate of above (EfficientNet×0.40 + CLIP×0.35 + Frequency×0.25)
- EXIF: stripped EXIF on JPEG = suspicious; missing EXIF on WebP/PNG from web = normal
- Reverse Search: finding the image online suggests it's a known real photo (lowers suspicion)

RULES:
1. If signals conflict significantly (e.g. CNN says real but freq says AI), default to INCONCLUSIVE
2. Ensemble below 45% → lean toward LIKELY REAL
3. Ensemble above 65% AND CNN + CLIP both agree → LIKELY AI GENERATED
4. Never overclaim — false positives on real people are worse than false negatives
5. A real press photo of a public figure is very likely to have its EXIF stripped by media organizations

Respond ONLY with a valid JSON object in this exact format:
{
  "verdict": "LIKELY AI GENERATED" | "LIKELY REAL" | "INCONCLUSIVE",
  "confidence": <integer 0-100>,
  "summary": "<2-3 sentence human-readable summary>",
  "reasoning": [
    "<step 1: evaluate each signal>",
    "<step 2: note agreements and conflicts>",
    "<step 3: weigh context clues>",
    "<step 4: final verdict rationale>"
  ]
}"""

    user_prompt = f"""Analyze the following signals for image: {filename}

SIGNAL 1 — EfficientNet CNN Score: {efficientnet_score:.1f}%
(Visual artifact detector — 0% = real, 100% = AI-generated)

SIGNAL 2 — CLIP Zero-Shot Score: {clip_score:.1f}%
(Semantic image-text similarity — generalizes to new generators)

SIGNAL 3 — Frequency Domain Anomaly: {freq_score:.1f}%
(DCT/FFT physics-level artifacts — AI generators leave traces here)

SIGNAL 4 — Weighted Ensemble Score: {ensemble_score:.1f}%
(EfficientNet×0.40 + CLIP×0.35 + Frequency×0.25)

SIGNAL 5 — EXIF Metadata: {exif_summary}

SIGNAL 6 — Reverse Image Search: {search_summary}

Reason through signal agreements and conflicts, then produce your verdict JSON."""

    try:
        llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0.1,
            api_key=os.getenv("GROQ_API_KEY"),
        )

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]

        response = llm.invoke(messages)
        content = response.content.strip()

        # Strip markdown code fences if present
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]

        return json.loads(content.strip())

    except json.JSONDecodeError as e:
        print(f"[TruthLens] Agent JSON parse error: {e}")
        return fallback_verdict(ensemble_score)
    except Exception as e:
        print(f"[TruthLens] Agent error: {e}")
        return fallback_verdict(ensemble_score)


def fallback_verdict(ensemble_score: float) -> dict:
    if ensemble_score > 65:
        verdict = "LIKELY AI GENERATED"
    elif ensemble_score < 40:   # raised threshold from 35→40 to reduce false positives
        verdict = "LIKELY REAL"
    else:
        verdict = "INCONCLUSIVE"

    return {
        "verdict": verdict,
        "confidence": round(abs(ensemble_score - 50) * 2),
        "summary": (
            f"Ensemble score of {ensemble_score:.0f}% suggests {verdict.lower()}. "
            "LLM agent unavailable — rule-based fallback used."
        ),
        "reasoning": [
            f"Ensemble score: {ensemble_score:.0f}%",
            "Verdict thresholds: >65% = AI-generated, <40% = real, else inconclusive",
            f"Final verdict: {verdict}",
            "Note: LLM agent unavailable, fallback used",
        ],
    }
