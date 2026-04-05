"use client";
import React, { useRef, useState } from "react";
import { useFrame } from "@react-three/fiber";
import { Html } from "@react-three/drei";
import { useSpring, animated } from "@react-spring/three";

const labels = [
  "Drinking Water", "Industrial", "Aquaculture",
  "Irrigation", "Wastewater", "Recreational"
];

const Bacterium = ({ position, rotation, label }: any) => {
  const [hovered, setHover] = useState(false);
  const meshRef = useRef<any>(null);

  const { scale } = useSpring({
    scale: hovered ? 1.3 : 1,
    config: { mass: 1, tension: 280, friction: 60 }
  });

  useFrame(() => {
    if (meshRef.current) {
      meshRef.current.rotation.y += 0.005;
    }
  });

  return (
    <animated.mesh
      ref={meshRef}
      position={position}
      rotation={rotation}
      scale={scale}
      onPointerOver={(e) => { e.stopPropagation(); setHover(true); }}
      onPointerOut={() => setHover(false)}
    >
      <capsuleGeometry args={[0.2, 0.8, 16, 16]} />
      <meshStandardMaterial 
        color={hovered ? "#00FFD1" : "#4A6B7A"} 
        emissive={hovered ? "#00FFD1" : "#0A2030"}
        emissiveIntensity={hovered ? 0.8 : 0.2}
      />
      
      <Html distanceFactor={10} position={[0, 1.2, 0]} center>
        <div 
          className="font-space text-[10px] whitespace-nowrap pointer-events-none transition-opacity duration-300"
          style={{
            color: hovered ? "#00FFD1" : "#4A6B7A",
            opacity: hovered ? 1 : 0.5,
            textShadow: hovered ? "0 0 8px rgba(0,255,209,0.5)" : "none"
          }}
        >
          {label}
        </div>
      </Html>
    </animated.mesh>
  );
};

export default function Organism2Bacteria(props: any) {
  const groupRef = useRef<any>(null);

  useFrame(({ clock }) => {
    if (groupRef.current) {
      groupRef.current.position.y = props.position[1] + Math.sin(clock.elapsedTime * 0.4) * 0.15;
    }
  });

  const positions = [
    [-1, 0, 0], [1, 0.5, 0], [0, -1, 0.5],
    [-0.5, 1, -0.5], [0.8, -0.8, -0.2], [0, 0, -1]
  ];

  return (
    <group {...props} ref={groupRef}>
      {labels.map((lbl, i) => (
        <Bacterium
          key={lbl}
          label={lbl}
          position={positions[i]}
          rotation={[Math.random(), Math.random(), Math.random()]}
        />
      ))}
    </group>
  );
}
