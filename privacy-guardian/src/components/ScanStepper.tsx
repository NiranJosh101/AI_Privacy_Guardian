import { ScanStage } from "@/types/privacy";
import { cn } from "@/lib/utils";
import { Check } from "lucide-react"; // Ensure you have lucide-react installed

// 1. MATCH THESE TO YOUR BACKEND STATUSES
const steps: { stage: ScanStage; label: string }[] = [
  { stage: "discovery", label: "Locating Policy" },
  { stage: "reasoning", label: "Analyzing Clauses" },
  { stage: "judging", label: "Judging Compliance" },
];

const stageOrder: ScanStage[] = ["discovery", "reasoning", "judging", "complete"];

interface Props {
  currentStage: ScanStage;
}

export const ScanStepper = ({ currentStage }: Props) => {
  const currentIdx = stageOrder.indexOf(currentStage);

  return (
    <div className="flex items-center w-full justify-between">
      {steps.map((step, i) => {
        const stepIdx = stageOrder.indexOf(step.stage);
        const isActive = stepIdx === currentIdx;
        const isDone = stepIdx < currentIdx;

        return (
          <div key={step.stage} className={cn("flex items-center", i !== steps.length - 1 && "flex-1")}>
            {/* Step Group: Circle + Text */}
            <div className="flex items-center gap-1.5 shrink-0">
              {/* Smaller Bubble */}
              <div className={cn(
                "relative flex h-5 w-5 shrink-0 items-center justify-center rounded-full text-[10px] font-bold transition-all duration-500",
                isDone ? "bg-primary text-primary-foreground" :
                  isActive ? "bg-primary/20 text-primary border border-primary/50" :
                    "bg-secondary/50 text-muted-foreground border border-transparent"
              )}>
                {isDone ? <Check size={10} /> : i + 1}
                {isActive && <div className="absolute inset-0 animate-ping rounded-full bg-primary/10" />}
              </div>

              {/* Slightly smaller text for better fit */}
              <span className={cn(
                "font-sans text-[11px] font-medium whitespace-nowrap transition-all",
                isActive ? "text-primary" : isDone ? "text-foreground" : "text-muted-foreground"
              )}>
                {step.label.replace('...', '')}
              </span>
            </div>

            {/* Shorter Connector Line */}
            {i < steps.length - 1 && (
              <div className={cn(
                "h-[1px] min-w-[8px] flex-1 mx-2 transition-all duration-700",
                isDone ? "bg-primary/60" : "bg-border/40"
              )} />
            )}
          </div>
        );
      })}
    </div>
  );
};