import { cn } from "@/lib/utils";

interface Props {
  score: number;
  size?: number;
}

export const RadialGauge = ({ score, size = 180 }: Props) => {
  const radius = (size - 20) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;

  const getColor = () => {
    if (score >= 70) return "text-success"; // Green for safe
    if (score >= 40) return "text-warning"; // Yellow for caution
    return "text-destructive";             // Red for danger
  };

  const getGlow = () => {
    if (score >= 70) return "drop-shadow(0 0 8px hsl(145 65% 42% / 0.6))";
    if (score >= 40) return "drop-shadow(0 0 8px hsl(32 95% 55% / 0.6))";
    return "drop-shadow(0 0 8px hsl(0 72% 55% / 0.6))";
  };

  return (
    <div className="relative flex items-center justify-center" style={{ width: size, height: size }}>
      {/* THE MISSING SVG BLOCK STARTS HERE */}
      <svg width={size} height={size} className="-rotate-90" style={{ filter: getGlow() }}>
        {/* Background Circle (The dim track) */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="hsl(var(--border))"
          strokeWidth="8"
        />
        {/* Progress Circle (The actual colored ring) */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="currentColor"
          strokeWidth="8"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          className={cn("transition-all duration-1000 ease-out", getColor())}
        />
      </svg>
      {/* THE MISSING SVG BLOCK ENDS HERE */}

      <div className="absolute flex flex-col items-center">
        <span className={cn("font-mono text-4xl font-bold", getColor())}>{score}</span>
        <span className="text-xs text-muted-foreground font-mono uppercase tracking-wider">Score</span>
      </div>
    </div>
  );
};