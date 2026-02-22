"use client";

import { CheckCircle, Circle, Loader2, XCircle } from "lucide-react";
import { AnalysisStep } from "@/app/results/[id]/page";
import { clsx } from "clsx";

export default function AnalysisProgress({ steps }: { steps: AnalysisStep[] }) {
  return (
    <div className="rounded border border-[#00ff46]/15 bg-[#00ff46]/3 p-6 space-y-4 font-mono">
      <h2 className="text-xs text-white uppercase tracking-widest">$ analysis pipeline</h2>
      <div className="space-y-3">
        {steps.map((step) => (
          <div key={step.id} className="flex items-start gap-3">
            <div className="mt-0.5 flex-shrink-0">
              {step.status === "done" && (
                <CheckCircle className="w-4 h-4 text-[#00ff46] drop-shadow-[0_0_4px_#00ff46]" />
              )}
              {step.status === "running" && (
                <Loader2 className="w-4 h-4 text-[#00ff46] animate-spin" />
              )}
              {step.status === "pending" && (
                <Circle className="w-4 h-4 text-white" />
              )}
              {step.status === "error" && (
                <XCircle className="w-4 h-4 text-red-400" />
              )}
            </div>
            <div className="flex-1">
              <p className={clsx(
                "text-sm",
                step.status === "done" && "text-[#00ff46]",
                step.status === "running" && "text-[#00ff46]/80",
                step.status === "pending" && "text-white",
                step.status === "error" && "text-red-400",
              )}>
                {step.status === "running" && <span className="mr-1 text-[#00ff46]/50">▶</span>}
                {step.status === "done" && <span className="mr-1 text-[#00ff46]/50">✓</span>}
                {step.status === "pending" && <span className="mr-1 text-white">·</span>}
                {step.label}
              </p>
              {step.detail && (
                <p className="text-xs text-white mt-0.5 font-sans ml-4">{step.detail}</p>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}