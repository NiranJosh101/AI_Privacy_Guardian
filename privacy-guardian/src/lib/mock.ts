import { ScanResult, ScanStage } from "@/types/privacy";

const mockResults: Record<string, ScanResult> = {
  flag: {
    verdict: "FLAG",
    risk_score: 78,
    explanation: "This site engages in extensive cross-site tracking and shares user data with 14 third-party entities without explicit consent.",
    violations: [
      { rule: "Disallow 3rd Party Sharing", evidence: "\"We may share your information with our advertising partners, analytics providers, and affiliated companies...\"" },
      { rule: "Block Cross-Site Tracking", evidence: "\"We use cookies and similar technologies to track your activity across other sites to serve you personalized content.\"" },
      { rule: "Max 30-Day Data Retention", evidence: "\"Your data will be retained for up to 5 years after your last interaction with our services.\"" },
    ],
  },
  clear: {
    verdict: "CLEAR",
    risk_score: 12,
    explanation: "This site has a transparent privacy policy with minimal data collection and no third-party sharing.",
    violations: [],
  },
};

export const simulateScan = (
  onStageChange: (stage: ScanStage) => void,
  onComplete: (result: ScanResult) => void,
) => {
  const stages: ScanStage[] = ["locating", "analyzing", "judging", "complete"];
  const delays = [1200, 1800, 1500, 500];
  const isFlagged = Math.random() > 0.4;

  let i = 0;
  const next = () => {
    if (i >= stages.length) {
      onComplete(isFlagged ? mockResults.flag : mockResults.clear);
      return;
    }
    onStageChange(stages[i]);
    setTimeout(() => { i++; next(); }, delays[i]);
  };
  next();
};

export const mockPostProfile = async (config: unknown) => {
  console.log("POST /profile/setup →", JSON.stringify(config, null, 2));
  return new Promise((resolve) => setTimeout(() => resolve({ status: 200, message: "Profile created" }), 800));
};
