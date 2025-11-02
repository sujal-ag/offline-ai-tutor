__version__ = "1.0.0"

# Frontend public API
from .main_window import TutorMainWindow
from .styles import MAIN_STYLESHEET, STATUS_STYLES, MESSAGE_TEMPLATES

__all__ = [
    'TutorMainWindow',
    'MAIN_STYLESHEET',
    'STATUS_STYLES',
    'MESSAGE_TEMPLATES',
]