"use client";

import { AnalysisResult } from "@/app/results/[id]/page";
import { clsx } from "clsx";
import { ShieldCheck, ShieldAlert, ShieldQuestion } from "lucide-react";

export default function VerdictCard({ result }: { result: AnalysisResult }) {
  const isReal = result.verdict === "LIKELY REAL";
  const isFake = result.verdict === "LIKELY AI GENERATED";
  const isInconclusive = result.verdict === "INCONCLUSIVE";

  return (
    <div className={clsx(
      "rounded border p-6 space-y-5 font-mono",
      isReal && "border-[#00ff46]/40 bg-[#00ff46]/5 shadow-[0_0_30px_rgba(0,255,70,0.08)]",
      isFake && "border-red-500/40 bg-red-500/5 shadow-[0_0_30px_rgba(239,68,68,0.08)]",
      isInconclusive && "border-yellow-500/40 bg-yellow-500/5",
    )}>
      {/* Verdict Header */}
      <div className="flex items-center gap-3">
        {isReal && <ShieldCheck className="w-8 h-8 text-[#00ff46] drop-shadow-[0_0_8px_#00ff46]" />}
        {isFake && <ShieldAlert className="w-8 h-8 text-red-400 drop-shadow-[0_0_8px_rgba(239,68,68,1)]" />}
        {isInconclusive && <ShieldQuestion className="w-8 h-8 text-yellow-400" />}
        <div>
          <p className="text-xs text-white/20 uppercase tracking-widest mb-0.5">$ verdict</p>
          <h2 className={clsx(
            "text-2xl font-bold tracking-wide",
            isReal && "text-[#00ff46]",
            isFake && "text-red-400",
            isInconclusive && "text-yellow-400",
          )}>
            {result.verdict}
          </h2>
        </div>
        <div className="ml-auto text-right">
          <p className="text-xs text-white/20 uppercase tracking-widest mb-0.5">confidence</p>
          <p className={clsx(
            "text-4xl font-bold",
            isReal && "text-[#00ff46] drop-shadow-[0_0_12px_#00ff46]",
            isFake && "text-red-400",
            isInconclusive && "text-yellow-400",
          )}>
            {result.confidence}%
          </p>
        </div>
      </div>

      {/* Summary */}
      <p className="text-white/50 text-sm leading-relaxed border-t border-white/10 pt-4 font-sans">
        {result.summary}
      </p>

      {/* Signal Breakdown */}
      <div className="grid grid-cols-2 gap-4 pt-1">
        <SignalBar label="AI Detector Score" value={result.ml_score} isFake={isFake} />
        <SignalBar label="Frequency Anomaly" value={result.frequency_score} isFake={isFake} />
      </div>

      {/* Disclaimer */}
      <p className="text-xs text-white/15 pt-2 font-sans">
        ⚠ Results are evidence to inform judgment, not definitive verdicts. Always verify with additional sources.
      </p>
    </div>
  );
}

function SignalBar({ label, value, isFake }: { label: string; value: number; isFake: boolean }) {
  return (
    <div>
      <div className="flex justify-between text-xs text-white/30 mb-1.5 font-mono">
        <span>{label}</span>
        <span>{value}%</span>
      </div>
      <div className="h-1 bg-white/10 rounded-full overflow-hidden">
        <div
          className={clsx(
            "h-full rounded-full transition-all duration-700",
            isFake ? "bg-red-500" : "bg-[#00ff46] shadow-[0_0_6px_#00ff46]"
          )}
          style={{ width: `${value}%` }}
        />
      </div>
    </div>
  );
}