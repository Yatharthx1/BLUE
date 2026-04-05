"use client";
import React, { useRef } from "react";
import { EffectComposer, Bloom, ChromaticAberration, Vignette } from "@react-three/postprocessing";
import { useScrollStore } from "@/lib/scrollStore";
import { usePerformance } from "@/lib/performanceContext";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";

const PostProcessing = () => {
  const { tier, loading } = usePerformance();
  const progress = useScrollStore((s) => s.progress);
  const chromRef = useRef<any>(null);

  useFrame(() => {
    if (!chromRef.current) return;
    const isTransitioning = [0.15, 0.3, 0.45, 0.57, 0.65, 0.75, 0.82, 0.9, 0.95].some(
      (pt) => Math.abs(progress - pt) < 0.03
    );

    const targetOffset = isTransitioning ? 0.015 : 0.002;
    const curOffset = chromRef.current.offset.x;
    const newOffset = curOffset + (targetOffset - curOffset) * 0.1;
    
    chromRef.current.offset.set(newOffset, newOffset);
  });

  if (loading || tier < 2) return null;

  return (
    <EffectComposer multisampling={0}>
      <Bloom luminanceThreshold={0.3} luminanceSmoothing={0.9} height={300} intensity={0.4} />
      <ChromaticAberration 
        ref={chromRef} 
        offset={new THREE.Vector2(0.002, 0.002)}
        radialModulation={false}
        modulationOffset={0}
      />
      <Vignette eskil={false} offset={0.3} darkness={0.5} />
    </EffectComposer>
  );
};
export default PostProcessing;
