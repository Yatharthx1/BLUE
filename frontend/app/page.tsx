"use client";
import React, { useEffect, useRef } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { useScrollStore } from "@/lib/scrollStore";
import dynamic from 'next/dynamic';
const MicroscopeWorld = dynamic(() => import("@/components/three/MicroscopeWorld"), { ssr: false });
import Reticle from "@/components/ui/Reticle";
import MicroscopeFrame from "@/components/ui/MicroscopeFrame";
import EntryLabel from "@/components/sections/EntryLabel";
import WhatIsBLUE from "@/components/sections/WhatIsBLUE";
import UseCases from "@/components/sections/UseCases";
import HowItWorks from "@/components/sections/HowItWorks";
import LLMTeaser from "@/components/sections/LLMTeaser";
import Footer from "@/components/sections/Footer";

// We need to register GSAP plugins before use
if (typeof window !== "undefined") {
  gsap.registerPlugin(ScrollTrigger);
}

export default function Home() {
  const scrollRef = useRef<HTMLDivElement>(null);
  const setProgress = useScrollStore((s) => s.setProgress);

  useEffect(() => {
    if (!scrollRef.current) return;

    const ctx = gsap.context(() => {
      ScrollTrigger.create({
        scroller: scrollRef.current,
        trigger: scrollRef.current?.firstElementChild,
        start: "top top",
        end: "bottom bottom",
        onUpdate: (self) => {
          setProgress(self.progress);
        },
      });
    }, scrollRef);

    return () => ctx.revert();
  }, [setProgress]);

  return (
    <main 
      ref={scrollRef} 
      className="relative w-full h-screen overflow-y-auto overflow-x-hidden bg-[var(--bg)]"
    >
      {/* The invisible height that forces scrolling */}
      <div className="w-full h-[750vh]" />

      {/* 3D Background */}
      <MicroscopeWorld />

      {/* Global UI */}
      <MicroscopeFrame />
      <Reticle />

      {/* Sections Overlays */}
      <EntryLabel />
      <WhatIsBLUE />
      <UseCases />
      <HowItWorks />
      <LLMTeaser />
      <Footer />
    </main>
  );
}
