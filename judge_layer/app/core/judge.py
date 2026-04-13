from typing import List
from ..models import PrivacyConstraints, SiteProfile, Violation, EvaluationResult
from ..registry.rule_registry import registry

class JudgeEngine:
    def __init__(self, base_score: int = 100):
        self.base_score = base_score
        # Weights for scoring
        self.severity_weights = {
            "critical": 25,
            "warning": 10,
            "info": 5
        }

    def evaluate_site(self, constraints: PrivacyConstraints, site: SiteProfile) -> EvaluationResult:
        violations: List[Violation] = []
        
        # Step 3 & 4: Iterate over User Constraints and lookup Rules
        # We convert the Pydantic model to a dict to loop through keys
        user_dict = constraints.model_dump()

        for constraint_key, is_enabled in user_dict.items():
            # Skip if the user doesn't care about this specific privacy protection
            if not is_enabled:
                continue

            # Fetch the logic from the Registry
            rule = registry.get_rule(constraint_key)
            
            if rule:
                # Step 5 & 6: Execute logic and collect violations
                result = rule.evaluate(is_enabled, site)
                if result:
                    violations.append(result)

        # Step 7: Scoring Logic
        final_score = self._calculate_score(violations)
        summary = self._generate_summary(violations, site.domain)

        # Step 8: Return Structured Result
        return EvaluationResult(
            domain=site.domain,
            score=final_score,
            violations=violations,
            summary=summary
        )

    def _calculate_score(self, violations: List[Violation]) -> int:
        total_deduction = 0
        for v in violations:
            total_deduction += self.severity_weights.get(v.severity, 0)
        
        # Ensure score doesn't drop below 0
        return max(0, self.base_score - total_deduction)

    def _generate_summary(self, violations: List[Violation], domain: str) -> str:
        if not violations:
            return f"Great news! {domain} respects all of your privacy preferences."
        
        return f"Found {len(violations)} privacy conflicts on {domain}."