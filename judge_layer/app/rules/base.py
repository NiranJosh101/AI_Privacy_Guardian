from abc import ABC, abstractmethod
from typing import Optional
from app.models.schema import SiteProfile, Violation

class BaseRule(ABC):
    """
    The abstract contract for all Privacy Rules.
    Each subclass represents the logic for a specific User Constraint.
    """

    def __init__(self, constraint_key: str, severity: str = "warning"):
        self.constraint_key = constraint_key
        self.severity = severity

    @abstractmethod
    def evaluate(self, user_preference: bool, site_profile: SiteProfile) -> Optional[Violation]:
        """
        Executes the comparison logic.
        :param user_preference: The boolean value from PrivacyConstraints
        :param site_profile: The full SiteProfile data from the Interpreter
        :return: A Violation object if a conflict is found, else None.
        """
        pass