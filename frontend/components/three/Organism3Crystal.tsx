"use client";
import React, { useRef, useMemo } from "react";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";
import { useScrollStore } from "@/lib/scrollStore";

export default function Organism3Crystal(props: any) {
  const groupRef = useRef<any>(null);
  const solidRef = useRef<any>(null);
  const progress = useScrollStore((s) => s.progress);
  
  const geometry = useMemo(() => {
    const geo = new THREE.IcosahedronGeometry(1.2, 0);
    return geo.toNonIndexed();
  }, []);

  useFrame(({ clock }) => {
    if (groupRef.current) {
      groupRef.current.rotation.y += 0.001;
      groupRef.current.rotation.z += 0.0005;
      groupRef.current.position.y = props.position[1] + Math.sin(clock.elapsedTime * 0.3) * 0.2;
    }

    if (solidRef.current) {
      const colors = [];
      const positionAttribute = geometry.attributes.position;
      
      let localProg = 0;
      if (progress >= 0.65 && progress <= 0.75) {
        localProg = (progress - 0.65) / 0.1;
      } else if (progress > 0.75) {
        localProg = 1;
      }
      
      const c1 = new THREE.Color("#00FFD1");
      const c2 = new THREE.Color("#4A9FFF");
      const c3 = new THREE.Color("#FF6B2B");
      const base = new THREE.Color("#0A2030");

      for (let i = 0; i < positionAttribute.count; i += 3) {
        let faceColor = base;
        if (i === 0 && localProg > 0.1) faceColor = c1;
        if (i === 12 && localProg > 0.4) faceColor = c2;
        if (i === 24 && localProg > 0.7) faceColor = c3;

        colors.push(faceColor.r, faceColor.g, faceColor.b);
        colors.push(faceColor.r, faceColor.g, faceColor.b);
        colors.push(faceColor.r, faceColor.g, faceColor.b);
      }
      geometry.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));
    }
  });

  return (
    <group {...props} ref={groupRef}>
      <mesh ref={solidRef} geometry={geometry}>
        <meshStandardMaterial vertexColors transparent opacity={0.8} />
      </mesh>
      <mesh geometry={geometry}>
        <meshBasicMaterial color="#00FFD1" wireframe transparent opacity={0.3} />
      </mesh>
    </group>
  );
}
