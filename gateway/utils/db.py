# app/utils/db.py
import motor.motor_async_engine
from configs.config_manager import cfg
from models.schemas import UserPersona

class DatabaseManager:
    def __init__(self):
        # Example using MongoDB, but the logic applies to Postgres too
        self.client = motor.motor_async_engine.AsyncIOMotorClient(cfg.db_url)
        self.db = self.client.privacy_guardian

    async def get_persona_by_id(self, user_id: str) -> UserPersona:
        """Looks up the persona directly in the Gateway's DB."""
        doc = await self.db.personas.find_one({"userId": user_id})
        if not doc:
            return None
        return UserPersona(**doc)

db = DatabaseManager()