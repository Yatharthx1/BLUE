"use client";
import React, { useRef, useMemo } from "react";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";

const Branch = ({ curvePoints }: { curvePoints: THREE.Vector3[] }) => {
  const curve = useMemo(() => new THREE.CatmullRomCurve3(curvePoints), [curvePoints]);
  return (
    <mesh>
      <tubeGeometry args={[curve, 20, 0.05, 8, false]} />
      <meshStandardMaterial color="#1A0A00" emissive="#FF6B2B" emissiveIntensity={0.2} roughness={0.9} />
    </mesh>
  );
};

const LeakingParticles = () => {
  const count = 50;
  const positions = useMemo(() => {
    const arr = new Float32Array(count * 3);
    for (let i = 0; i < count; i++) {
      arr[i*3] = (Math.random() - 0.5);
      arr[i*3+1] = (Math.random() - 0.5);
      arr[i*3+2] = (Math.random() - 0.5);
    }
    return arr;
  }, []);

  const pointsRef = useRef<THREE.Points>(null);

  useFrame(() => {
    if (pointsRef.current) {
      const pos = pointsRef.current.geometry.attributes.position.array as Float32Array;
      for(let i = 0; i < count; i++) {
        pos[i*3+1] -= 0.005;
        if (pos[i*3+1] < -2) {
          pos[i*3+1] = 1;
          pos[i*3] = (Math.random() - 0.5);
          pos[i*3+2] = (Math.random() - 0.5);
        }
      }
      pointsRef.current.geometry.attributes.position.needsUpdate = true;
    }
  });

  return (
    <points ref={pointsRef}>
      <bufferGeometry>
        <bufferAttribute attach="attributes-position" count={count} array={positions} itemSize={3} args={[positions, 3]} />
      </bufferGeometry>
      <pointsMaterial color="#FF6B2B" size={0.08} transparent opacity={0.6} />
    </points>
  );
};

export default function Organism4Contamination(props: any) {
  const groupRef = useRef<any>(null);

  const branches = useMemo(() => {
    return Array.from({ length: 6 }).map(() => {
      const points = [];
      points.push(new THREE.Vector3(0, 0, 0));
      const endX = (Math.random() - 0.5) * 4;
      const endY = (Math.random() - 0.5) * 4;
      const endZ = (Math.random() - 0.5) * 4;
      points.push(new THREE.Vector3(endX * 0.3, endY * 0.3, endZ * 0.3));
      points.push(new THREE.Vector3(endX * 0.7, endY * 0.7 + (Math.random()-0.5), endZ * 0.7));
      points.push(new THREE.Vector3(endX, endY, endZ));
      return points;
    });
  }, []);

  useFrame(({ clock }) => {
    if (groupRef.current) {
      groupRef.current.rotation.x = Math.sin(clock.elapsedTime * 0.2) * 0.2;
      groupRef.current.position.y = props.position[1] + Math.sin(clock.elapsedTime * 0.35) * 0.15;
    }
  });

  return (
    <group {...props} ref={groupRef}>
      {branches.map((pts, i) => <Branch key={i} curvePoints={pts} />)}
      <LeakingParticles />
    </group>
  );
}
