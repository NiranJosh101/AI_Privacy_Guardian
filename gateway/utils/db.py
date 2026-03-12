# app/utils/db.py
from motor.motor_asyncio import AsyncIOMotorClient
from configs.config_manager import cfg
from models.schemas import UserPersona


class DatabaseManager:
    async def get_persona_by_id(self, user_id: str) -> UserPersona:
        # MOCK DATA: Skip the real DB and return a default persona
        return UserPersona(
            userId=user_id,
            persona="Balanced",
            constraints={
                "no_sharing": True,
                "no_tracking": True,
                "no_fingerprinting": False,
                "no_ads": True,
                "max_retention_30": True,
                "require_encryption": True,
                "no_location": False,
                "no_biometrics": False
            }
        )

db = DatabaseManager()