"use client";
import React, { Suspense } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { useScrollStore } from "@/lib/scrollStore";
import { Preload, Stars } from "@react-three/drei";
import PostProcessing from "./PostProcessing";
import Organism1Amoeba from "./Organism1Amoeba";
import Organism2Bacteria from "./Organism2Bacteria";
import Organism3Crystal from "./Organism3Crystal";
import Organism4Contamination from "./Organism4Contamination";
import Organism5CleanCell from "./Organism5CleanCell";

const CameraManager = () => {
  const progress = useScrollStore((s) => s.progress);
  
  useFrame((state) => {
    const lerp = (v0: number, v1: number, t: number) => v0 * (1 - t) + v1 * t;

    let tx = 0, ty = 0, tz = 20;

    if (progress < 0.15) {
      const t = progress / 0.15;
      tx = lerp(0, -4, t); ty = lerp(0, 2, t); tz = lerp(20, 3, t);
    } else if (progress < 0.3) {
      const t = (progress - 0.15) / 0.15;
      tx = lerp(-4, 0, t); ty = lerp(2, 0, t); tz = lerp(3, 15, t);
    } else if (progress < 0.45) {
      const t = (progress - 0.3) / 0.15;
      tx = lerp(0, 3, t); ty = lerp(0, 1, t); tz = lerp(15, 3, t);
    } else if (progress < 0.57) {
      const t = (progress - 0.45) / 0.12;
      tx = lerp(3, 0, t); ty = lerp(1, 0, t); tz = lerp(3, 15, t);
    } else if (progress < 0.65) {
      const t = (progress - 0.57) / 0.08;
      tx = lerp(0, -1, t); ty = lerp(0, -3, t); tz = lerp(15, 3, t);
    } else if (progress < 0.75) {
      const t = (progress - 0.65) / 0.1;
      tx = lerp(-1, 0, t); ty = lerp(-3, 0, t); tz = lerp(3, 15, t);
    } else if (progress < 0.82) {
      const t = (progress - 0.75) / 0.07;
      tx = lerp(0, 4, t); ty = lerp(0, -2, t); tz = lerp(15, 3, t);
    } else if (progress < 0.9) {
      const t = (progress - 0.82) / 0.08;
      tx = lerp(4, 0, t); ty = lerp(-2, 0, t); tz = lerp(3, 15, t);
    } else if (progress < 0.95) {
      const t = (progress - 0.9) / 0.05;
      tx = lerp(0, 0, t); ty = lerp(0, 0, t); tz = lerp(15, 2, t);
    } else {
      const t = (progress - 0.95) / 0.05;
      tx = lerp(0, 0, t); ty = lerp(0, -2, t); tz = lerp(2, 25, t);
    }

    state.camera.position.setX(lerp(state.camera.position.x, tx, 0.05));
    state.camera.position.setY(lerp(state.camera.position.y, ty, 0.05));
    state.camera.position.setZ(lerp(state.camera.position.z, tz, 0.05));
    
    // Look at slightly delayed position to create weight
    state.camera.lookAt(tx * 0.9, ty * 0.9, 0);
  });
  return null;
};

const MicroscopeWorld = () => {
  return (
    <div className="fixed inset-0 z-0 bg-[var(--bg)]">
      <Canvas camera={{ position: [0, 0, 20], fov: 45 }} dpr={[1, 1.5]}>
        <color attach="background" args={["#020408"]} />
        <ambientLight intensity={0.5} />
        <directionalLight position={[10, 10, 5]} intensity={1} color="#00FFD1" />
        <directionalLight position={[-10, -10, 5]} intensity={1} color="#FF6B2B" />
        
        <Suspense fallback={null}>
          <CameraManager />
          
          <group>
            {/* Background Particles drifting */}
            <Stars radius={100} depth={50} count={2000} factor={4} saturation={0} fade speed={1} />
            
            <Organism1Amoeba position={[-4, 2, 0]} />
            <Organism2Bacteria position={[3, 1, 0]} />
            <Organism3Crystal position={[-1, -3, 0]} />
            <Organism4Contamination position={[4, -2, 0]} />
            <Organism5CleanCell position={[0, 0, 0]} />
          </group>

          <PostProcessing />
          <Preload all />
        </Suspense>
      </Canvas>
    </div>
  );
};
export default MicroscopeWorld;
