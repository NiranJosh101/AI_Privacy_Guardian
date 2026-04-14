from typing import Optional, List
from app.rules.base import BaseRule
from app.models.schema import SiteProfile, Violation

class EncryptionStrengthRule(BaseRule):
    """
    Evaluates if the site's encryption meets a minimum required standard.
    """
    def __init__(
        self, 
        constraint_key: str, 
        min_allowed_standards: List[str], 
        message: str, 
        severity: str = "critical"
    ):
        super().__init__(constraint_key, severity)
        self.min_allowed_standards = min_allowed_standards
        self.message = message

    def evaluate(self, user_pref: bool, site: SiteProfile) -> Optional[Violation]:
        if not user_pref:
            return None

        # Reality check: What is the site actually using?
        actual = site.encryption_standard # e.g., "TLS 1.1" or "None"

        # If the site has no encryption or it's not in our 'Safe' list
        if actual == "None" or actual not in self.min_allowed_standards:
            return Violation(
                type=self.constraint_key,
                severity=self.severity,
                description=self.message + f" (Site uses: {actual})"
            )
        
        return None