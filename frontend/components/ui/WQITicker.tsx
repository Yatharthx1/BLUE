"use client";
import React, { useEffect, useState } from "react";

export const WQITicker = ({ active }: { active: boolean }) => {
  const [score, setScore] = useState(0);
  const target = 78;

  useEffect(() => {
    if (!active) {
      setScore(0);
      return;
    }
    const duration = 2000; // ms
    const steps = 60;
    const interval = duration / steps;
    let current = 0;
    let timer = setInterval(() => {
      current += target / steps;
      if (current >= target) {
        current = target;
        clearInterval(timer);
      }
      setScore(Math.floor(current));
    }, interval);
    return () => clearInterval(timer);
  }, [active]);

  let color = "text-[#00FFD1]"; // var(--glow)
  if (score > 50 && score <= 75) color = "text-yellow-400";
  if (score > 75) color = "text-[var(--warning)]";

  return (
    <div className="flex flex-col items-center justify-center">
      <div className={`font-bebas text-9xl ${color} transition-colors duration-500 font-bold`}>
        {score}
      </div>
      <div className="font-space text-xs tracking-widest text-[var(--muted)] mt-2">
        SAMPLE WQI SCORE
      </div>
    </div>
  );
};
