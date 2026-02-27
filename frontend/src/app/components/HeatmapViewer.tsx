"use client";

import { useState } from "react";
import { Eye, EyeOff } from "lucide-react";

export default function HeatmapViewer({ heatmap }: { heatmap?: string }) {
    const [showHeatmap, setShowHeatmap] = useState(true);

    if (!heatmap) return null;

    return (
        <div className="rounded border border-[#00ff46]/15 bg-[#00ff46]/3 p-6 space-y-4 font-mono">
            <div className="flex items-center justify-between">
                <h2 className="text-xs text-[#00ff46]/60 uppercase tracking-widest">
                    $ grad-cam — detection heatmap
                </h2>
                <button
                    onClick={() => setShowHeatmap(!showHeatmap)}
                    className="flex items-center gap-2 text-xs text-white/60 hover:text-[#00ff46] transition-colors border border-[#00ff46]/20 hover:border-[#00ff46]/50 px-2 py-1 rounded"
                >
                    {showHeatmap
                        ? <><EyeOff className="w-3 h-3 mr-1" />Hide</>
                        : <><Eye className="w-3 h-3 mr-1" />Show</>
                    }
                </button>
            </div>

            {showHeatmap && (
                <div className="space-y-3">
                    <img
                        src={heatmap}
                        alt="Grad-CAM heatmap"
                        className="w-full rounded border border-[#00ff46]/20 object-contain max-h-96"
                    />
                    <div className="flex items-center gap-6 text-xs font-sans">
                        <div className="flex items-center gap-2">
                            <div className="w-3 h-3 rounded-sm bg-red-500" />
                            <span className="text-white/80">High suspicion</span>
                        </div>
                        <div className="flex items-center gap-2">
                            <div className="w-3 h-3 rounded-sm bg-yellow-500" />
                            <span className="text-white/80">Medium</span>
                        </div>
                        <div className="flex items-center gap-2">
                            <div className="w-3 h-3 rounded-sm bg-blue-500" />
                            <span className="text-white/80">Low suspicion</span>
                        </div>
                    </div>
                    <p className="text-xs text-white/60 font-sans">
                        Regions the model found most suspicious when making its verdict.
                    </p>
                </div>
            )}
        </div>
    );
}