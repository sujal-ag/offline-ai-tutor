import time
from PyQt5.QtCore import QThread, pyqtSignal
from .model_manager import ModelManager
from .config import config


class InferenceThread(QThread):
    """Background thread for LLM inference"""
    
    response_chunk = pyqtSignal(str)
    inference_complete = pyqtSignal(float, str)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, messages):
        super().__init__()
        self.messages = messages
        
    def run(self):
        """Run inference"""
        llm = ModelManager.get_instance().get_model()
        
        if llm is None:
            self.error_occurred.emit("Model not loaded!")
            return
            
        try:
            start_time = time.time()
            full_response = ""
            
            # Stream inference
            response_stream = llm.create_chat_completion(
                messages=self.messages,
                max_tokens=config.MAX_TOKENS,
                temperature=config.TEMPERATURE,
                stream=True,
            )
            
            # Emit chunks
            for chunk in response_stream:
                content = chunk["choices"][0]["delta"].get("content", "")
                if content:
                    self.response_chunk.emit(content)
                    full_response += content
                    
            latency = time.time() - start_time
            self.inference_complete.emit(latency, full_response)
            
        except Exception as e:
            self.error_occurred.emit(f"Inference error: {str(e)}")