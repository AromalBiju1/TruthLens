"use client";

import { Search, ExternalLink } from "lucide-react";

interface SearchResult {
  url: string;
  title: string;
  thumbnail: string;
  date?: string;
}

export default function ReverseSearchResults({ results }: { results: SearchResult[] }) {
  return (
    <div className="rounded border border-[#00ff46]/15 bg-[#00ff46]/3 p-6 space-y-4 font-mono">
      <div className="flex items-center gap-2">
        <Search className="w-4 h-4 text-[#00ff46]" />
        <h2 className="text-xs text-[#00ff46]/60 uppercase tracking-widest">$ reverse image search — web provenance</h2>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {results.map((r, i) => (
          <a
            key={i}
            href={r.url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex gap-3 p-3 rounded border border-[#00ff46]/10 hover:border-[#00ff46]/40 hover:bg-[#00ff46]/5 transition-all group"
          >
            {r.thumbnail && (
              <img
                src={r.thumbnail}
                alt=""
                className="w-12 h-12 rounded object-cover flex-shrink-0 bg-white/5 border border-[#00ff46]/10"
              />
            )}
            <div className="min-w-0 flex-1">
              <p className="text-xs text-white/70 font-medium truncate group-hover:text-white transition-colors font-sans">
                {r.title}
              </p>
              <p className="text-xs text-white/20 truncate mt-0.5 font-sans">{r.url}</p>
              {r.date && (
                <p className="text-xs text-[#00ff46]/50 mt-1">⊕ {r.date}</p>
              )}
            </div>
            <ExternalLink className="w-3 h-3 text-white/10 group-hover:text-[#00ff46]/50 flex-shrink-0 mt-0.5 transition-colors" />
          </a>
        ))}
      </div>
    </div>
  );
}