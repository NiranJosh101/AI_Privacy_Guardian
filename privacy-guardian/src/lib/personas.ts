import { Persona, Constraint } from "@/types/privacy";

export interface PersonaCard {
  id: Persona;
  title: string;
  subtitle: string;
  icon: string;
  description: string;
}

export const personas: PersonaCard[] = [
  {
    id: "Ghost",
    title: "The Ghost",
    subtitle: "Strict Privacy",
    icon: "👻",
    description: "Maximum protection. Block all tracking, sharing, and minimize data retention.",
  },
  {
    id: "Balanced",
    title: "The Balanced",
    subtitle: "Standard Privacy",
    icon: "⚖️",
    description: "Smart defaults. Allow essential functions while blocking invasive practices.",
  },
  {
    id: "Open",
    title: "The Open",
    subtitle: "Minimal Privacy",
    icon: "🌐",
    description: "Relaxed settings. Monitor but rarely block. Stay informed without restrictions.",
  },
];

export const getConstraintsForPersona = (persona: Persona): Constraint[] => {
  const base: Constraint[] = [
    { key: "no_sharing", label: "Disallow 3rd Party Sharing", description: "Block data sharing with third-party entities", enabled: false },
    { key: "no_tracking", label: "Block Cross-Site Tracking", description: "Prevent tracking across different websites", enabled: false },
    { key: "no_fingerprinting", label: "Block Browser Fingerprinting", description: "Prevent unique browser identification techniques", enabled: false },
    { key: "no_ads", label: "Block Targeted Advertising", description: "Prevent personalized ad targeting", enabled: false },
    { key: "max_retention_30", label: "Max 30-Day Data Retention", description: "Flag sites retaining data beyond 30 days", enabled: false },
    { key: "require_encryption", label: "Require Data Encryption", description: "Flag sites not using proper encryption", enabled: false },
    { key: "no_location", label: "Block Location Access", description: "Prevent location data collection", enabled: false },
    { key: "no_biometrics", label: "Block Biometric Collection", description: "Prevent biometric data harvesting", enabled: false },
  ];

  const presets: Record<Persona, string[]> = {
    Ghost: ["no_sharing", "no_tracking", "no_fingerprinting", "no_ads", "max_retention_30", "require_encryption", "no_location", "no_biometrics"],
    Balanced: ["no_sharing", "no_tracking", "no_ads", "max_retention_30"],
    Open: ["no_sharing"],
  };

  return base.map((c) => ({
    ...c,
    enabled: presets[persona].includes(c.key),
  }));
};
