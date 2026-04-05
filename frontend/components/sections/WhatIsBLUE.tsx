"use client";
import React from 'react';
import { motion } from 'framer-motion';
import { useScrollStore } from '@/lib/scrollStore';
import { WQITicker } from '../ui/WQITicker';

const WhatIsBLUE = () => {
  const progress = useScrollStore((s) => s.progress);
  
  let opacity = 0;
  let active = false;
  if (progress >= 0.13 && progress <= 0.16) {
    opacity = (progress - 0.13) / 0.03;
  } else if (progress > 0.16 && progress < 0.28) {
    opacity = 1;
    active = true;
  } else if (progress >= 0.28 && progress <= 0.32) {
    opacity = 1 - (progress - 0.28) / 0.04;
  }

  return (
    <motion.div 
      className="fixed inset-0 pointer-events-none z-10 flex items-center justify-between px-24"
      animate={{ opacity }}
    >
      <div className="w-[45%] flex flex-col gap-6">
        <div className="font-space text-[11px] text-[var(--muted)] tracking-[0.2em]">01 / WHAT IS BLUE</div>
        <h2 className="font-bebas text-[72px] leading-[0.9] text-[var(--text)] text-balance">
          WATER HOLDS TRUTH.<br/>WE TRANSLATE IT.
        </h2>
      </div>
      
      <div className="w-[45%] flex justify-center">
        <WQITicker active={active} />
      </div>
    </motion.div>
  );
};
export default WhatIsBLUE;
