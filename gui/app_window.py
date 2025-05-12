"""
Main application window for the TerraScope GUI.
"""
import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTabWidget, 
                            QVBoxLayout, QHBoxLayout, QWidget, QPushButton,
                            QLabel, QStatusBar, QMessageBox, QSplitter)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QFont

# Import from our package
from gui.drag_drop_canvas import DragDropCanvas
from gui.form_generator import FormGenerator
from core.resource_manager import ResourceManager
from core.terraform_writer import TerraformWriter
from core.terraform_runner import TerraformRunner

class AppWindow(QMainWindow):
    """Main application window for TerraScope."""
    
    def __init__(self):
        """Initialize the main application window."""
        super().__init__()
        
        # Initialize backend components
        self.resource_manager = ResourceManager()
        self.terraform_writer = TerraformWriter()
        self.terraform_runner = TerraformRunner()
        
        # Set window properties
        self.setWindowTitle("TerraScope - Visual Terraform Builder")
        self.setMinimumSize(1000, 700)
        
        # Setup UI
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the user interface."""
        # Create central widget and main layout
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        
        # Create header
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(10, 5, 10, 5)
        
        title_label = QLabel("TerraScope")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_terraform)
        
        generate_button = QPushButton("Generate Terraform")
        generate_button.clicked.connect(self.generate_terraform)
        
        run_button = QPushButton("Run")
        run_button.clicked.connect(self.run_terraform)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(save_button)
        header_layout.addWidget(generate_button)
        header_layout.addWidget(run_button)
        
        # Create main content area with splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # Create tabs
        tabs = QTabWidget()
        
        # Resources tab
        self.canvas = DragDropCanvas(self.resource_manager)
        tabs.addTab(self.canvas, "Canvas")
        
        # Preview tab
        preview_widget = QWidget()
        preview_layout = QVBoxLayout(preview_widget)
        self.preview_label = QLabel("Terraform code will appear here...")
        self.preview_label.setAlignment(Qt.AlignTop)
        self.preview_label.setWordWrap(True)
        self.preview_label.setFont(QFont("Courier New", 10))
        preview_layout.addWidget(self.preview_label)
        tabs.addTab(preview_widget, "Preview")
        
        # Output tab
        output_widget = QWidget()
        output_layout = QVBoxLayout(output_widget)
        self.output_label = QLabel("Terraform output will appear here...")
        self.output_label.setAlignment(Qt.AlignTop)
        self.output_label.setWordWrap(True)
        self.output_label.setFont(QFont("Courier New", 10))
        output_layout.addWidget(self.output_label)
        tabs.addTab(output_widget, "Output")
        
        # Create form area
        self.form_generator = FormGenerator()
        
        # Add widgets to splitter
        splitter.addWidget(tabs)
        splitter.addWidget(self.form_generator)
        
        # Set initial sizes
        splitter.setSizes([int(self.width() * 0.7), int(self.width() * 0.3)])
        
        # Set up connections between components
        self.canvas.resource_selected.connect(self.form_generator.load_resource_form)
        
        # Add widgets to main layout
        main_layout.addWidget(header)
        main_layout.addWidget(splitter)
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
        # Set the central widget
        self.setCentralWidget(central_widget)
    
    def save_terraform(self):
        """Save the current Terraform configuration."""
        resources = self.canvas.get_resources()
        providers = {
            "aws": {"region": "us-west-2"},
            "azurerm": {"features": {}}
        }
        
        success = self.terraform_writer.generate_main_tf(resources, providers)
        
        if success:
            self.status_bar.showMessage("Terraform configuration saved successfully")
            QMessageBox.information(self, "Success", "Terraform configuration saved to output/main.tf")
        else:
            self.status_bar.showMessage("Failed to save Terraform configuration")
            QMessageBox.critical(self, "Error", "Failed to save Terraform configuration")
    
    def generate_terraform(self):
        """Generate and display Terraform code."""
        resources = self.canvas.get_resources()
        if not resources:
            self.status_bar.showMessage("No resources to generate")
            return
        
        providers = {
            "aws": {"region": "us-west-2"},
            "azurerm": {"features": {}}
        }
        
        content = ""
        
        # Add provider blocks
        for provider_name, provider_config in providers.items():
            content += self.terraform_writer.create_provider_block(provider_name, provider_config)
            content += "\n"
        
        # Add resource blocks
        for resource in resources:
            content += self.terraform_writer.create_resource_block(
                resource["type"], 
                resource["name"], 
                resource["config"]
            )
            content += "\n"
        
        self.preview_label.setText(content)
        self.status_bar.showMessage("Terraform code generated")
    
    def run_terraform(self):
        """Run Terraform commands on the generated configuration."""
        # First save the configuration
        self.save_terraform()
        
        # Run terraform init
        success, message = self.terraform_runner.init()
        self.output_label.setText(message)
        
        if success:
            # Run terraform plan
            success, message = self.terraform_runner.plan()
            self.output_label.setText(message)
            
            if success:
                reply = QMessageBox.question(
                    self, 
                    "Apply Configuration",
                    "Do you want to apply this configuration?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                
                if reply == QMessageBox.Yes:
                    success, message = self.terraform_runner.apply(auto_approve=True)
                    self.output_label.setText(message)
                    
                    if success:
                        self.status_bar.showMessage("Terraform apply completed successfully")
                    else:
                        self.status_bar.showMessage("Terraform apply failed")
            else:
                self.status_bar.showMessage("Terraform plan failed")
        else:
            self.status_bar.showMessage("Terraform init failed")