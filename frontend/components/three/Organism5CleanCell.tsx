"use client";
import React, { useRef, useMemo } from "react";
import { useFrame } from "@react-three/fiber";
import { Html } from "@react-three/drei";
import { useScrollStore } from "@/lib/scrollStore";
import * as THREE from "three";
import { useRouter } from "next/navigation";

const cellVertexShader = `
varying vec3 vNormal;
varying vec3 vPosition;
void main() {
  vNormal = normalize(normalMatrix * normal);
  vPosition = (modelViewMatrix * vec4(position, 1.0)).xyz;
  gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
}
`;

const cellFragmentShader = `
varying vec3 vNormal;
varying vec3 vPosition;
void main() {
  vec3 viewDirection = normalize(-vPosition);
  float fresnel = dot(viewDirection, vNormal);
  fresnel = clamp(1.0 - fresnel, 0.0, 1.0);
  fresnel = pow(fresnel, 3.0);
  
  vec3 cyan = vec3(0.0, 1.0, 0.82);
  vec3 finalColor = cyan * (0.3 + fresnel * 0.7);
  gl_FragColor = vec4(finalColor, 0.2 + fresnel * 0.6);
}
`;

export default function Organism5CleanCell(props: any) {
  const groupRef = useRef<any>(null);
  const leftHalf = useRef<any>(null);
  const rightHalf = useRef<any>(null);
  const progress = useScrollStore((s) => s.progress);
  const router = useRouter();

  const uniforms = useMemo(() => ({}), []);

  useFrame(({ clock }) => {
    if (!groupRef.current) return;
    
    const pulse = 1.0 + Math.sin(clock.elapsedTime * 2.0) * 0.025;
    groupRef.current.scale.setScalar(pulse);
    groupRef.current.position.y = props.position[1] + Math.sin(clock.elapsedTime * 0.5) * 0.1;

    let split = 0;
    if (progress > 0.93) {
      split = Math.min((progress - 0.93) / 0.05, 1.0);
      split = Math.pow(split, 2.0); 
    }

    if (leftHalf.current && rightHalf.current) {
      leftHalf.current.position.z = split * 1.5;
      rightHalf.current.position.z = -split * 1.5;
    }
  });

  return (
    <group {...props} ref={groupRef}>
      <mesh ref={leftHalf} rotation={[0, 0, 0]}>
        <sphereGeometry args={[1.5, 32, 32, 0, Math.PI]} />
        <shaderMaterial
          vertexShader={cellVertexShader}
          fragmentShader={cellFragmentShader}
          uniforms={uniforms}
          transparent
          side={THREE.DoubleSide}
          depthWrite={false}
        />
      </mesh>
      
      <mesh ref={rightHalf} rotation={[0, Math.PI, 0]}>
        <sphereGeometry args={[1.5, 32, 32, 0, Math.PI]} />
        <shaderMaterial
          vertexShader={cellVertexShader}
          fragmentShader={cellFragmentShader}
          uniforms={uniforms}
          transparent
          side={THREE.DoubleSide}
          depthWrite={false}
        />
      </mesh>

      <Html center position={[0,0,0]} distanceFactor={10} zIndexRange={[100, 0]}>
        <div 
          className="flex flex-col items-center justify-center transition-opacity duration-500"
          style={{ opacity: progress > 0.94 ? 1 : 0, pointerEvents: progress > 0.94 ? 'auto' : 'none' }}
        >
          <button 
            onClick={() => {
              const rip = document.createElement("div");
              rip.className = "fixed inset-0 z-[100] bg-[var(--glow)] blur-3xl rounded-full scale-0 animate-[ping_1s_ease-out_forwards]";
              document.body.appendChild(rip);
              setTimeout(() => {
                router.push("/dashboard");
              }, 800);
            }}
            className="font-bebas text-[28px] text-[var(--glow)] border border-[var(--glow)] px-8 py-4 rounded-none hover:bg-[var(--glow)] hover:text-[var(--bg)] transition-colors tracking-wider whitespace-nowrap"
          >
            ANALYZE YOUR WATER
          </button>
        </div>
      </Html>
    </group>
  );
}
