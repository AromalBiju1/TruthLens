"use client";

import { Terminal } from "lucide-react";

export default function AgentLog({ reasoning }: { reasoning: string[] }) {
  return (
    <div className="rounded border border-[#00ff46]/15 bg-black p-6 space-y-4 font-mono">
      <div className="flex items-center gap-2 border-b border-[#00ff46]/10 pb-3">
        <Terminal className="w-4 h-4 text-[#00ff46]" />
        <h2 className="text-xs text-[#00ff46]/60 uppercase tracking-widest">Agent Reasoning Chain</h2>
        <span className="ml-auto text-xs text-white/20">{reasoning.length} steps</span>
      </div>
      <div className="space-y-2">
        {reasoning.map((step, i) => (
          <div key={i} className="flex gap-3 text-sm group">
            <span className="text-white/30 text-xs flex-shrink-0 mt-0.5">
              [{String(i + 1).padStart(2, "0")}]
            </span>
            <p className="text-[#00ff46]/60 leading-relaxed group-hover:text-[#00ff46]/80 transition-colors font-sans text-xs">
              {step}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}