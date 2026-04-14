import logging
from typing import List, Dict
from app.models.schema import PrivacyConstraints, SiteProfile, Violation, EvaluationResult
from app.registry.rules_registry import registry

# Standard logging for server-side monitoring
logger = logging.getLogger("JudgeService")

class JudgeEngine:
    def __init__(self, base_score: int = 100, strict: bool = False):
        self.base_score = base_score
        self.strict = strict
        
        # Scoring logic
        self.severity_weights = {
            "critical": 25,
            "warning": 10,
            "info": 5
        }
        self.default_severity_weight = 5

    def evaluate_site(self, constraints: PrivacyConstraints, site: SiteProfile) -> EvaluationResult:
        logger.info(f"Starting evaluation for domain: {site.domain}")
        
        violations: List[Violation] = []
        user_dict: Dict[str, bool] = constraints.model_dump()

        # Step 0: Validate constraints
        unknown_constraints = registry.validate_constraints(user_dict)
        if unknown_constraints:
            logger.warning(f"Unknown constraints detected: {unknown_constraints}")
            if self.strict:
                raise ValueError(f"Unsupported constraints: {unknown_constraints}")

        # Step 1-4: Execute Rules
        for constraint_key, is_enabled in user_dict.items():
            if not is_enabled:
                continue

            rule = registry.get_rule(constraint_key)
            if not rule:
                continue

            try:
                result = rule.evaluate(True, site)
                if result:
                    logger.info(f"Violation found: {result.type}")
                    violations.append(result)
            except Exception as e:
                logger.error(f"Error in rule {constraint_key}: {str(e)}")
                if self.strict:
                    raise e

        # Step 5: Scoring
        final_score = self._calculate_score(violations)

        # Step 6: Summary/Explanation
        explanation = self._generate_summary(violations, site.domain)

        # Step 7: Verdict Logic
        # Flag if score is low or a critical issue exists
        has_critical = any(v.severity == "critical" for v in violations)
        verdict_str = "FLAG" if (final_score < 70 or has_critical) else "CLEAR"

        return EvaluationResult(
            verdict=verdict_str,
            risk_score=final_score,
            explanation=explanation,
            violations=violations
        )

    def _calculate_score(self, violations: List[Violation]) -> int:
        total_deduction = 0
        for v in violations:
            total_deduction += self.severity_weights.get(
                v.severity, self.default_severity_weight
            )
        return max(0, self.base_score - total_deduction)

    def _generate_summary(self, violations: List[Violation], domain: str) -> str:
        if not violations:
            return f"Great news! {domain} respects all of your privacy preferences."

        severity_count = {"critical": 0, "warning": 0, "info": 0}
        for v in violations:
            if v.severity in severity_count:
                severity_count[v.severity] += 1

        parts = [f"{count} {sev}" for sev, count in severity_count.items() if count > 0]
        return f"{domain} has {len(violations)} issues ({', '.join(parts)})."