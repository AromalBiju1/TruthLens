"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import UploadZone from "./components/UploadZone";
import { Shield, Zap, Search, Brain } from "lucide-react";
import logo from './assets/logo.png'
import Image from "next/image";
export default function Home() {
  const router = useRouter();
  const [isUploading, setIsUploading] = useState(false);

 const handleUpload = async (file: File) => {
  setIsUploading(true);
  try {
    const formData = new FormData();
    formData.append("file", file);

    const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/analyze`, {
      method: "POST",
      body: formData,
    });

    if (!res.ok) throw new Error(`Backend error: ${res.status}`);

    const data = await res.json();
    router.push(`/results/${data.job_id}`);
  } catch (err) {
    console.error("Upload failed:", err);
    setIsUploading(false);
  }
};

  return (
    <main className="min-h-screen bg-[#050a05] text-white font-mono">
      {/* Scanline overlay for texture */}
      <div className="pointer-events-none fixed inset-0 z-10 bg-[repeating-linear-gradient(0deg,transparent,transparent_2px,rgba(0,255,70,0.015)_2px,rgba(0,255,70,0.015)_4px)]" />

      {/* Nav */}
      <nav className="border-b border-[#00ff46]/20 px-6 py-4 flex items-center justify-between relative z-20">
        <div className="flex items-center gap-3 cursor-pointer">
  {/* The Icon */}
  <img 
    src={logo.src} 
    alt="TruthLens Icon" 
    className="h-10 w-10 object-contain mix-blend-screen opacity-90" 
  />
  
  {/* The Text */}
  <span className="font-mono text-xl font-bold tracking-tight text-white">
    Truth<span className="text-[#00ff46]">Lens</span>
  </span>
</div>
        <div className="flex items-center gap-4">
          <span className="text-white/60 text-xs tracking-widest">MEDIA FORENSICS v0.1</span>
          <a
            href="https://github.com/AromalBiju1/TruthLens"
            target="_blank"
            className="text-xs text-white hover:text-[#00ff46] transition-colors border border-[#00ff46]/20 hover:border-[#00ff46]/50 px-3 py-1 rounded"
          >
            GitHub ↗
          </a>
        </div>
      </nav>

      {/* Hero */}
      <section className="max-w-3xl mx-auto px-6 pt-24 pb-12 text-center relative z-20">
        <div className="inline-block mb-6 px-3 py-1 rounded border border-[#00ff46]/30 bg-[#00ff46]/5 text-[#00ff46] text-xs font-bold tracking-widest uppercase">
          ◈ Authenticity Verification System
        </div>
        <h1 className="text-5xl font-bold tracking-tight mb-5 text-white leading-tight">
          Is what you're{" "}
          <span className="text-[#00ff46] drop-shadow-[0_0_20px_#00ff46]">seeing</span>{" "}
          real?
        </h1>
        <p className="text-white/80 font-semibold text-base mb-12 max-w-xl mx-auto leading-relaxed font-sans">
          Upload any image or video. TruthLens runs it through deepfake detection models,
          reverse image search, and an AI agent — then delivers a transparent, evidence-backed verdict.
        </p>

        <UploadZone onUpload={handleUpload} isUploading={isUploading} />

        {/* Terminal-style hint */}
        <p className="mt-6 text-white/80 text-xs tracking-widest">
          $ supported formats: JPG · PNG · MP4 · MOV · WEBP
        </p>
      </section>


     {/* Features */}
<section className="w-full max-w-3xl mx-auto pt-8 pb-16 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 relative z-20">
  {[
    { icon: Brain, label: "CNN Ensemble", desc: "EfficientNet + CLIP deepfake detection" },
    { icon: Zap, label: "Frequency Analysis", desc: "DCT/FFT artifact detection" },
    { icon: Search, label: "Reverse Search", desc: "Web provenance cross-referencing" },
    { icon: Shield, label: "AI Agent Verdict", desc: "LLM synthesizes all signals" },
  ].map(({ icon: Icon, label, desc }) => (
    <div
      key={label}
      className="p-4 rounded border border-white/15 bg-[#00ff46]/5 hover:border-[#00ff46]/40 hover:bg-[#00ff46]/10 transition-all group flex flex-col h-full"
    >
      <Icon className="w-5 h-5 text-[#00ff46] mb-3 group-hover:drop-shadow-[0_0_6px_#00ff46] transition-all" />
      <div className="text-xs font-bold text-[#00ff46]/80 mb-2 tracking-wide uppercase">{label}</div>
      <div className="text-xs text-white/70 leading-relaxed font-sans mt-auto">{desc}</div>
    </div>
  ))}
</section>

      {/* Footer */}
      <footer className="text-center py-8 text-white/60 text-xs border-t border-[#00ff46]/10 tracking-widest relative z-20">
        TRUTHLENS — BUILT FOR MEDIA INTEGRITY · RESULTS ARE EVIDENCE, NOT FINAL VERDICTS
      </footer>
    </main>
  );
}