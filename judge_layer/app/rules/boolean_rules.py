from typing import Optional
from .base import BaseRule
from ..models import SiteProfile, Violation

class BooleanCollectionRule(BaseRule):
    """Checks flags inside the data_collection DICT."""
    def __init__(self, constraint_key: str, site_data_key: str, message: str, severity: str = "critical"):
        super().__init__(constraint_key, severity)
        self.site_data_key = site_data_key
        self.message = message

    def evaluate(self, user_pref: bool, site: SiteProfile) -> Optional[Violation]:
        if not user_pref: return None
        
        if site.data_collection.get(self.site_data_key, False):
            return Violation(
                constraint_key=self.constraint_key,
                severity=self.severity,
                message=self.message,
                actual_value=True
            )
        return None

class SimpleAttributeRule(BaseRule):
    """Checks top-level ATTRIBUTES on the SiteProfile object."""
    def __init__(self, constraint_key: str, attribute_name: str, message: str, severity: str = "critical"):
        super().__init__(constraint_key, severity)
        self.attribute_name = attribute_name
        self.message = message

    def evaluate(self, user_pref: bool, site: SiteProfile) -> Optional[Violation]:
        if not user_pref: return None

        # getattr(object, "field_name") is the magic here
        if getattr(site, self.attribute_name, False):
            return Violation(
                constraint_key=self.constraint_key,
                severity=self.severity,
                message=self.message,
                actual_value=True
            )
        return None