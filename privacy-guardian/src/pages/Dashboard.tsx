import { useState, useEffect, useRef } from "react";
import { UserConfiguration, ScanResult, ScanStage } from "@/types/privacy";
import { RadialGauge } from "@/components/RadialGauge";
import { ScanStepper } from "@/components/ScanStepper";
import { ViolationCard } from "@/components/ViolationCard";
import { PersonaBadge } from "@/components/PersonaBadge";
import { Button } from "@/components/ui/button";

interface Props {
  config: UserConfiguration | null;
}

const Dashboard = ({ config }: Props) => {
  const [stage, setStage] = useState<ScanStage>("idle");
  const [result, setResult] = useState<ScanResult | null>(null);
  const [currentUrl, setCurrentUrl] = useState("");
  const API_BASE = import.meta.env.VITE_API_BASE_URL;
  // Use a ref for the interval to clean up properly and avoid multiple polls
  const pollIntervalRef = useRef<NodeJS.Timeout | null>(null);

  const stopPolling = () => {
    if (pollIntervalRef.current) {
      clearInterval(pollIntervalRef.current);
      pollIntervalRef.current = null;
    }
  };

  const startScan = async (url: string) => {
    if (!url || !config?.userId) return;

    // Reset UI state for new scan
    stopPolling();
    setCurrentUrl(url);
    setResult(null);
    setStage("discovery");

    try {
      // 1. Trigger the Gateway Orchestrator
      const response = await fetch(`${API_BASE}/api/v1/scan`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          userId: config.userId,
          url: url,
        }),
      });

      if (!response.ok) throw new Error("Gateway failed to initiate scan");

      const { jobId } = await response.json();

      // 2. Begin Polling for results
      pollIntervalRef.current = setInterval(async () => {
        try {
          const statusRes = await fetch(`${API_BASE}/api/v1/status/${jobId}`);
          if (!statusRes.ok) return;

          const data = await statusRes.json();

          // Update stage (discovery -> reasoning -> judging)
          setStage(data.status);

          if (data.status === "complete" && data.result) {
            setResult(data.result);
            stopPolling();
          }
        } catch (pollError) {
          console.error("Polling error:", pollError);
        }
      }, 2000); // Poll every 2 seconds

    } catch (err) {
      console.error("Scan initialization failed:", err);
      setStage("idle");
    }
  };

  useEffect(() => {
    // Initial load: Get current tab and scan
    chrome.runtime.sendMessage({ type: "GET_CURRENT_TAB" }, (response) => {
      if (response?.url && !response.url.startsWith("chrome")) {
        startScan(response.url);
      }
    });

    // Listener for tab switches or updates
    const handleMessage = (message: any) => {
      if (message.type === "TAB_UPDATED" && message.url) {
        startScan(message.url);
      }
    };

    chrome.runtime.onMessage.addListener(handleMessage);

    return () => {
      chrome.runtime.onMessage.removeListener(handleMessage);
      stopPolling();
    };
  }, []);

  if (!config) {
    return (
      <div className="flex min-h-screen items-center justify-center gradient-dark">
        <p className="text-muted-foreground">No configuration found. Complete onboarding first.</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen gradient-dark p-4 sm:p-8">
      <div className="mx-auto max-w-4xl">
        {/* Header */}
        <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <div className="font-mono text-xs uppercase tracking-[0.3em] text-primary">Privacy Guardian</div>
            <h1 className="font-display text-2xl font-bold text-foreground">Live Monitor</h1>
          </div>
          <PersonaBadge config={config} />
        </div>

        {/* URL Bar */}
        <div className="mb-6 flex items-center gap-3 rounded-lg border border-border bg-card p-3">
          <div className="flex h-8 w-8 items-center justify-center rounded bg-secondary">
            <span className="text-sm">🔗</span>
          </div>
          <div className="min-w-0 flex-1">
            <div className="font-mono text-xs text-muted-foreground">Currently scanning</div>
            <div className="truncate font-mono text-sm text-foreground">{currentUrl || "Waiting for active tab..."}</div>
          </div>
          <Button
            variant="outline"
            size="sm"
            className="font-mono text-xs"
            onClick={() => startScan(currentUrl)}
            disabled={stage !== "complete" && stage !== "idle"}
          >
            {stage !== "complete" && stage !== "idle" ? "Scanning..." : "Refresh Scan"}
          </Button>
        </div>

        {/* Replace your old scanning block with this */}
        {stage !== "complete" && stage !== "idle" && (
          <div className="mb-6 rounded-xl border border-border bg-card p-6 animate-in fade-in duration-500">
            <div className="mb-6 flex items-center gap-2">
              <div className="h-3 w-3 rounded-full bg-primary animate-pulse" />
              <h4 className="font-display text-sm uppercase tracking-widest text-foreground/80">
                Live Analysis in Progress
              </h4>
            </div>

            <ScanStepper currentStage={stage} />
          </div>
        )}


        {/* Results */}
        {result && stage === "complete" && (
          <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className={`rounded-xl border p-6 ${result.verdict === "FLAG"
              ? "border-destructive/40 bg-destructive/5 glow-destructive"
              : "border-success/40 bg-success/5 glow-primary"
              }`}>
              <div className="flex flex-col items-center gap-6 sm:flex-row">
                <RadialGauge score={result.risk_score} />
                <div className="flex-1 text-center sm:text-left">
                  <div className={`mb-1 inline-block rounded-full px-4 py-1 font-mono text-xs font-bold uppercase tracking-wider ${result.verdict === "FLAG"
                    ? "bg-destructive/20 text-destructive"
                    : "bg-success/20 text-success"
                    }`}>
                    {result.verdict === "FLAG" ? "⚠ Flagged" : "✓ Clear"}
                  </div>
                  <h2 className="mb-2 font-display text-xl font-bold text-foreground">
                    {result.verdict === "FLAG" ? "Privacy Risks Detected" : "Site Looks Safe"}
                  </h2>
                  <p className="text-sm text-muted-foreground leading-relaxed">{result.explanation}</p>
                </div>
              </div>
            </div>

            {/* Violations */}
            {result.violations.length > 0 && (
              <div>
                <h3 className="mb-3 font-display text-lg font-bold text-foreground">
                  Violations ({result.violations.length})
                </h3>
                <div className="space-y-3">
                  {result.violations.map((v, i) => (
                    <ViolationCard key={i} violation={v} />
                  ))}
                </div>
              </div>
            )}

            {/* Config Summary */}
            <div className="rounded-lg border border-border bg-card p-4">
              <h3 className="mb-2 font-display text-sm font-bold text-foreground">Active Policy Constraints</h3>
              <pre className="overflow-x-auto rounded bg-background p-3 font-mono text-xs text-muted-foreground">
                {JSON.stringify(config.constraints, null, 2)}
              </pre>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;