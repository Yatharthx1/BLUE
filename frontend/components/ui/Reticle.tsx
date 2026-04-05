"use client";
import React, { useEffect, useState } from "react";
import { useScrollStore } from "@/lib/scrollStore";

const Reticle = () => {
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 });
  const [activePos, setActivePos] = useState({ x: 0, y: 0 });
  const progress = useScrollStore((s) => s.progress);

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      setMousePos({ x: e.clientX, y: e.clientY });
    };
    window.addEventListener("mousemove", handleMouseMove);
    return () => window.removeEventListener("mousemove", handleMouseMove);
  }, []);

  useEffect(() => {
    // Smooth lerp on requestAnimationFrame
    let animationFrameId: number;
    const lerp = (start: number, end: number, factor: number) => start + (end - start) * factor;

    const updatePosition = () => {
      setActivePos((prev) => {
        // Only apply lerp if point is far enough
        const nx = lerp(prev.x, mousePos.x, 0.15);
        const ny = lerp(prev.y, mousePos.y, 0.15);
        return { x: nx, y: ny };
      });
      animationFrameId = requestAnimationFrame(updatePosition);
    };
    updatePosition();
    return () => cancelAnimationFrame(animationFrameId);
  }, [mousePos]);

  // Opacity spikes during zoom transitions. Zoom transition points approx:
  // 15, 30, 45, 57, 65, 75, 82, 90, 95
  const isTransitioning = [0.15, 0.3, 0.45, 0.57, 0.65, 0.75, 0.82, 0.9, 0.95].some(
    (pt) => Math.abs(progress - pt) < 0.02
  );

  return (
    <div
      className="fixed inset-0 pointer-events-none z-50 overflow-hidden mix-blend-screen"
    >
      <div 
        className="absolute transition-opacity duration-200"
        style={{ 
          transform: `translate(${activePos.x}px, ${activePos.y}px) translate(-50%, -50%)`,
          opacity: isTransitioning ? 0.8 : 0.3
        }}
      >
        <svg width="60" height="60" viewBox="0 0 60 60" fill="none" xmlns="http://www.w3.org/2000/svg">
          <circle cx="30" cy="30" r="28" stroke="var(--glow)" strokeWidth="1" strokeDasharray="4 4" opacity="0.5"/>
          <line x1="30" y1="0" x2="30" y2="15" stroke="var(--glow)" strokeWidth="1"/>
          <line x1="30" y1="45" x2="30" y2="60" stroke="var(--glow)" strokeWidth="1"/>
          <line x1="0" y1="30" x2="15" y2="30" stroke="var(--glow)" strokeWidth="1"/>
          <line x1="45" y1="30" x2="60" y2="30" stroke="var(--glow)" strokeWidth="1"/>
          <circle cx="30" cy="30" r="2" fill="var(--glow)"/>
        </svg>
      </div>
    </div>
  );
};
export default Reticle;
