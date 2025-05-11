"""
Main entry point for the TerraScope application.
"""
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from gui.app_window import AppWindow

def main():
    """Main entry point for the application."""
    # Create the Qt application
    app = QApplication(sys.argv)
    app.setApplicationName("TerraScope")
    
    # Create and show the main window
    window = AppWindow()
    window.show()
    
    # Start the application event loop
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()