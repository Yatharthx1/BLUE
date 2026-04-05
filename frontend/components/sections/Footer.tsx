"use client";
import React from 'react';
import { motion } from 'framer-motion';
import { useScrollStore } from '@/lib/scrollStore';

const Footer = () => {
  const progress = useScrollStore((s) => s.progress);
  
  const opacity = progress > 0.98 ? (progress - 0.98) / 0.02 : 0;

  return (
    <motion.div 
      className="fixed inset-x-0 bottom-10 flex flex-col items-center justify-center font-space text-[11px] tracking-widest z-10 pointer-events-auto"
      animate={{ opacity }}
    >
      <div className="text-[var(--text)] mb-2 group cursor-pointer hover:text-[var(--glow)] transition-colors">
        SAMPLE: <span className="text-[var(--glow)]">PURIFIED</span>_
      </div>
      <div className="text-[var(--muted)] text-[9px]">
        BLUE © 2025
      </div>
    </motion.div>
  );
};
export default Footer;
