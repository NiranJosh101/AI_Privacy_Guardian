from typing import Optional
from app.rules.base import BaseRule
from app.models.schema import SiteProfile, Violation

class MaxThresholdRule(BaseRule):
    """
    Evaluates if a site value exceeds a maximum allowed threshold.
    Logic: if site_value > threshold -> Violation
    """
    def __init__(
        self, 
        constraint_key: str, 
        attribute_name: str, 
        threshold: int, 
        message: str, 
        severity: str = "warning"
    ):
        super().__init__(constraint_key, severity)
        self.attribute_name = attribute_name
        self.threshold = threshold
        self.message = message

    def evaluate(self, user_pref: bool, site: SiteProfile) -> Optional[Violation]:
        # If user doesn't have the 'max_retention' toggle on, skip
        if not user_pref:
            return None

        # Get the value (e.g., site.data_retention_period)
        site_value = getattr(site, self.attribute_name, None)

        # Logic: If site_value is None, it's often 'indefinite' (Violation)
        # Logic: If site_value > threshold (Violation)
        if site_value is None or site_value > self.threshold:
            actual_display = site_value if site_value is not None else "Indefinite"
            
            return Violation(
                type=self.constraint_key,
                severity=self.severity,
                description=self.message + f" (Site value: {actual_display})"
            )

        return None