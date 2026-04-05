"use client";
import React from 'react';
import { motion } from 'framer-motion';
import { useScrollStore } from '@/lib/scrollStore';

const HowItWorks = () => {
  const progress = useScrollStore((s) => s.progress);
  
  let opacity = 0;
  if (progress >= 0.62 && progress <= 0.65) opacity = (progress - 0.62) / 0.03;
  else if (progress > 0.65 && progress < 0.73) opacity = 1;
  else if (progress >= 0.73 && progress <= 0.76) opacity = 1 - (progress - 0.73) / 0.03;

  const l1 = progress > 0.66;
  const l2 = progress > 0.68;
  const l3 = progress > 0.70;

  return (
    <motion.div 
      className="fixed inset-0 pointer-events-none z-10 flex items-center justify-end px-24"
      animate={{ opacity }}
    >
      <div className="w-[40%] flex flex-col gap-12">
        <div className="font-space text-[11px] text-[var(--muted)] tracking-widest">03 / THE ENGINE</div>
        
        <div className="flex flex-col gap-6 font-jetbrains text-[20px] text-[var(--text)]">
          <motion.div animate={{ opacity: l1 ? 1 : 0, x: l1 ? 0 : 20 }} className="flex items-center gap-4">
            <span className="text-[var(--glow)]">→</span> ① INPUT RAW PARAMETERS
          </motion.div>
          <motion.div animate={{ opacity: l2 ? 1 : 0, x: l2 ? 0 : 20 }} className="flex items-center gap-4">
            <span className="text-[var(--glow)]">→</span> ② CONTEXT-ORGANIC SCORING
          </motion.div>
          <motion.div animate={{ opacity: l3 ? 1 : 0, x: l3 ? 0 : 20 }} className="flex items-center gap-4">
            <span className="text-[var(--glow)]">→</span> ③ ACTIONABLE INTELLIGENCE
          </motion.div>
        </div>
      </div>
    </motion.div>
  );
};
export default HowItWorks;
