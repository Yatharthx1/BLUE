"use client";
import React from 'react';
import { motion } from 'framer-motion';
import { useScrollStore } from '@/lib/scrollStore';

const UseCases = () => {
  const progress = useScrollStore((s) => s.progress);
  
  let opacity = 0;
  if (progress >= 0.43 && progress <= 0.46) {
    opacity = (progress - 0.43) / 0.03;
  } else if (progress > 0.46 && progress < 0.55) {
    opacity = 1;
  } else if (progress >= 0.55 && progress <= 0.58) {
    opacity = 1 - (progress - 0.55) / 0.03;
  }

  return (
    <motion.div 
      className="fixed inset-0 pointer-events-none z-10 flex flex-col justify-between py-16 px-24"
      animate={{ opacity }}
    >
      <div className="flex justify-between items-center border-b border-[var(--organism-membrane)] pb-4">
        <div className="font-space text-xs text-[var(--muted)] tracking-widest">02 / SIX CONTEXTS. ONE ENGINE.</div>
        <div className="font-space text-[10px] text-[var(--glow)] tracking-widest opacity-50">INTERACTIVE</div>
      </div>
      
      <div className="flex justify-center border-t border-[var(--organism-membrane)] pt-4">
        <div className="font-space text-xs text-[var(--glow)] tracking-widest flex items-center gap-2">
          HOVER EACH ORGANISM <span className="animate-pulse">_</span>
        </div>
      </div>
    </motion.div>
  );
};
export default UseCases;
