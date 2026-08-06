import { useEffect, useRef, useState } from "react";

interface ScoreGaugeProps {
  score: number; // 0-100
  size?: number;
  label?: string;
  animate?: boolean;
}

function scoreColor(score: number): string {
  if (score >= 80) return "var(--color-accent)";
  if (score >= 60) return "#eab308";
  return "var(--color-destructive)";
}

export default function ScoreGauge({
  score,
  size = 160,
  label = "ATS Match",
  animate = true,
}: ScoreGaugeProps) {
  const clamped = Math.max(0, Math.min(100, Math.round(score)));
  const [display, setDisplay] = useState(animate ? 0 : clamped);
  const [drawn, setDrawn] = useState(animate ? 0 : clamped);
  const raf = useRef<number | null>(null);

  useEffect(() => {
    if (!animate) {
      setDisplay(clamped);
      setDrawn(clamped);
      return;
    }
    const start = performance.now();
    const duration = 1400;
    const tick = (now: number) => {
      const t = Math.min(1, (now - start) / duration);
      const eased = 1 - Math.pow(1 - t, 3); // ease-out cubic
      setDisplay(Math.round(eased * clamped));
      setDrawn(eased * clamped);
      if (t < 1) raf.current = requestAnimationFrame(tick);
    };
    raf.current = requestAnimationFrame(tick);
    return () => {
      if (raf.current) cancelAnimationFrame(raf.current);
    };
  }, [clamped, animate]);

  const stroke = size / 8;
  const radius = (size - stroke) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference * (1 - drawn / 100);
  const color = scoreColor(clamped);

  return (
    <div className="relative inline-flex flex-col items-center" role="img" aria-label={`${label}: ${clamped} out of 100`}>
      <svg width={size} height={size} className="-rotate-90">
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="var(--color-muted)"
          strokeWidth={stroke}
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth={stroke}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          style={{ transition: "stroke 0.3s ease" }}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="font-heading text-4xl font-extrabold tabular-nums text-foreground">
          {display}
        </span>
        <span className="text-[11px] font-semibold uppercase tracking-wider text-foreground/45">
          {label}
        </span>
      </div>
    </div>
  );
}

/* ───── Small horizontal bar (category scores) ───── */

export function CategoryBar({
  name,
  value,
}: {
  name: string;
  value: number;
}) {
  const clamped = Math.max(0, Math.min(100, Math.round(value)));
  const color = scoreColor(clamped);
  return (
    <div className="flex items-center gap-3">
      <span className="w-24 shrink-0 text-xs font-semibold text-foreground/70">{name}</span>
      <div className="h-2 flex-1 overflow-hidden rounded-full bg-muted">
        <div
          className="h-full rounded-full transition-all duration-700 ease-out"
          style={{ width: `${clamped}%`, backgroundColor: color }}
        />
      </div>
      <span className="w-8 text-right text-xs font-bold tabular-nums text-foreground/70">
        {clamped}
      </span>
    </div>
  );
}