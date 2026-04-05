"use client";
import React from "react";
import { useScrollStore } from "@/lib/scrollStore";

const MicroscopeFrame = () => {
  const progress = useScrollStore((s) => s.progress);
  const depthPercent = Math.round(progress * 100);

  return (
    <div className="fixed inset-0 pointer-events-none z-40 overflow-hidden mix-blend-screen">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,transparent_40%,var(--bg)_100%)] opacity-80" />
      <svg className="absolute inset-0 w-full h-full opacity-15">
        <circle cx="50%" cy="50%" r="48%" stroke="var(--glow)" strokeWidth="1" fill="none" />
      </svg>
      {/* Corner Brackets */}
      <div className="absolute top-8 left-8 w-16 h-16 border-t border-l border-[var(--glow)] opacity-50" />
      <div className="absolute top-8 right-8 w-16 h-16 border-t border-r border-[var(--glow)] opacity-50" />
      <div className="absolute bottom-8 left-8 w-16 h-16 border-b border-l border-[var(--glow)] opacity-50" />
      <div className="absolute bottom-8 right-8 w-16 h-16 border-b border-r border-[var(--glow)] opacity-50" />
      
      {/* Readout */}
      <div className="absolute bottom-10 right-10 flex flex-col items-end gap-1 font-space text-[10px] tracking-widest text-[var(--glow)] opacity-80">
        <span>sys.optics_online</span>
        <span>DEPTH: {depthPercent}%</span>
      </div>
    </div>
  );
};
export default MicroscopeFrame;
