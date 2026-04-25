import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Persona, Constraint, UserConfiguration } from "@/types/privacy";
import { getConstraintsForPersona } from "@/lib/personas";
import { mockPostProfile } from "@/lib/mock";
import { PersonaSelector } from "@/components/PersonaSelector";
import { ConstraintEditor } from "@/components/ConstraintEditor";
import { Button } from "@/components/ui/button";

interface Props {
  onComplete: (config: UserConfiguration) => void;
}

const Onboarding = ({ onComplete }: Props) => {
  const navigate = useNavigate();
  const [step, setStep] = useState<1 | 2>(1);
  const [persona, setPersona] = useState<Persona | null>(null);
  const [constraints, setConstraints] = useState<Constraint[]>([]);
  const [loading, setLoading] = useState(false);

  const handlePersonaSelect = (p: Persona) => {
    setPersona(p);
    setConstraints(getConstraintsForPersona(p));
  };

  const handleFinish = async () => {
    if (!persona) return;
    setLoading(true);

    const config: UserConfiguration = {
      userId: crypto.randomUUID(),
      persona,
      constraints: constraints.reduce((acc, c) => {
        acc[c.key] = c.enabled;
        return acc;
      }, {} as Record<string, boolean>),
    };

    await mockPostProfile(config);
    onComplete(config);
    setLoading(false);
    navigate("/dashboard");
  };

  return (
    <div className="flex min-h-screen items-center justify-center gradient-dark p-4">
      <div className="w-full max-w-3xl">
        {/* Header */}
        <div className="mb-8 text-center">
          <div className="mb-2 font-mono text-xs uppercase tracking-[0.3em] text-primary animate-pulse-glow">Privacy Guardian</div>
          <h1 className="font-display text-3xl font-bold text-foreground sm:text-4xl">
            Configure Your <span className="text-primary glow-text">Shield</span>
          </h1>
        </div>

        {/* Step indicator */}
        <div className="mb-6 flex items-center justify-center gap-3">
          {[1, 2].map((s) => (
            <div key={s} className="flex items-center gap-2">
              {s > 1 && <div className={`h-px w-8 ${step >= 2 ? "bg-primary" : "bg-border"}`} />}
              <div className={`flex h-7 w-7 items-center justify-center rounded-full font-mono text-xs font-bold ${
                step >= s ? "bg-primary text-primary-foreground" : "bg-secondary text-muted-foreground"
              }`}>
                {step > s ? "✓" : s}
              </div>
            </div>
          ))}
        </div>

        {/* Content */}
        <div className="rounded-xl border border-border bg-card p-6">
          {step === 1 && (
            <>
              <PersonaSelector selected={persona} onSelect={handlePersonaSelect} />
              <div className="mt-6 flex justify-end">
                <Button
                  disabled={!persona}
                  onClick={() => setStep(2)}
                  className="font-mono"
                >
                  Continue →
                </Button>
              </div>
            </>
          )}

          {step === 2 && (
            <>
              <ConstraintEditor constraints={constraints} onChange={setConstraints} />
              <div className="mt-6 flex justify-between">
                <Button variant="ghost" onClick={() => setStep(1)} className="font-mono text-muted-foreground">
                  ← Back
                </Button>
                <Button onClick={handleFinish} disabled={loading} className="font-mono">
                  {loading ? "Deploying Shield..." : "Activate Shield →"}
                </Button>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default Onboarding;
