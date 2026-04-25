import { UserConfiguration } from "@/types/privacy";

export const PersonaBadge = ({ config }: { config: UserConfiguration }) => {
  const activeCount = Object.values(config.constraints).filter((v) => v === true).length;
  return (
    <div className="flex items-center gap-3 rounded-lg border border-border bg-secondary/50 px-4 py-2">
      <span className="text-lg">
        {config.persona === "Ghost" ? "👻" : config.persona === "Balanced" ? "⚖️" : "🌐"}
      </span>
      <div>
        <div className="font-display text-sm font-bold text-foreground">The {config.persona}</div>
        <div className="font-mono text-xs text-muted-foreground">{activeCount} active constraints</div>
      </div>
    </div>
  );
};
