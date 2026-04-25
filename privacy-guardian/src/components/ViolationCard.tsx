// src/components/ViolationCard.tsx
import { cn } from "@/lib/utils";

export const ViolationCard = ({ violation }: { violation: any }) => {
  // Map severity to CSS classes
  const isCritical = violation.severity === "critical";
  const colorClass = isCritical ? "text-destructive" : "text-warning";
  const borderClass = isCritical ? "border-destructive/30 bg-destructive/5" : "border-warning/30 bg-warning/5";

  return (
    <div className={cn("rounded-lg border p-4 transition-all", borderClass)}>
      <div className="mb-2 flex items-center gap-2">
        <span className={cn("text-sm", colorClass)}>{isCritical ? "❌" : "⚠️"}</span>
        <span className={cn("font-display text-sm font-bold uppercase", colorClass)}>
          {violation.type}
        </span>
      </div>
      <blockquote className={cn(
        "border-l-2 pl-3 font-mono text-xs text-muted-foreground italic leading-relaxed",
        isCritical ? "border-destructive/40" : "border-warning/40"
      )}>
        "{violation.description}"
      </blockquote>
    </div>
  );
};