"use client";
import React from "react";

export default function Dashboard() {
  return (
    <div className="min-h-screen bg-[var(--bg)] flex items-center justify-center font-jetbrains">
      <div className="text-center">
        <h1 className="font-bebas text-6xl text-[var(--glow)] mb-4">BLUE DASHBOARD</h1>
        <p className="text-[var(--text)] tracking-widest text-sm">{"// coming soon."}</p>
        <button 
          onClick={() => window.history.back()}
          className="mt-8 border border-[var(--glow)] text-[var(--glow)] px-6 py-2 hover:bg-[var(--glow)] hover:text-[var(--bg)] transition-colors"
        >
          RETURN TO MICROSCOPE
        </button>
      </div>
    </div>
  );
}
