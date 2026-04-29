export type Persona = "Ghost" | "Balanced" | "Open";

export interface Constraint {
  key: string;
  label: string;
  description: string;
  enabled: boolean;
}



export interface UserConfiguration {
  userId: string;
  persona: Persona;
  constraints: Record<string, boolean | number>;
}

export type Verdict = "FLAG" | "CLEAR";


export interface Violation {
  type: string;
  severity: string;
  description: string;
}

export interface ScanResult {
  verdict: Verdict;
  risk_score: number;
  explanation: string;
  violations: Violation[];
}

export type ScanStage = "idle" | "discovery" | "analyzing" | "judging" | "complete";
