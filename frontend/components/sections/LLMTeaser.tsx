"use client";
import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { useScrollStore } from '@/lib/scrollStore';

const Typewriter = ({ text, delay, active }: { text: string, delay: number, active: boolean }) => {
  const [displayed, setDisplayed] = useState("");
  
  useEffect(() => {
    if (!active) {
      setDisplayed("");
      return;
    }
    const to = setTimeout(() => {
      let i = 0;
      const interval = setInterval(() => {
        setDisplayed(text.substring(0, i+1));
        i++;
        if(i >= text.length) clearInterval(interval);
      }, 30);
      return () => clearInterval(interval);
    }, delay);
    return () => clearTimeout(to);
  }, [active, delay, text]);

  return <span>{displayed}</span>;
}

const LLMTeaser = () => {
  const progress = useScrollStore((s) => s.progress);
  
  let opacity = 0;
  let active = false;
  if (progress >= 0.80 && progress <= 0.82) opacity = (progress - 0.80) / 0.02;
  else if (progress > 0.82 && progress < 0.88) { opacity = 1; active = true; }
  else if (progress >= 0.88 && progress <= 0.91) opacity = 1 - (progress - 0.88) / 0.03;

  const msg1 = "my borewell water smells a bit metallic and looks slightly cloudy...";
  const msg2 = "Analyzing... Estimated TDS elevated. Possible iron contamination. WQI score: 61 — marginal for drinking, acceptable for irrigation.";

  return (
    <motion.div 
      className="fixed inset-0 pointer-events-none z-10 flex flex-col items-center justify-center pt-10"
      animate={{ opacity }}
    >
      <div className="w-[480px] flex flex-col gap-4">
        <div className="font-space text-[11px] text-[var(--muted)] tracking-widest text-center mb-6">04 / JUST DESCRIBE IT</div>
        
        <div className="bg-[rgba(10,32,48,0.4)] backdrop-blur-md border border-[var(--organism-membrane)] p-6 rounded-lg flex flex-col gap-6">
          <div className="font-jetbrains text-[14px] text-[var(--text)] opacity-80 leading-relaxed">
            <span className="text-[var(--muted)] mr-2">usr:</span>
            <Typewriter text={msg1} delay={500} active={active} />
            {active && <span className="animate-pulse">_</span>}
          </div>
          
          <div className="font-jetbrains text-[14px] text-[var(--glow)] leading-relaxed">
            <span className="text-[#4A6B7A] mr-2">sys:</span>
            <Typewriter text={msg2} delay={2500} active={active} />
          </div>
        </div>
        
        <div className="font-space text-xs text-[var(--muted)] text-center mt-4">
          {"// no lab required"}
        </div>
      </div>
    </motion.div>
  );
};
export default LLMTeaser;
