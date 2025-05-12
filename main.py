# terraform-gui-builder/
# ├── main.py                       # Entry point (launch GUI)
# ├── gui/
# │   ├── __init__.py
# │   ├── app_window.py             # GUI layout & logic (PyQt/Tkinter)
# │   ├── drag_drop_canvas.py      # Drag/drop interactions
# │   └── form_generator.py        # Form to edit resource params
# ├── core/
# │   ├── __init__.py
# │   ├── resource_manager.py      # Load resource templates, manage state
# │   ├── terraform_writer.py      # Generate HCL `.tf` file
# │   └── terraform_runner.py      # Run CLI commands
# ├── data/
# │   └── resources.json           # JSON file for AWS & Azure resource templates
# ├── utils/
# │   └── helpers.py               # Any shared logic/utilities
# ├── output/
# │   ├── main.tf                  # Generated Terraform file
# │   └── terraform.log            # CLI output
# └── README.md


# main.py
"""
Main entry point for the TerraScope application.
"""
import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
import os

from gui.app_window import AppWindow
from core import initialize_app

def main():
    """Main entry point for the application."""
    # Initialize the core application
    initialize_app()
    
    # Create the Qt application
    app = QApplication(sys.argv)
    app.setApplicationName("TerraScope")
    
    # Set application icon if available
    if os.path.exists("resources/icon.png"):
        app.setWindowIcon(QIcon("resources/icon.png"))
    
    # Create and show the main window
    window = AppWindow()
    window.show()
    
    # Start the application event loop
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
