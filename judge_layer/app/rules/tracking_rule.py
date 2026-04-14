from typing import Optional, List
from app.rules.base import BaseRule
from app.models.schema import SiteProfile, Violation


class TrackingRule(BaseRule):
    """
    Evaluates whether a site performs user tracking using multiple signals.

    This is a multi-field rule that checks across:
    - data_collection signals
    - third-party sharing behavior
    """

    def __init__(
        self,
        constraint_key: str,
        tracking_signals: List[str],
        message: str,
        severity: str = "critical"
    ):
        super().__init__(constraint_key, severity)
        self.tracking_signals = tracking_signals
        self.message = message

    def evaluate(self, user_pref: bool, site: SiteProfile) -> Optional[Violation]:
        if not user_pref:
            return None

        detected_signals = []

        # 1. Check data_collection signals
        for signal in self.tracking_signals:
            if site.data_collection.get(signal, False):
                detected_signals.append(signal)

        # 2. Check third-party sharing (common tracking vector)
        if site.third_party_sharing:
            detected_signals.append("third_party_sharing")

        # If ANY tracking signal is detected → violation
        if detected_signals:
            return Violation(
                type=self.constraint_key,
                severity=self.severity,
                description=self.message + f" (Detected: {', '.join(detected_signals)})"
            )

        return None