# Singleton-style config management
from configs.config_manager import ConfigManager
from engine.orchestrator import InterpreterOrchestrator


# Better: Load once at startup
_config_manager = ConfigManager()

def get_orchestrator():
    return InterpreterOrchestrator(_config_manager)