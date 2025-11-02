import os
from dotenv import load_dotenv
from pathlib import Path

class Config:
    """Application configuration from environment variables"""
    
    def __init__(self):
        # Load .env file from project root
        env_path = Path(__file__).parent.parent / '.env'
        load_dotenv(env_path)
        
        # Model Configuration (Transformers)
        self.MODEL_ID = os.getenv('MODEL_ID', 'TinyLlama/TinyLlama-1.1B-Chat-v1.0')
        self.MODEL_DIR = os.getenv('MODEL_DIR', 'models')
        
        # LLM Parameters
        self.MAX_TOKENS = int(os.getenv('MAX_TOKENS', '256'))
        self.TEMPERATURE = float(os.getenv('TEMPERATURE', '0.7'))
        
        # System Prompt
        self.SYSTEM_PROMPT = os.getenv(
            'SYSTEM_PROMPT',
            "You are an offline, conversational AI tutor. Your primary goal is to "
            "guide the student to the correct answer by providing clear, effective hints "
            "and analogies, not direct solutions. You prioritize data privacy. "
            "Keep responses concise (3-4 sentences max). And only answer for assisstant role."
        )
        
        # UI Configuration
        self.WINDOW_WIDTH = int(os.getenv('WINDOW_WIDTH', '1000'))
        self.WINDOW_HEIGHT = int(os.getenv('WINDOW_HEIGHT', '700'))
        self.FONT_FAMILY = os.getenv('FONT_FAMILY', 'Arial')
        self.FONT_SIZE = int(os.getenv('FONT_SIZE', '11'))
        
        # CPU threads (auto-detect optimal count). Fall back to 4 when
        # os.cpu_count() returns None (rare on some embedded platforms).
        cpu_count = os.cpu_count() or 4
        # Use half the available cores but at least 1 thread.
        self.N_THREADS = max(1, cpu_count // 2)

# Global config instance
config = Config()