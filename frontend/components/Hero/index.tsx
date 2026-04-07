"use client";

import React, { useRef, useEffect, useState, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";

// ─── CONSTANTS ──────────────────────────────────────────────
const DIRTY_COLORS = [
  [61, 43, 31],   // #3D2B1F
  [92, 61, 46],   // #5C3D2E
  [139, 99, 71],  // #8B6347
];

const CLEAN_COLORS = [
  [14, 165, 233],  // #0EA5E9
  [34, 211, 238],  // #22D3EE
  [186, 230, 253], // #BAE6FD
];

const PHASE1_DURATION = 2000;   // ms before sweep starts
const SWEEP_DURATION = 3000;    // ms for the sweep
const FADE_DURATION = 800;      // ms for canvas fade to navy

// ─── EASING ─────────────────────────────────────────────────
function easeInOutCubic(t: number): number {
  return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
}

// ─── PARTICLE CLASS ─────────────────────────────────────────
interface Particle {
  x: number;
  y: number;
  r: number;
  vx: number;
  vy: number;
  opacity: number;
  type: "dirty" | "clean";
}

function createParticles(
  count: number,
  w: number,
  h: number,
  type: "dirty" | "clean"
): Particle[] {
  const particles: Particle[] = [];
  for (let i = 0; i < count; i++) {
    particles.push({
      x: type === "dirty" ? Math.random() * (w / 2) : w / 2 + Math.random() * (w / 2),
      y: Math.random() * h,
      r: Math.random() * 2.5 + 0.5,
      vx: (Math.random() - 0.5) * 0.4,
      vy: (Math.random() - 0.5) * 0.3,
      opacity: Math.random() * 0.6 + 0.2,
      type,
    });
  }
  return particles;
}

// ─── FLUID HELPERS ──────────────────────────────────────────
function fluidOffset(x: number, y: number, t: number, scale: number): number {
  return (
    Math.sin(x * 0.003 * scale + t * 0.8) * 12 +
    Math.sin(y * 0.005 * scale + t * 1.1) * 8 +
    Math.sin((x + y) * 0.002 * scale + t * 0.6) * 6
  );
}

function turbulence(x: number, y: number, t: number): number {
  return (
    Math.sin(x * 0.008 + t * 1.3) * 0.3 +
    Math.sin(y * 0.006 + t * 0.9) * 0.25 +
    Math.sin((x * 0.004 + y * 0.003) + t * 1.7) * 0.2
  );
}

// ─── DRAW WATER COLUMN ─────────────────────────────────────
function drawWaterRegion(
  ctx: CanvasRenderingContext2D,
  startX: number,
  endX: number,
  h: number,
  t: number,
  colors: number[][],
  isDirty: boolean
) {
  const bandCount = 7;
  const bandH = h / bandCount;

  for (let band = 0; band < bandCount; band++) {
    const y0 = band * bandH;
    const colorIdx = band % colors.length;
    const [r, g, b] = colors[colorIdx];

    // Shift color slightly with sine for variation
    const shift = Math.sin(band * 0.9 + t * 0.5) * 12;
    const fr = Math.max(0, Math.min(255, r + shift));
    const fg = Math.max(0, Math.min(255, g + shift * (isDirty ? 0.6 : 1.2)));
    const fb = Math.max(0, Math.min(255, b + shift * (isDirty ? 0.3 : 1.5)));

    ctx.fillStyle = `rgb(${fr}, ${fg}, ${fb})`;
    ctx.fillRect(startX, y0, endX - startX, bandH + 2);
  }

  // Overlay sine-wave distortion layers
  const layerCount = isDirty ? 5 : 4;
  for (let layer = 0; layer < layerCount; layer++) {
    const baseAlpha = isDirty ? 0.07 : 0.05;
    const alpha = baseAlpha + Math.sin(layer + t) * 0.02;
    const colPick = colors[layer % colors.length];

    ctx.save();
    ctx.globalAlpha = Math.max(0, Math.min(1, alpha));
    ctx.fillStyle = `rgb(${colPick[0]}, ${colPick[1]}, ${colPick[2]})`;

    const step = 4;
    for (let x = startX; x < endX; x += step) {
      const offset = fluidOffset(x, 0, t + layer * 1.3, isDirty ? 1.4 : 1.0);
      const waveH = 30 + Math.sin(layer * 2 + t * 0.7) * 10;
      for (let y = 0; y < h; y += step) {
        const dy = fluidOffset(x, y, t + layer * 0.7, isDirty ? 1.6 : 0.8);
        const localAlpha = 0.5 + turbulence(x, y + offset, t + layer) * 0.5;
        ctx.globalAlpha = Math.max(0, Math.min(1, alpha * localAlpha));
        ctx.fillRect(x, y + dy * 0.3, step, step);
      }
    }
    ctx.restore();
  }

  // Caustics on clean side
  if (!isDirty) {
    ctx.save();
    for (let i = 0; i < 6; i++) {
      const cx = startX + ((endX - startX) * 0.5) + Math.sin(t * 0.6 + i * 1.8) * (endX - startX) * 0.35;
      const cy = h * 0.5 + Math.cos(t * 0.5 + i * 2.1) * h * 0.35;
      const radius = 40 + Math.sin(t * 0.8 + i) * 20;

      const grad = ctx.createRadialGradient(cx, cy, 0, cx, cy, radius);
      grad.addColorStop(0, "rgba(186, 230, 253, 0.12)");
      grad.addColorStop(0.5, "rgba(34, 211, 238, 0.05)");
      grad.addColorStop(1, "rgba(14, 165, 233, 0)");
      ctx.fillStyle = grad;
      ctx.fillRect(startX, 0, endX - startX, h);
    }
    ctx.restore();
  }
}

// ─── DRAW PARTICLES ─────────────────────────────────────────
function drawParticles(
  ctx: CanvasRenderingContext2D,
  particles: Particle[],
  w: number,
  h: number,
  sweepX: number,
  phase: number
) {
  particles.forEach((p) => {
    p.x += p.vx;
    p.y += p.vy;

    // Wrap around
    if (p.type === "dirty") {
      if (p.x < 0) p.x = sweepX > 0 ? Math.min(w / 2, sweepX) : w / 2;
      if (p.x > (sweepX > 0 ? sweepX : w / 2)) p.x = 0;
    } else {
      const leftBound = phase >= 2 ? 0 : sweepX > 0 ? sweepX : w / 2;
      if (p.x < leftBound) p.x = w;
      if (p.x > w) p.x = leftBound;
    }
    if (p.y < 0) p.y = h;
    if (p.y > h) p.y = 0;

    // During phase 2+ hide dirty particles that have been swept
    if (phase >= 1 && p.type === "dirty" && p.x > sweepX) return;

    ctx.beginPath();
    ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);

    if (p.type === "dirty") {
      ctx.fillStyle = `rgba(30, 20, 10, ${p.opacity * 0.7})`;
    } else {
      // Shimmer effect
      const shimmer = 0.5 + Math.sin(Date.now() * 0.003 + p.x * 0.01) * 0.5;
      ctx.fillStyle = `rgba(186, 230, 253, ${p.opacity * 0.5 * shimmer})`;
    }
    ctx.fill();
  });
}

// ─── DRAW SWEEP GLOW LINE ──────────────────────────────────
function drawSweepLine(
  ctx: CanvasRenderingContext2D,
  x: number,
  h: number,
  alpha: number
) {
  if (alpha <= 0) return;

  // Outer glow
  const glowWidth = 80;
  const outerGrad = ctx.createLinearGradient(x - glowWidth, 0, x + glowWidth, 0);
  outerGrad.addColorStop(0, `rgba(14, 165, 233, 0)`);
  outerGrad.addColorStop(0.3, `rgba(34, 211, 238, ${0.08 * alpha})`);
  outerGrad.addColorStop(0.5, `rgba(255, 255, 255, ${0.35 * alpha})`);
  outerGrad.addColorStop(0.7, `rgba(34, 211, 238, ${0.08 * alpha})`);
  outerGrad.addColorStop(1, `rgba(14, 165, 233, 0)`);
  ctx.fillStyle = outerGrad;
  ctx.fillRect(x - glowWidth, 0, glowWidth * 2, h);

  // Core bright line
  ctx.save();
  ctx.shadowColor = "rgba(186, 230, 253, 0.9)";
  ctx.shadowBlur = 25;
  ctx.strokeStyle = `rgba(255, 255, 255, ${0.9 * alpha})`;
  ctx.lineWidth = 2.5;
  ctx.beginPath();
  ctx.moveTo(x, 0);
  ctx.lineTo(x, h);
  ctx.stroke();
  ctx.restore();
}

// ─── DRAW CAUSTIC BACKGROUND (Phase 3) ─────────────────────
function drawNavyCaustics(
  ctx: CanvasRenderingContext2D,
  w: number,
  h: number,
  t: number
) {
  // Deep navy base
  ctx.fillStyle = "#020617";
  ctx.fillRect(0, 0, w, h);

  // Central radial glow
  const centerGrad = ctx.createRadialGradient(w / 2, h / 2, 0, w / 2, h / 2, Math.max(w, h) * 0.5);
  centerGrad.addColorStop(0, "rgba(14, 165, 233, 0.08)");
  centerGrad.addColorStop(0.4, "rgba(14, 165, 233, 0.03)");
  centerGrad.addColorStop(1, "rgba(2, 6, 23, 0)");
  ctx.fillStyle = centerGrad;
  ctx.fillRect(0, 0, w, h);

  // Subtle caustic patches
  for (let i = 0; i < 8; i++) {
    const cx = w * (0.2 + 0.6 * ((Math.sin(t * 0.3 + i * 1.5) + 1) / 2));
    const cy = h * (0.2 + 0.6 * ((Math.cos(t * 0.25 + i * 2.0) + 1) / 2));
    const radius = 60 + Math.sin(t * 0.4 + i * 0.8) * 30;

    const grad = ctx.createRadialGradient(cx, cy, 0, cx, cy, radius);
    grad.addColorStop(0, `rgba(14, 165, 233, ${0.04 + Math.sin(t + i) * 0.02})`);
    grad.addColorStop(0.6, `rgba(34, 211, 238, ${0.02})`);
    grad.addColorStop(1, "rgba(2, 6, 23, 0)");
    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, w, h);
  }
}

// ─── MAIN HERO COMPONENT ───────────────────────────────────
export default function Hero() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animRef = useRef<number>(0);
  const startTimeRef = useRef<number>(0);
  const particlesRef = useRef<Particle[]>([]);
  const [phase, setPhase] = useState<0 | 1 | 2 | 3>(0);
  // 0 = contrast, 1 = sweeping, 2 = fade to navy, 3 = text entry

  const initParticles = useCallback((w: number, h: number) => {
    particlesRef.current = [
      ...createParticles(60, w, h, "dirty"),
      ...createParticles(50, w, h, "clean"),
    ];
  }, []);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    let w = window.innerWidth;
    let h = window.innerHeight;

    const resize = () => {
      w = window.innerWidth;
      h = window.innerHeight;
      canvas.width = w;
      canvas.height = h;
      // Reinitialize particles on resize
      initParticles(w, h);
    };

    resize();
    window.addEventListener("resize", resize);

    startTimeRef.current = performance.now();
    let sweepProgress = 0;
    let fadeAlpha = 0;
    let phaseLocal = 0;

    const animate = (now: number) => {
      const elapsed = now - startTimeRef.current;
      const t = now * 0.001; // seconds for sine waves

      ctx.clearRect(0, 0, w, h);

      // ── PHASE 0: Contrast ──
      if (phaseLocal === 0) {
        const midX = w / 2;
        drawWaterRegion(ctx, 0, midX, h, t, DIRTY_COLORS, true);
        drawWaterRegion(ctx, midX, w, h, t, CLEAN_COLORS, false);

        // Dividing line
        ctx.save();
        ctx.strokeStyle = "rgba(255, 255, 255, 0.3)";
        ctx.lineWidth = 1.5;
        ctx.beginPath();
        ctx.moveTo(midX, 0);
        ctx.lineTo(midX, h);
        ctx.stroke();
        ctx.restore();

        drawParticles(ctx, particlesRef.current, w, h, midX, 0);

        if (elapsed >= PHASE1_DURATION) {
          phaseLocal = 1;
          setPhase(1);
        }
      }

      // ── PHASE 1: Sweep ──
      else if (phaseLocal === 1) {
        const sweepElapsed = elapsed - PHASE1_DURATION;
        const rawProgress = Math.min(1, sweepElapsed / SWEEP_DURATION);
        sweepProgress = easeInOutCubic(rawProgress);
        const sweepX = sweepProgress * w;

        // Draw dirty water on left of sweep
        if (sweepX > 0) {
          drawWaterRegion(ctx, 0, sweepX, h, t, CLEAN_COLORS, false);
        }

        // Draw clean water from sweep to right
        if (sweepX < w) {
          ctx.save();
          ctx.beginPath();
          ctx.rect(sweepX, 0, w - sweepX, h);
          ctx.clip();
          // Still show dirty on the right side that hasn't been swept
          const dirtyStart = sweepX;
          // Blend: left of midpoint was dirty, right of midpoint was clean
          if (sweepX < w / 2) {
            drawWaterRegion(ctx, sweepX, w / 2, h, t, DIRTY_COLORS, true);
            drawWaterRegion(ctx, w / 2, w, h, t, CLEAN_COLORS, false);
          } else {
            drawWaterRegion(ctx, sweepX, w, h, t, CLEAN_COLORS, false);
          }
          ctx.restore();
        }

        drawParticles(ctx, particlesRef.current, w, h, sweepX, 1);
        drawSweepLine(ctx, sweepX, h, 1);

        if (rawProgress >= 1) {
          phaseLocal = 2;
          setPhase(2);
        }
      }

      // ── PHASE 2: Fade to navy ──
      else if (phaseLocal === 2) {
        const fadeElapsed = elapsed - PHASE1_DURATION - SWEEP_DURATION;
        fadeAlpha = Math.min(1, fadeElapsed / FADE_DURATION);

        // Still show clean water underneath
        drawWaterRegion(ctx, 0, w, h, t, CLEAN_COLORS, false);
        drawParticles(ctx, particlesRef.current, w, h, 0, 2);

        // Overlay navy fade
        ctx.save();
        ctx.globalAlpha = fadeAlpha;
        drawNavyCaustics(ctx, w, h, t);
        ctx.restore();

        if (fadeAlpha >= 1) {
          phaseLocal = 3;
          setPhase(3);
        }
      }

      // ── PHASE 3: Navy caustics loop ──
      else {
        drawNavyCaustics(ctx, w, h, t);
      }

      animRef.current = requestAnimationFrame(animate);
    };

    animRef.current = requestAnimationFrame(animate);

    return () => {
      window.removeEventListener("resize", resize);
      cancelAnimationFrame(animRef.current);
    };
  }, [initParticles]);

  return (
    <section
      id="hero"
      style={{
        position: "relative",
        width: "100vw",
        height: "100vh",
        overflow: "hidden",
        background: "#020617",
      }}
    >
      {/* Canvas Background */}
      <canvas
        ref={canvasRef}
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          width: "100%",
          height: "100%",
          display: "block",
        }}
      />

      {/* Hero Content — appears in Phase 3 */}
      <AnimatePresence>
        {phase === 3 && (
          <div
            style={{
              position: "absolute",
              inset: 0,
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "center",
              zIndex: 10,
              padding: "0 1.5rem",
              textAlign: "center",
            }}
          >
            {/* BLUE Title */}
            <motion.h1
              initial={{ y: 120, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ duration: 0.8, ease: "easeOut" }}
              style={{
                fontSize: "clamp(80px, 12vw, 160px)",
                fontWeight: 900,
                color: "#0EA5E9",
                letterSpacing: "0.04em",
                lineHeight: 1,
                margin: 0,
                textShadow:
                  "0 0 20px rgba(14,165,233,0.6), 0 0 60px rgba(14,165,233,0.3), 0 0 120px rgba(14,165,233,0.15)",
                fontFamily: "var(--font-bebas), 'Inter', sans-serif",
              }}
            >
              BLUE
            </motion.h1>

            {/* Subheadline */}
            <motion.p
              initial={{ y: 40, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ duration: 0.7, ease: "easeOut", delay: 0.3 }}
              style={{
                fontSize: "clamp(18px, 2.5vw, 32px)",
                fontWeight: 600,
                color: "#FFFFFF",
                marginTop: "clamp(12px, 2vw, 24px)",
                letterSpacing: "0.02em",
                fontFamily: "'Inter', sans-serif",
              }}
            >
              Water Intelligence. Redefined.
            </motion.p>

            {/* One-liner */}
            <motion.p
              initial={{ y: 30, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ duration: 0.7, ease: "easeOut", delay: 0.6 }}
              style={{
                fontSize: "clamp(14px, 1.8vw, 20px)",
                fontWeight: 400,
                color: "rgba(255, 255, 255, 0.6)",
                marginTop: "clamp(8px, 1.2vw, 16px)",
                maxWidth: "600px",
                fontFamily: "'Inter', sans-serif",
              }}
            >
              Know what&apos;s in your water — before it&apos;s too late.
            </motion.p>

            {/* CTA Button */}
            <motion.button
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ duration: 0.7, ease: "easeOut", delay: 0.9 }}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.97 }}
              style={{
                marginTop: "clamp(24px, 3vw, 48px)",
                padding: "14px 40px",
                fontSize: "clamp(14px, 1.4vw, 18px)",
                fontWeight: 600,
                color: "#0EA5E9",
                background: "transparent",
                border: "2px solid #0EA5E9",
                borderRadius: "9999px",
                cursor: "pointer",
                letterSpacing: "0.06em",
                transition: "all 0.3s ease",
                boxShadow: "0 0 20px rgba(14,165,233,0.2), inset 0 0 20px rgba(14,165,233,0.05)",
                fontFamily: "'Inter', sans-serif",
              }}
              onMouseEnter={(e) => {
                const el = e.currentTarget;
                el.style.background = "rgba(14, 165, 233, 0.15)";
                el.style.boxShadow =
                  "0 0 30px rgba(14,165,233,0.4), inset 0 0 30px rgba(14,165,233,0.1)";
                el.style.color = "#FFFFFF";
              }}
              onMouseLeave={(e) => {
                const el = e.currentTarget;
                el.style.background = "transparent";
                el.style.boxShadow =
                  "0 0 20px rgba(14,165,233,0.2), inset 0 0 20px rgba(14,165,233,0.05)";
                el.style.color = "#0EA5E9";
              }}
            >
              Try BLUE
            </motion.button>
          </div>
        )}
      </AnimatePresence>
    </section>
  );
}
