from langchain_text_splitters import RecursiveCharacterTextSplitter
from configs.config_manager import ConfigManager
import logging

logger = logging.getLogger(__name__)

class PolicyChunker:
    def __init__(self,):
        config = ConfigManager().get_interpreter_config().chunking
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.chunk_size,
            chunk_overlap=config.chunk_overlap,
            separators=config.separators
        )

    def split(self, text: str) -> list[str]:
        """
        Transforms raw policy text into manageable semantic chunks.
        """
        try:
            chunks = self.splitter.split_text(text)
            logger.info(f"Successfully split policy into {len(chunks)} chunks.")
            return chunks
        except Exception as e:
            logger.error(f"Failed to chunk text: {str(e)}")
            raise e