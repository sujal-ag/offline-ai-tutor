MAIN_STYLESHEET = """
    QMainWindow {
        background-color: #ecf0f1;
    }
    
    QTextEdit {
        background-color: white;
        border: 2px solid #bdc3c7;
        border-radius: 8px;
        padding: 10px;
    }
    
    QLineEdit {
        padding: 10px;
        border: 2px solid #bdc3c7;
        border-radius: 8px;
        background-color: white;
        font-size: 11pt;
    }
    
    QLineEdit:focus {
        border: 2px solid #3498db;
    }
    
    QPushButton {
        background-color: #3498db;
        color: white;
        border: none;
        padding: 10px;
        border-radius: 8px;
        font-weight: bold;
    }
    
    QPushButton:hover {
        background-color: #2980b9;
    }
    
    QPushButton:pressed {
        background-color: #21618c;
    }
    
    QPushButton:disabled {
        background-color: #95a5a6;
    }
    
    #clearBtn {
        background-color: #e74c3c;
    }
    
    #clearBtn:hover {
        background-color: #c0392b;
    }
"""

STATUS_STYLES = {
    'loading': "background-color: #f39c12; color: white; padding: 8px; border-radius: 5px; font-weight: bold;",
    'ready': "background-color: #27ae60; color: white; padding: 8px; border-radius: 5px; font-weight: bold;",
    'error': "background-color: #e74c3c; color: white; padding: 8px; border-radius: 5px; font-weight: bold;",
    'thinking': "background-color: #3498db; color: white; padding: 8px; border-radius: 5px; font-weight: bold;",
}

MESSAGE_TEMPLATES = {
    'system': """
        <div style='background-color: #fff3cd; border-left: 4px solid #ffc107; 
                    padding: 10px; margin: 5px 0; border-radius: 5px;'>
            <b style='color: #856404;'>SYSTEM:</b><br>
            <span style='color: #856404;'>{content}</span>
        </div>
    """,
    'user': """
        <div style='background-color: #d1ecf1; border-left: 4px solid #17a2b8; 
                    padding: 10px; margin: 5px 0; border-radius: 5px;'>
            <b style='color: #0c5460;'>You:</b><br>
            <span style='color: #0c5460;'>{content}</span>
        </div>
    """,
    'ai_start': """
        <div style='background-color: #d4edda; border-left: 4px solid #28a745; 
                    padding: 10px; margin: 5px 0; border-radius: 5px;'>
            <b style='color: #155724;'>AI Tutor:</b><br>
            <span style='color: #155724;'>
    """,
    'ai_end': """
            </span>
        </div>
    """
}
