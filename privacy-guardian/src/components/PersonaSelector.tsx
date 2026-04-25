import { personas, PersonaCard as PersonaCardType } from "@/lib/personas";
import { Persona } from "@/types/privacy";
import { cn } from "@/lib/utils";

interface Props {
  selected: Persona | null;
  onSelect: (p: Persona) => void;
}

const PersonaCard = ({ card, isSelected, onClick }: { card: PersonaCardType; isSelected: boolean; onClick: () => void }) => (
  <button
    onClick={onClick}
    className={cn(
      "relative flex flex-col items-center gap-3 rounded-xl border-2 p-6 text-center transition-all duration-300 hover:scale-[1.03]",
      isSelected
        ? "border-primary bg-primary/10 glow-primary"
        : "border-border bg-card hover:border-primary/40"
    )}
  >
    <span className="text-4xl">{card.icon}</span>
    <h3 className="font-display text-lg font-bold text-foreground">{card.title}</h3>
    <span className={cn(
      "rounded-full px-3 py-0.5 text-xs font-mono font-semibold uppercase tracking-wider",
      isSelected ? "bg-primary text-primary-foreground" : "bg-secondary text-secondary-foreground"
    )}>
      {card.subtitle}
    </span>
    <p className="text-sm text-muted-foreground leading-relaxed">{card.description}</p>
    {isSelected && (
      <div className="absolute -top-2 -right-2 flex h-6 w-6 items-center justify-center rounded-full bg-primary text-primary-foreground text-xs font-bold">✓</div>
    )}
  </button>
);

export const PersonaSelector = ({ selected, onSelect }: Props) => (
  <div>
    <h2 className="mb-2 font-display text-2xl font-bold text-foreground glow-text">Choose Your Shield</h2>
    <p className="mb-6 text-sm text-muted-foreground">Select a privacy persona to define your protection baseline.</p>
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
      {personas.map((p) => (
        <PersonaCard key={p.id} card={p} isSelected={selected === p.id} onClick={() => onSelect(p.id)} />
      ))}
    </div>
  </div>
);
