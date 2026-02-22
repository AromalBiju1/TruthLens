"use client";

import { useCallback, useState } from "react";
import { Upload, FileImage, FileVideo, Loader2 } from "lucide-react";
import { clsx } from "clsx";

interface UploadZoneProps {
  onUpload: (file: File) => void;
  isUploading: boolean;
}

export default function UploadZone({ onUpload, isUploading }: UploadZoneProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [preview, setPreview] = useState<string | null>(null);
  const [fileName, setFileName] = useState<string | null>(null);

  const handleFile = useCallback(
    (file: File) => {
      if (!file) return;
      setFileName(file.name);
      if (file.type.startsWith("image/")) {
        setPreview(URL.createObjectURL(file));
      }
      onUpload(file);
    },
    [onUpload]
  );

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragging(false);
      const file = e.dataTransfer.files[0];
      if (file) handleFile(file);
    },
    [handleFile]
  );

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) handleFile(file);
  };

  return (
    <div
      onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
      onDragLeave={() => setIsDragging(false)}
      onDrop={handleDrop}
      className={clsx(
        "relative rounded border-2 border-dashed transition-all duration-200 p-10 cursor-pointer group",
        isDragging
          ? "border-[#00ff46] bg-[#00ff46]/10 shadow-[0_0_30px_rgba(0,255,70,0.15)]"
          : "border-[#00ff46]/20 bg-[#00ff46]/5 hover:border-[#00ff46]/50 hover:bg-[#00ff46]/8 hover:shadow-[0_0_20px_rgba(0,255,70,0.08)]"
      )}
    >
      <input
        type="file"
        accept="image/*,video/*"
        onChange={handleChange}
        className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
        disabled={isUploading}
      />

      {isUploading ? (
        <div className="flex flex-col items-center gap-3">
          <Loader2 className="w-10 h-10 text-[#00ff46] animate-spin drop-shadow-[0_0_8px_#00ff46]" />
          <p className="text-[#00ff46]/60 text-sm font-mono tracking-widest">
            $ analyzing {fileName}...
          </p>
        </div>
      ) : preview ? (
        <div className="flex flex-col items-center gap-3">
          <div className="border border-[#00ff46]/30 rounded p-1">
            <img src={preview} alt="preview" className="max-h-40 rounded object-contain" />
          </div>
          <p className="text-[#00ff46]/40 text-xs font-mono">{fileName}</p>
          <p className="text-[#00ff46] text-sm font-mono tracking-wide">[ click or drop to change ]</p>
        </div>
      ) : (
        <div className="flex flex-col items-center gap-4">
          <div className="flex gap-4">
            <FileImage className="w-7 h-7 text-[#00ff46]/20 group-hover:text-[#00ff46]/60 transition-all" />
            <Upload className="w-7 h-7 text-[#00ff46]/40 group-hover:text-[#00ff46] group-hover:drop-shadow-[0_0_6px_#00ff46] transition-all" />
            <FileVideo className="w-7 h-7 text-[#00ff46]/20 group-hover:text-[#00ff46]/60 transition-all" />
          </div>
          <div className="text-center">
            <p className="text-white/60 font-sans mb-1">Drop your image or video here</p>
            <p className="text-white/20 text-sm font-sans">or click to browse</p>
          </div>
          <div className="px-5 py-2 rounded border border-[#00ff46]/40 bg-transparent hover:bg-[#00ff46]/10 hover:border-[#00ff46] transition-all text-sm font-mono text-[#00ff46] tracking-widest">
            $ SELECT FILE
          </div>
        </div>
      )}
    </div>
  );
}