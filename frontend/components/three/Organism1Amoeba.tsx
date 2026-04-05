"use client";
import React, { useRef, useMemo } from "react";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";

const amoebaVertexShader = `
uniform float uTime;
varying vec3 vNormal;
varying vec3 vPosition;

void main() {
  vNormal = normal;
  vec3 p = position;
  
  float displacement = sin(p.x * 2.0 + uTime) * 0.1 
                     + cos(p.y * 2.5 + uTime * 1.2) * 0.1
                     + sin(p.z * 1.5 + uTime * 0.8) * 0.1;
  p += normal * displacement;
  vPosition = p;
  
  gl_Position = projectionMatrix * modelViewMatrix * vec4(p, 1.0);
}
`;

const amoebaFragmentShader = `
uniform float uTime;
varying vec3 vNormal;
varying vec3 vPosition;

void main() {
  vec3 baseColor = vec3(0.039, 0.188, 0.251); 
  vec3 glowColor = vec3(0.0, 1.0, 0.82); 
  
  vec3 viewDirection = normalize(cameraPosition - vPosition);
  float fresnel = dot(viewDirection, vNormal);
  fresnel = clamp(1.0 - fresnel, 0.0, 1.0);
  fresnel = pow(fresnel, 2.0); 
  
  vec3 finalColor = mix(baseColor, glowColor, fresnel * 0.8);
  
  gl_FragColor = vec4(finalColor, 0.6 + fresnel * 0.4);
}
`;

export default function Organism1Amoeba(props: any) {
  const meshRef = useRef<THREE.Mesh>(null);
  
  const uniforms = useMemo(() => ({
    uTime: { value: 0 }
  }), []);

  useFrame((state) => {
    if (meshRef.current) {
      meshRef.current.rotation.y += 0.002;
      meshRef.current.rotation.x += 0.001;
      (meshRef.current.material as THREE.ShaderMaterial).uniforms.uTime.value = state.clock.elapsedTime;
      meshRef.current.position.y = props.position[1] + Math.sin(state.clock.elapsedTime * 0.5) * 0.2;
    }
  });

  return (
    <group {...props}>
      <mesh ref={meshRef}>
        <sphereGeometry args={[1.5, 64, 64]} />
        <shaderMaterial
          vertexShader={amoebaVertexShader}
          fragmentShader={amoebaFragmentShader}
          uniforms={uniforms}
          transparent={true}
          side={THREE.DoubleSide}
        />
      </mesh>
    </group>
  );
}
