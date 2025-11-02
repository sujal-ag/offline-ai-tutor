"""
Model Manager (Transformers Version)
Handles LLM loading using HuggingFace Transformers
"""

from PyQt5.QtCore import QThread, pyqtSignal
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from .config import config


class ModelManager:
    """Singleton class to manage LLM instance"""
    
    _instance = None
    _model = None
    _tokenizer = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def set_model(self, model, tokenizer):
        self._model = model
        self._tokenizer = tokenizer
    
    def get_model(self):
        return self._model
    
    def get_tokenizer(self):
        return self._tokenizer
    
    def is_loaded(self):
        return self._model is not None and self._tokenizer is not None


class ModelLoadThread(QThread):
    """Background thread for loading model"""
    
    finished = pyqtSignal(bool, str)
    progress = pyqtSignal(str)
    
    def run(self):
        try:
            self.progress.emit("📥 Downloading TinyLlama from HuggingFace...")
            
            tokenizer = AutoTokenizer.from_pretrained(
                "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
                cache_dir=config.MODEL_DIR
            )
            
            self.progress.emit("🔧 Loading model into memory...")
            
            model = AutoModelForCausalLM.from_pretrained(
                "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
                cache_dir=config.MODEL_DIR,
                torch_dtype=torch.float32,
                low_cpu_mem_usage=True,
                device_map="cpu"
            )
            
            ModelManager.get_instance().set_model(model, tokenizer)
            self.finished.emit(True, "✅ Model loaded successfully!")
            
        except Exception as e:
            self.finished.emit(False, f"❌ Error: {str(e)}")