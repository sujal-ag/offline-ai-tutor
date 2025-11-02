"""
Inference Handler (Transformers Version)
Manages LLM inference with streaming
"""

import time
import torch
from PyQt5.QtCore import QThread, pyqtSignal
from transformers import TextIteratorStreamer
from threading import Thread
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
        
    def format_chat_prompt(self, messages):
        """Format messages for TinyLlama"""
        prompt = ""
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            
            if role == "system":
                prompt += f"<|system|>\n{content}</s>\n"
            elif role == "user":
                prompt += f"<|user|>\n{content}</s>\n"
            elif role == "assistant":
                prompt += f"<|assistant|>\n{content}</s>\n"
        
        prompt += "<|assistant|>\n"
        return prompt
        
    def run(self):
        model = ModelManager.get_instance().get_model()
        tokenizer = ModelManager.get_instance().get_tokenizer()
        
        if model is None or tokenizer is None:
            self.error_occurred.emit("Model not loaded!")
            return
            
        try:
            start_time = time.time()
            
            prompt = self.format_chat_prompt(self.messages)
            inputs = tokenizer(prompt, return_tensors="pt")
            
            streamer = TextIteratorStreamer(
                tokenizer, 
                skip_prompt=True,
                skip_special_tokens=True
            )
            
            generation_kwargs = {
                "input_ids": inputs["input_ids"],
                "max_new_tokens": config.MAX_TOKENS,
                "temperature": config.TEMPERATURE,
                "do_sample": True,
                "top_p": 0.9,
                "streamer": streamer,
            }
            
            thread = Thread(target=model.generate, kwargs=generation_kwargs)
            thread.start()
            
            full_response = ""
            for text in streamer:
                if "</s>" in text or "<|" in text:
                    break
                self.response_chunk.emit(text)
                full_response += text
            
            thread.join()
            latency = time.time() - start_time
            full_response = full_response.strip()
            
            self.inference_complete.emit(latency, full_response)
            
        except Exception as e:
            self.error_occurred.emit(f"Inference error: {str(e)}")