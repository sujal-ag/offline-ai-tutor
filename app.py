import sys
from PyQt5.QtWidgets import QApplication
from frontend.main_window import TutorMainWindow


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Modern look across platforms
    
    window = TutorMainWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()