# TruthLens 🔍

> **In a world where any image can be faked in seconds, TruthLens gives you the tools to fight back.**

TruthLens is a full-stack media forensics platform that analyzes images and videos for AI-generated or manipulated content. Users upload any media and receive a multi-signal authenticity report — powered by an ensemble of deep learning models, DCT frequency domain analysis, reverse image search provenance, and an LLM reasoning agent that weighs all evidence to produce a confidence-scored, evidence-backed verdict.

![Status](https://img.shields.io/badge/status-in%20development-yellow)
![License](https://img.shields.io/badge/license-MIT-blue)
![Stack](https://img.shields.io/badge/stack-Next.js%20%2B%20FastAPI%20%2B%20PyTorch-informational)

---

## ✨ Features

- 🧠 **CNN Ensemble Detection** — EfficientNet-B7 + CLIP ViT-L/14 zero-shot classifier running concurrently on CUDA
- 👤 **Real Face Extraction** — InsightFace buffalo_l detects, crops and aligns faces before model inference
- 📡 **Frequency Domain Analysis** — DCT/FFT artifact detection that catches physics-level signals invisible to the human eye
- 🔎 **Reverse Image Search** — Cross-references uploaded media against the web to establish provenance
- 🤖 **LLM Reasoning Agent** — LangChain + Groq (llama-3.3-70b) synthesizes all signals into a transparent, explainable verdict
- 🗺️ **Grad-CAM Heatmaps** — Visual explanation of which facial regions triggered the detection
- 📊 **Confidence Scoring** — Never just "REAL" or "FAKE" — always a calibrated confidence score with evidence breakdown
- ⚡ **Real-time Progress** — WebSocket-powered live updates as each analysis step completes

---

## 🏗️ Architecture

```
┌─────────────────────────────────┐
│        Next.js Frontend         │
│  Upload → Live Progress → Results│
└──────────────┬──────────────────┘
               │ REST / WebSocket
┌──────────────▼──────────────────┐
│       FastAPI Backend (Python)  │
│  - POST /analyze                │
│  - WebSocket /ws/{job_id}       │
│  - Async background pipeline    │
│  - In-memory job store          │
└──────┬──────────────┬───────────┘
       │              │
┌──────▼──────────┐ ┌─▼───────────┐
│   ML Pipeline   │ │ Agent Layer │
│                 │ │             │
│ InsightFace     │ │ LangChain   │
│ EfficientNet-B7 │ │ + Groq LLM  │
│ CLIP ViT-L/14   │ │ llama-3.3   │
│ DCT/FFT Freq    │ │ 70b         │
│ Grad-CAM        │ └─────────────┘
└─────────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 14, TypeScript, TailwindCSS |
| Backend | FastAPI, Python 3.14, Async pipeline |
| Face Extraction | InsightFace buffalo_l on CUDA |
| ML Models | EfficientNet-B7 (FP16), CLIP ViT-L/14 |
| Frequency Analysis | DCT/FFT via NumPy + OpenCV |
| Explainability | Grad-CAM heatmap overlay |
| Agent | LangChain + Groq (llama-3.3-70b) |
| Reverse Search | DuckDuckGo Search |
| Deployment | Vercel (frontend) + Docker (backend) |

---

## 🚀 Getting Started

### Prerequisites
- Node.js 18+
- Python 3.11+
- NVIDIA GPU (recommended) or CPU

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Environment Variables

Create `.env.local` in `/frontend`:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Create `.env` in `/backend`:
```
GROQ_API_KEY=your_groq_key_here
SERPAPI_KEY=placeholder
```

---

## 📁 Project Structure

```
TruthLens/
├── frontend/
│   └── src/
│       ├── app/
│       │   ├── page.tsx               # Home / upload
│       │   └── results/[id]/
│       │       └── page.tsx           # Results dashboard
│       └── components/
│           ├── UploadZone.tsx
│           ├── AnalysisProgress.tsx
│           ├── VerdictCard.tsx
│           ├── HeatmapViewer.tsx
│           ├── AgentLog.tsx
│           └── ReverseSearchResults.tsx
│
└── backend/
    ├── main.py                        # FastAPI routes + WebSocket
    ├── pipeline.py                    # Analysis orchestrator
    ├── models/
    │   ├── efficientnet.py            # EfficientNet-B7 on CUDA
    │   ├── clip_classifier.py         # CLIP zero-shot classifier
    │   ├── frequency.py               # DCT/FFT analysis
    │   ├── face_extractor.py          # InsightFace extraction
    │   └── gradcam.py                 # Grad-CAM heatmap
    ├── agent/
    │   └── agent.py                   # LangChain + Groq verdict
    ├── tools/
    │   ├── exif.py                    # EXIF metadata extractor
    │   └── reverse_search.py          # DuckDuckGo search
    └── requirements.txt
```

---

## 🧪 Detection Approach

TruthLens uses a **multi-signal weighted ensemble** rather than relying on a single model — because no single model reliably catches all AI generators in 2025/2026.

| Signal | Weight | What it catches |
|---|---|---|
| EfficientNet-B7 | 40% | Visual artifacts, facial inconsistencies |
| CLIP ViT-L/14 | 35% | Generalizes to unseen generators including MiniMax, Kling, Hailuo |
| DCT/FFT Frequency | 25% | Physics-level artifacts all generators leave behind |
| EXIF Metadata | signal | Stripped metadata is a strong manipulation indicator |
| Reverse Image Search | signal | Provenance — was this image online before? |
| LLM Agent | synthesis | Weighs all signals into a human-readable verdict |

---

## ⚠️ Limitations

TruthLens is transparent about what it can and cannot do:

- No detector catches 100% of AI-generated media — this is an active research problem
- EfficientNet-B7 is not yet fine-tuned on deepfake datasets — fine-tuning on FaceForensics++/DFDC is planned
- Newer generators (MiniMax, Kling, Hailuo, Nano Banana Pro etc.) are harder to detect than older GANs
- Results should be treated as **evidence to inform judgment**, not binary verdicts

---

## 📌 Roadmap

- [x] Repo setup
- [x] Next.js frontend with black/green terminal UI
- [x] FastAPI backend with WebSocket streaming
- [x] EfficientNet-B7 on CUDA with FP16
- [x] CLIP zero-shot classifier
- [x] Weighted ensemble pipeline
- [x] InsightFace real face extraction on CUDA
- [x] DCT/FFT frequency domain analysis
- [x] EXIF metadata extraction
- [x] Grad-CAM heatmap visualization
- [x] LangChain + Groq agent verdict
- [x] DuckDuckGo reverse search
- [ ] Fine-tuning on FaceForensics++ / DFDC
- [ ] Video support (frame extraction + temporal LSTM)
- [ ] Test suite (unit + integration + model evaluation)
- [ ] Docker deployment
- [ ] Vercel deployment

---

## 🤝 Contributing

Contributions, issues and feature requests are welcome. Feel free to open an issue or submit a pull request.

---

## 📄 License

[MIT](LICENSE) © 2026 Aromal Biju