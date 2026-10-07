"use client";

// Inline SVG sparkline for Mastery(t) — Level 4.1b temporal history.
// No chart dependency; pure SVG polyline. Empty → honest placeholder.

export interface MasteryPoint {
  t: string;
  mastery: number;
  confidence?: number | null;
  reason?: string;
  overall_mastery?: number;
}

function valueOf(p: MasteryPoint): number {
  if (typeof p.overall_mastery === "number") return p.overall_mastery;
  return p.mastery;
}

export function trendBadge(trend: string): string {
  switch (trend) {
    case "STRONGLY_IMPROVING":
      return "bg-emerald-100 text-emerald-800";
    case "IMPROVING":
      return "bg-green-100 text-green-800";
    case "STABLE":
      return "bg-neutral-100 text-neutral-600";
    case "DECLINING":
      return "bg-amber-100 text-amber-800";
    case "STRONGLY_DECLINING":
      return "bg-red-100 text-red-800";
    default:
      return "bg-neutral-100 text-neutral-500";
  }
}

export function TrendBadge({ trend }: { trend: string }) {
  const label = trend.replace(/_/g, " ").toLowerCase();
  return (
    <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${trendBadge(trend)}`}>
      {trend === "UNKNOWN" ? "not enough history" : label}
    </span>
  );
}

export default function MasterySparkline({
  points,
  width = 160,
  height = 36,
}: {
  points: MasteryPoint[];
  width?: number;
  height?: number;
}) {
  if (!points || points.length === 0) {
    return <span className="text-xs text-neutral-400">No history yet</span>;
  }
  if (points.length === 1) {
    return <span className="text-xs text-neutral-400">Not enough history</span>;
  }
  const values = points.map(valueOf);
  const min = Math.min(...values, 0);
  const max = Math.max(...values, 1);
  const span = max - min || 1;
  const stepX = width / Math.max(points.length - 1, 1);
  const coords = points.map((p, i) => {
    const v = valueOf(p);
    const x = Math.round(i * stepX * 10) / 10;
    const y = Math.round((height - 4 - ((v - min) / span) * (height - 8)) * 10) / 10;
    return `${x},${y}`;
  });
  return (
    <svg
      width={width}
      height={height}
      viewBox={`0 0 ${width} ${height}`}
      role="img"
      aria-label={`Mastery history, ${points.length} points`}
      className="overflow-visible"
    >
      <polyline
        points={coords.join(" ")}
        fill="none"
        stroke="currentColor"
        strokeWidth={1.5}
        strokeLinejoin="round"
        strokeLinecap="round"
        className="text-neutral-900"
      />
      {coords.length > 0 && (
        <circle
          cx={Number(coords[coords.length - 1].split(",")[0])}
          cy={Number(coords[coords.length - 1].split(",")[1])}
          r={2.5}
          className="fill-emerald-600"
        />
      )}
    </svg>
  );
}
