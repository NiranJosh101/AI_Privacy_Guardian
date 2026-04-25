import { Constraint } from "@/types/privacy";
import { cn } from "@/lib/utils";

interface Props {
  constraints: Constraint[];
  onChange: (constraints: Constraint[]) => void;
}

export const ConstraintEditor = ({ constraints, onChange }: Props) => {
  const toggle = (key: string) => {
    onChange(constraints.map((c) => (c.key === key ? { ...c, enabled: !c.enabled } : c)));
  };

  const enabledCount = constraints.filter((c) => c.enabled).length;

  return (
    <div>
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h2 className="font-display text-2xl font-bold text-foreground glow-text">Refine Constraints</h2>
          <p className="text-sm text-muted-foreground">Toggle rules to match your comfort level.</p>
        </div>
        <span className="rounded-full bg-primary/15 px-3 py-1 font-mono text-xs text-primary">
          {enabledCount}/{constraints.length} active
        </span>
      </div>
      <div className="space-y-2">
        {constraints.map((c) => (
          <button
            key={c.key}
            onClick={() => toggle(c.key)}
            className={cn(
              "flex w-full items-center gap-3 rounded-lg border p-3 text-left transition-all duration-200",
              c.enabled
                ? "border-primary/30 bg-primary/5"
                : "border-border bg-card hover:border-muted-foreground/30"
            )}
          >
            <div className={cn(
              "flex h-5 w-5 shrink-0 items-center justify-center rounded border-2 text-xs font-bold transition-all",
              c.enabled
                ? "border-primary bg-primary text-primary-foreground"
                : "border-muted-foreground/40"
            )}>
              {c.enabled && "✓"}
            </div>
            <div className="min-w-0">
              <div className="font-display text-sm font-semibold text-foreground">{c.label}</div>
              <div className="text-xs text-muted-foreground">{c.description}</div>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
};
