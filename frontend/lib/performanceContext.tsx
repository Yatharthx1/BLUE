"use client";

import React, { createContext, useContext, useEffect, useState } from "react";
import { getGPUTier } from "detect-gpu";

type PerformanceTier = 0 | 1 | 2 | 3;

interface PerformanceContextType {
  tier: PerformanceTier;
  loading: boolean;
}

const PerformanceContext = createContext<PerformanceContextType>({ tier: 3, loading: true });

export const usePerformance = () => useContext(PerformanceContext);

export function PerformanceProvider({ children }: { children: React.ReactNode }) {
  const [tier, setTier] = useState<PerformanceTier>(3);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function determinePerformance() {
      try {
        const gpuTier = await getGPUTier();
        if (gpuTier.isMobile) {
          // Force lowest tier on mobile as requested
          setTier(0);
        } else {
          // `gpuTier.tier` is 1, 2, or 3.
          setTier(Math.max(0, Math.min(3, gpuTier.tier)) as PerformanceTier);
        }
      } catch (err) {
        console.warn("Could not determine GPU tier, defaulting to 1", err);
        setTier(1);
      } finally {
        setLoading(false);
      }
    }

    determinePerformance();
  }, []);

  return (
    <PerformanceContext.Provider value={{ tier, loading }}>
      {children}
    </PerformanceContext.Provider>
  );
}
