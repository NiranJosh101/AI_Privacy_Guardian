from typing import Dict, List, Optional
from app.rules.base import BaseRule
from app.rules.boolean_rules import BooleanCollectionRule, SimpleAttributeRule
from app.rules.numeric_rules import MaxThresholdRule
from app.rules.technical_rules import EncryptionStrengthRule
from app.models.schema import ConstraintKeys
from app.rules.tracking_rule import TrackingRule




class RuleRegistry:
    """
    The central routing system for all privacy rules.

    Responsibilities:
    - Map constraint keys → rule instances
    - Provide safe lookup
    - Validate constraints
    - Support introspection (for UI/debugging)
    """

    def __init__(self):
        self._rules: Dict[str, BaseRule] = {}
        self._setup_default_rules()

    def _setup_default_rules(self):
        """Initialize all rules for the Privacy Guardian system."""

        default_rules = [
            # 1. Data Collection Rules (dict-based signals)
            BooleanCollectionRule(
                ConstraintKeys.NO_LOCATION,
                "location",
                "Site tracks precise physical location."
            ),
            BooleanCollectionRule(
                ConstraintKeys.NO_BIOMETRICS,
                "biometrics",
                "Site collects biometric identifiers."
            ),
           TrackingRule(
                ConstraintKeys.NO_TRACKING,
                tracking_signals=[
                    "usage_stats",
                    "fingerprinting",
                    "ads"
                ],
                message="Site performs user tracking through behavioral monitoring mechanisms."
            ),
            BooleanCollectionRule(
                ConstraintKeys.NO_ADS,
                "ads",
                "Site serves personalized advertisements."
            ),
            BooleanCollectionRule(
                ConstraintKeys.NO_FINGERPRINTING,
                "fingerprinting",
                "Site uses device fingerprinting techniques."
            ),

            # 2. Top-level Attribute Rules
            SimpleAttributeRule(
                ConstraintKeys.NO_SHARING,
                "third_party_sharing",
                "Data is shared with third-party partners."
            ),

            # 3. Threshold Rules
            MaxThresholdRule(
                ConstraintKeys.MAX_RETENTION_30,
                "data_retention_period",
                threshold=30,
                message="Data retention exceeds the 30-day safety limit."
            ),

            # 4. Security Rules
            EncryptionStrengthRule(
                ConstraintKeys.REQUIRE_ENCRYPTION,
                min_allowed_standards=["TLS 1.2", "TLS 1.3"],  # removed AES mixing
                message="Site uses weak or non-existent transport encryption."
            ),
        ]

        for rule in default_rules:
            self.register(rule)

    def register(self, rule: BaseRule):
        """
        Adds a new rule to the registry.

        Raises:
            ValueError: If a rule for the same constraint already exists.
        """
        if rule.constraint_key in self._rules:
            raise ValueError(f"Rule already registered for: {rule.constraint_key}")

        self._rules[rule.constraint_key] = rule

    def get_rule(self, constraint_key: str, strict: bool = False) -> Optional[BaseRule]:
        """
        Fetch a rule for a given constraint.

        Args:
            constraint_key: The user constraint key
            strict: If True, raise error if not found

        Returns:
            BaseRule or None

        Raises:
            KeyError if strict=True and rule not found
        """
        rule = self._rules.get(constraint_key)

        if not rule and strict:
            raise KeyError(f"No rule registered for constraint: {constraint_key}")

        return rule

    def validate_constraints(self, constraints: Dict[str, bool]) -> List[str]:
        """
        Checks for unsupported constraints.

        Returns:
            List of unknown constraint keys
        """
        return [key for key in constraints.keys() if key not in self._rules]

    def get_all_registered_keys(self) -> List[str]:
        """Returns all supported constraint keys."""
        return list(self._rules.keys())

    def get_registry_snapshot(self) -> Dict[str, str]:
        """
        Debugging / introspection helper.

        Returns:
            Mapping of constraint_key → rule class name
        """
        return {
            key: rule.__class__.__name__
            for key, rule in self._rules.items()
        }


# Global singleton instance for the Judge Service
registry = RuleRegistry()