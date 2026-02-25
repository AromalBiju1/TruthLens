# TruthLens 🔍

> **In a world where any image can be faked in seconds, TruthLens gives you the tools to fight back.**

TruthLens is a full-stack media forensics platform that analyzes images and videos for AI-generated or manipulated content. Users upload any media and receive a multi-signal authenticity report — powered by an ensemble of deep learning models, DCT frequency domain analysis, reverse image search provenance, and an LLM reasoning agent that weighs all evidence to produce a confidence-scored, evidence-backed verdict.

![Status](https://img.shields.io/badge/status-in%20development-yellow)
![License](https://img.shields.io/badge/license-MIT-blue)
![Stack](https://img.shields.io/badge/stack-Next.js%20%2B%20FastAPI%20%2B%20PyTorch-informational)

---

## ✨ Features

- 🧠 **CNN Ensemble Detection** — EfficientNet-B7 + CLIP-based classifier fine-tuned on FaceForensics++, DFDC, and Celeb-DF datasets
- 📡 **Frequency Domain Analysis** — DCT/FFT artifact detection that catches signals invisible to the human eye, generalized across new AI generators
- 🔎 **Reverse Image Search** — Cross-references the uploaded media against the web to establish provenance and detect reused or manipulated originals
- 🤖 **LLM Reasoning Agent** — An AI agent that synthesizes all signals (ML score, frequency anomalies, search provenance, EXIF metadata) into a transparent, explainable verdict
- 🗺️ **Grad-CAM Heatmaps** — Visual explanation of which regions of the image triggered the detection
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
│  - /analyze endpoint            │
│  - WebSocket progress streaming │
│  - Celery + Redis job queue     │
└──────┬──────────────┬───────────┘
       │              │
┌──────▼──────┐ ┌─────▼───────┐
│  ML Service │ │ Agent Layer │
│  PyTorch    │ │  LangChain  │
│  EfficientNet│ │  + Groq LLM │
│  CLIP + FFT │ └─────────────┘
└─────────────┘
               │
┌──────────────▼──────────────────┐
│    Supabase (PostgreSQL)        │
│    Cloudflare R2 (Media)        │
│    Upstash Redis (Queue)        │
└─────────────────────────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 14, TypeScript, TailwindCSS |
| Backend | FastAPI, Python 3.11+ |
| ML Models | PyTorch, HuggingFace Transformers, timm, OpenCV |
| Agent | LangChain + Groq (Llama 3) |
| Reverse Search | SerpAPI + TinEye API |
| Database | Supabase (PostgreSQL) |
| Media Storage | Cloudflare R2 |
| Queue | Celery + Upstash Redis |
| Deployment | Vercel (frontend) + Render (backend) |

---

## 🚀 Getting Started

### Prerequisites
- Node.js 18+
- Python 3.11+
- pip

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### Environment Variables

Create a `.env.local` in `/frontend`:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Create a `.env` in `/backend`:
```
SUPABASE_URL=
SUPABASE_KEY=
SERPAPI_KEY=
TINEYE_API_KEY=
GROQ_API_KEY=
CLOUDFLARE_R2_KEY=
CLOUDFLARE_R2_SECRET=
UPSTASH_REDIS_URL=
```

---

## 📁 Project Structure

```
TruthLens/
├── frontend/                  # Next.js app
│   ├── app/
│   │   ├── page.tsx           # Home / upload
│   │   ├── results/[id]/      # Results dashboard
│   │   └── api/               # Next.js API routes
│   └── components/
│       ├── UploadZone.tsx
│       ├── AnalysisProgress.tsx
│       ├── VerdictCard.tsx
│       ├── HeatmapViewer.tsx
│       └── ReverseSearchResults.tsx
│
├── backend/                   # FastAPI + ML
│   ├── main.py
│   ├── models/                # ML model wrappers
│   │   ├── efficientnet.py
│   │   ├── clip_classifier.py
│   │   └── frequency_analyzer.py
│   ├── agent/                 # LangChain agent + tools
│   │   ├── agent.py
│   │   └── tools/
│   │       ├── reverse_search.py
│   │       ├── exif_extractor.py
│   │       └── face_comparator.py
│   ├── workers/               # Celery tasks
│   └── requirements.txt
│
└── README.md
```

---

## 🧪 Detection Approach

TruthLens uses a **multi-signal ensemble** rather than relying on a single model — because no single model reliably catches all AI generators in 2025/2026.

| Signal | What it catches |
|---|---|
| EfficientNet-B4 | Visual artifacts, facial inconsistencies |
| CLIP Classifier | Generalizes to unseen generators including new diffusion models |
| DCT Frequency Analysis | Physics-level artifacts all generators leave behind |
| Reverse Image Search | Provenance — was this image online before, and where? |
| EXIF Metadata | Stripped metadata is a strong signal of manipulation |
| LLM Agent | Synthesizes all signals into a human-readable verdict |

---

## ⚠️ Limitations

TruthLens is transparent about what it can and cannot do:

- No detector catches 100% of AI-generated media — this is an active research problem
- Newer generators (MiniMax, Kling, Hailuo, etc.) are harder to detect than older GANs
- Results should be treated as **evidence to inform judgment**, not binary verdicts
- The system is updated periodically but will always lag behind the latest generators

---

## 📌 Roadmap

- [x] Repo setup
- [ ] FastAPI backend scaffold
- [ ] EfficientNet-B4 integration
- [ ] CLIP classifier integration
- [ ] DCT frequency analyzer
- [ ] Reverse image search (SerpAPI + TinEye)
- [ ] LangChain agent
- [ ] Next.js frontend
- [ ] WebSocket live progress
- [ ] Grad-CAM heatmap overlay
- [ ] Supabase + Cloudflare R2 integration
- [ ] Vercel + Render deployment
- [ ] Video support (frame-level + temporal)

---

## 🤝 Contributing

Contributions, issues and feature requests are welcome. Feel free to open an issue or submit a pull request.

---

## 📄 License

[MIT](LICENSE) © 2026 Aromal Biju