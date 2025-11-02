from PyQt5.QtCore import QThread, pyqtSignal
from transformers import AutoModelForCausalLM, AutoTokenizer, TextIteratorStreamer
from threading import Thread
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
        """Get singleton instance"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def set_model(self, model, tokenizer):
        """Set the loaded model and tokenizer"""
        self._model = model
        self._tokenizer = tokenizer
    
    def get_model(self):
        """Get the loaded model"""
        return self._model
    
    def get_tokenizer(self):
        """Get the tokenizer"""
        return self._tokenizer
    
    def is_loaded(self):
        """Check if model is loaded"""
        return self._model is not None and self._tokenizer is not None


class ModelLoadThread(QThread):
    """Background thread for loading model without blocking GUI"""
    
    finished = pyqtSignal(bool, str)
    progress = pyqtSignal(str)
    
    def run(self):
        """Load model in background thread"""
        try:
            # Import torch here (inside the background thread) so a broken
            # or missing torch installation doesn't crash the whole app at
            # import time. If torch fails to import we emit a helpful error
            # to the UI and stop loading.
            try:
                import torch
            except Exception as ie:
                self.finished.emit(False, f"❌ Error loading model: failed to import torch: {ie}.\nPlease ensure a compatible PyTorch build is installed for your platform.")
                return
            self.progress.emit("📥 Downloading TinyLlama model from HuggingFace...")
            
            # Load tokenizer
            tokenizer = AutoTokenizer.from_pretrained(
                "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
                cache_dir=config.MODEL_DIR
            )

            self.progress.emit("🔧 Loading model into memory...")

            # Load model with optimizations
            # Note: avoid using `device_map` or `low_cpu_mem_usage` here because
            # those options rely on the `accelerate` package. On some systems
            # (especially Windows without accelerate installed) that causes an
            # error. Loading directly onto CPU is less memory-efficient but
            # doesn't require accelerate.
            hf_model = AutoModelForCausalLM.from_pretrained(
                "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
                cache_dir=config.MODEL_DIR,
                torch_dtype=torch.float32,  # Use float32 for CPU
            )

            # Wrap HF model into a streaming-friendly adapter that exposes
            # create_chat_completion(messages=..., stream=True) to match the
            # rest of the application.
            class TransformersLLM:
                def __init__(self, model, tokenizer):
                    self.model = model
                    self.tokenizer = tokenizer

                def _build_prompt(self, messages):
                    # Simple chat-style prompt formatting
                    parts = []
                    for m in messages:
                        role = m.get('role', 'user')
                        content = m.get('content', '')
                        if role == 'system':
                            parts.append(f"System: {content}")
                        elif role == 'user':
                            parts.append(f"User: {content}")
                        else:
                            parts.append(f"Assistant: {content}")
                    # Ask the assistant to continue
                    parts.append("Assistant:")
                    return "\n".join(parts)

                def create_chat_completion(self, messages, max_tokens=256, temperature=0.7, stream=False):
                    prompt = self._build_prompt(messages)
                    inputs = self.tokenizer(prompt, return_tensors='pt')
                    input_ids = inputs.input_ids.to('cpu')

                    if not stream:
                        # Non-streaming generate
                        with torch.no_grad():
                            outputs = self.model.generate(
                                input_ids=input_ids,
                                max_new_tokens=max_tokens,
                                temperature=temperature,
                                do_sample=True,
                                top_p=0.95,
                            )
                        text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
                        return [{"choices": [{"message": {"content": text}}]}]

                    # Streaming path: use TextIteratorStreamer
                    streamer = TextIteratorStreamer(self.tokenizer, skip_prompt=True, decode_kwargs={"skip_special_tokens": True})

                    gen_kwargs = dict(
                        input_ids=input_ids,
                        max_new_tokens=max_tokens,
                        temperature=temperature,
                        do_sample=True,
                        top_p=0.95,
                        streamer=streamer,
                    )

                    # Run generation in a separate thread so we can iterate streamer here
                    thread = Thread(target=self.model.generate, kwargs=gen_kwargs)
                    thread.start()

                    # Yield chunks in the format the InferenceThread expects
                    for chunk in streamer:
                        yield {"choices": [{"delta": {"content": chunk}}]}

            wrapper = TransformersLLM(hf_model, tokenizer)

            # Store in singleton (wrapper exposes create_chat_completion)
            ModelManager.get_instance().set_model(wrapper, tokenizer)
            
            self.finished.emit(True, "✅ Model loaded successfully!")
            
        except Exception as e:
            self.finished.emit(False, f"❌ Error loading model: {str(e)}")