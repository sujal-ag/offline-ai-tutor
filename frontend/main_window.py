from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QTextEdit, 
    QLineEdit, QPushButton, QHBoxLayout, QLabel, QFrame
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QTextCursor

from backend.config import config
from backend.model_manager import ModelLoadThread, ModelManager
from backend.inference import InferenceThread
from .styles import MAIN_STYLESHEET, STATUS_STYLES, MESSAGE_TEMPLATES


class TutorMainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🧠 Offline AI Tutor - TinyLlama")
        self.setGeometry(100, 100, config.WINDOW_WIDTH, config.WINDOW_HEIGHT)
        
        # Initialize state
        self.messages = [{"role": "system", "content": config.SYSTEM_PROMPT}]
        self.current_response = ""
        self.msg_count = 0
        self.total_time = 0.0
        
        # Setup UI
        self.setup_ui()
        self.setStyleSheet(MAIN_STYLESHEET)
        
        # Start model loading
        self.start_model_loading()
        
    def setup_ui(self):
        """Initialize all UI components"""
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # Header
        header = QLabel("🧠 Offline AI Tutor")
        header.setFont(QFont(config.FONT_FAMILY, 18, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("color: #2c3e50; padding: 10px;")
        main_layout.addWidget(header)
        
        # Status bar
        self.status_label = QLabel("⏳ Initializing...")
        self.status_label.setFont(QFont(config.FONT_FAMILY, config.FONT_SIZE))
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet(STATUS_STYLES['thinking'])
        main_layout.addWidget(self.status_label)
        
        # Chat display
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setFont(QFont(config.FONT_FAMILY, config.FONT_SIZE))
        main_layout.addWidget(self.chat_display)
        
        # Input area
        input_frame = QFrame()
        input_layout = QHBoxLayout(input_frame)
        input_layout.setContentsMargins(0, 0, 0, 0)
        
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Type your question here...")
        self.user_input.setFont(QFont(config.FONT_FAMILY, config.FONT_SIZE))
        self.user_input.returnPressed.connect(self.send_message)
        self.user_input.setEnabled(False)
        
        self.send_btn = QPushButton("Send")
        self.send_btn.setFont(QFont(config.FONT_FAMILY, config.FONT_SIZE, QFont.Bold))
        self.send_btn.clicked.connect(self.send_message)
        self.send_btn.setEnabled(False)
        self.send_btn.setFixedWidth(100)
        
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.setFont(QFont(config.FONT_FAMILY, config.FONT_SIZE))
        self.clear_btn.clicked.connect(self.clear_chat)
        self.clear_btn.setFixedWidth(100)
        self.clear_btn.setObjectName("clearBtn")
        
        input_layout.addWidget(self.user_input)
        input_layout.addWidget(self.send_btn)
        input_layout.addWidget(self.clear_btn)
        
        main_layout.addWidget(input_frame)
        
        # Stats display
        self.stats_label = QLabel("Messages: 0 | Avg Response Time: 0.0s")
        self.stats_label.setFont(QFont(config.FONT_FAMILY, 9))
        self.stats_label.setStyleSheet("color: #7f8c8d; padding: 5px;")
        main_layout.addWidget(self.stats_label)
        
    def start_model_loading(self):
        """Start loading model in background"""
        self.add_message('system', "🔄 Initializing AI Tutor...")
        
        self.loader_thread = ModelLoadThread()
        self.loader_thread.progress.connect(self.update_loading_progress)
        self.loader_thread.finished.connect(self.model_loaded_callback)
        self.loader_thread.start()
        
    def update_loading_progress(self, message):
        """Update status during model loading"""
        self.status_label.setText(f"⏳ {message}")
        self.add_message('system', message)
        
    def model_loaded_callback(self, success, message):
        """Handle model loading completion"""
        if success:
            self.status_label.setText("✅ Ready - Ask me anything!")
            self.status_label.setStyleSheet(STATUS_STYLES['ready'])
            self.add_message('system', "✅ Model ready! You can now ask questions.")
            self.user_input.setEnabled(True)
            self.send_btn.setEnabled(True)
            self.user_input.setFocus()
        else:
            self.status_label.setText("❌ Failed to load model")
            self.status_label.setStyleSheet(STATUS_STYLES['error'])
            self.add_message('system', message)
            
    def add_message(self, msg_type, content):
        """Add a message to chat display"""
        html = MESSAGE_TEMPLATES[msg_type].format(content=content)
        self.chat_display.append(html)
        self.scroll_to_bottom()
        
    def start_ai_message(self):
        """Start a new AI response block"""
        self.chat_display.append(MESSAGE_TEMPLATES['ai_start'])
        self.current_response = ""
        
    def append_ai_chunk(self, chunk):
        """Append streaming text to AI response"""
        self.current_response += chunk
        cursor = self.chat_display.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(chunk)
        self.scroll_to_bottom()
        
    def end_ai_message(self):
        """Close AI response block"""
        cursor = self.chat_display.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertHtml(MESSAGE_TEMPLATES['ai_end'])
        self.scroll_to_bottom()
        
    def scroll_to_bottom(self):
        """Auto-scroll to bottom"""
        scrollbar = self.chat_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
    def send_message(self):
        """Handle send button click"""
        if not ModelManager.get_instance().is_loaded():
            return
            
        user_text = self.user_input.text().strip()
        if not user_text:
            return
            
        # Update UI
        self.add_message('user', user_text)
        self.messages.append({"role": "user", "content": user_text})
        self.user_input.clear()
        self.user_input.setEnabled(False)
        self.send_btn.setEnabled(False)
        
        # Update status
        self.status_label.setText("⏳ Thinking...")
        self.status_label.setStyleSheet(STATUS_STYLES['thinking'])
        
        # Start AI response
        self.start_ai_message()
        
        # Run inference
        self.llm_thread = InferenceThread(self.messages.copy())
        self.llm_thread.response_chunk.connect(self.append_ai_chunk)
        self.llm_thread.inference_complete.connect(self.inference_finished)
        self.llm_thread.error_occurred.connect(self.inference_error)
        self.llm_thread.start()
        
    def inference_finished(self, latency, full_response):
        """Handle successful inference completion"""
        self.end_ai_message()
        
        # Update message history
        self.messages.append({"role": "assistant", "content": full_response})
        
        # Update stats
        self.msg_count += 1
        self.total_time += latency
        avg_time = self.total_time / self.msg_count
        self.stats_label.setText(
            f"Messages: {self.msg_count} | Last: {latency:.2f}s | Avg: {avg_time:.2f}s"
        )
        
        # Reset UI
        self.status_label.setText(f"✅ Ready (responded in {latency:.2f}s)")
        self.status_label.setStyleSheet(STATUS_STYLES['ready'])
        self.user_input.setEnabled(True)
        self.send_btn.setEnabled(True)
        self.user_input.setFocus()
        
    def inference_error(self, error_msg):
        """Handle inference errors"""
        self.end_ai_message()
        self.add_message('system', f"❌ Error: {error_msg}")
        self.status_label.setText("❌ Error occurred")
        self.status_label.setStyleSheet(STATUS_STYLES['error'])
        self.user_input.setEnabled(True)
        self.send_btn.setEnabled(True)
        
    def clear_chat(self):
        """Clear chat history"""
        self.chat_display.clear()
        self.messages = [{"role": "system", "content": config.SYSTEM_PROMPT}]
        self.msg_count = 0
        self.total_time = 0.0
        self.stats_label.setText("Messages: 0 | Avg Response Time: 0.0s")
        self.add_message('system', "Chat cleared. Start a new conversation!")