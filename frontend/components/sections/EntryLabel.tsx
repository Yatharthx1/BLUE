"use client";
import React from 'react';
import { motion } from 'framer-motion';
import { useScrollStore } from '@/lib/scrollStore';

const EntryLabel = () => {
  const progress = useScrollStore((s) => s.progress);
  
  let opacity = 1;
  if (progress > 0.08 && progress <= 0.12) {
    opacity = 1 - (progress - 0.08) / 0.04;
  } else if (progress > 0.12) {
    opacity = 0;
  }

  return (
    <motion.div 
      className="fixed inset-0 flex flex-col items-center justify-center pointer-events-none z-10"
      animate={{ opacity }}
      transition={{ ease: "linear", duration: 0.1 }}
    >
      <div className="flex flex-col items-center -mt-20">
        <h1 
          className="font-bebas text-[180px] leading-none text-[var(--glow)] drop-shadow-[0_0_15px_rgba(0,255,209,0.4)] tracking-wider"
        >
          BLUE
        </h1>
        <p className="font-jetbrains text-[16px] text-[var(--muted)] -mt-6 tracking-widest">
          {"// water quality. decoded."}
        </p>
      </div>

      <div className="absolute bottom-20 flex flex-col items-center gap-2 font-space text-xs text-[var(--glow)] animate-pulse">
        <span>SCROLL TO ANALYZE</span>
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <line x1="12" y1="5" x2="12" y2="19"></line>
          <polyline points="19 12 12 19 5 12"></polyline>
        </svg>
      </div>
    </motion.div>
  );
};
export default EntryLabel;
