import os
import json
from langchain_groq import ChatGroq
from langchain.schema import HumanMessage,SystemMessage

def run_agent(signals: dict)-> dict:
    """takes all analysis and uses groq llm to synthesize a final verdict with reasoning outputs"""
    efficientnet_score = signals.get("efficentnet_score",50)
    clip_score = signals.get("clip_score",50)
    freq_score = signals.get("freq_Score",50)
    ensemble_score = signals.get("ensemble_score",50)
    exif = signals.get("exif",{})
    search_results = signals.get("search_results",[])
    filename = signals.get("filename","unknown")

    exif_summary = (
        "EXIF metadata is completely stripped - strong manipulation signal"
        if exif.get("stripped")
        else f"EXIF intact- camera:{exif.get('camera')},software:{exif.get('software')},date:{exif.get('date_taken')}"

          )

    search_summary =(
        f"{len(search_results)} web sources found matching this image"
        if search_results
        else "No matching sources found on the wbe"
     )  

    system_prompt = """ You are TruthLens,a media forensics AI agent specialized in detecting AI-generated and manipulated images.
     1. Reason through each signal carefully
     2. Note Where signals agree or conflict
     3. Weigh the evidence holistically
     4. Produce a final verdict

     Respond only with valid JSON object in this exact format:
     {
      "verdict": "LIKELY AI GENERATED" | "LIKELY REAL" | "INCONCLUSIVE",
      "confidence": <integer 0-100>,
      "summary": "<2-3 sentence human-readable summary>",
       "reasoning": [
            "<step 1>",
            "<step 2>",
            "<step 3>",
            "<step 4 — final verdict rationale>"
  ]
     }

     Be honest about uncertainty. if signals conflict,say INCONCLUSIVE
     Never overclaim - this is a forensic tool, not an oracle
     """

    user_prompt = f""" Analyze the following signals for : {filename}
   SIGNAL 1 — EfficientNet-B7 CNN Score: {efficientnet_score:.1f}%
(Trained on visual artifacts — 0% = real, 100% = AI-generated)

SIGNAL 2 — CLIP Zero-Shot Score: {clip_score:.1f}%
(Semantic understanding — generalizes to new generators like MiniMax, Kling)

SIGNAL 3 — Frequency Domain Anomaly: {freq_score:.1f}%
(DCT/FFT physics-level artifacts — all generators leave traces here)

SIGNAL 4 — Weighted Ensemble Score: {ensemble_score:.1f}%
(EfficientNet×0.40 + CLIP×0.35 + Frequency×0.25)

SIGNAL 5 — EXIF Metadata: {exif_summary}

SIGNAL 6 — Reverse Image Search: {search_summary}

Note where signals agree or conflict, then produce your verdict JSON."""

    try:
        llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0.1,
            api_key=os.getenv("GROQ_API_KEY"),
        )

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(user_prompt),
        ]

        response = llm.invoke(messages)
        content = response.content.strip()

        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        return json.loads(content.strip())
    except json.JSONDecodeError as e:
        print(f"{TruthLens} Agent json parse rror {e}")
        return fallback_verdict(ensemble_score)



def fallback_verdict(ensemble_score:float)->dict:
    if ensemble_score > 65:
        verdict = "LIKELY AI GENERATED"
    elif ensemble_score < 35:
        verdict =  "LIKELY REAL" 
    else:
        verdict = "INCONCLUSIVE" 
    return{
        "verdict" : verdict,
        "confidence" : round(abs(ensemble_score - 50)*2),
        "summary" : f"Ensemble score of {ensemble_score:.0f}% suggests {verdict.lower()}. LLM Agent unavailable(rule based fallback used)",
        "reasoning": [
            f"Ensemble score: {ensemble_score:.0f}%",
            f"Verdict threshold: >65% = AI-generated, <35% = real, else inconclusive",
            f"Final verdict: {verdict}",
            "Note: LLM agent unavailable, fallback used"
        ]
    }         





