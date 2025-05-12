"""
Dynamically generates forms for editing resource properties.
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QLabel, 
                           QLineEdit, QComboBox, QCheckBox, QScrollArea,
                           QPushButton, QSpinBox, QDoubleSpinBox, QGroupBox)
from PyQt5.QtCore import Qt, pyqtSignal

class FormGenerator(QWidget):
    """Generates and manages forms for editing resource properties."""
    
    def __init__(self, parent=None):
        """
        Initialize the form generator.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.current_resource = None
        self.current_resource_type = None
        self.current_resource_name = None
        self.form_fields = {}
        
        # Set up UI
        layout = QVBoxLayout(self)
        
        self.title_label = QLabel("Resource Properties")
        self.title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label)
        
        # Scroll area for the form
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)
        
        self.form_container = QWidget()
        self.form_layout = QFormLayout(self.form_container)
        
        scroll_area.setWidget(self.form_container)
        
        # Add apply button
        self.apply_button = QPushButton("Apply Changes")
        self.apply_button.clicked.connect(self.apply_changes)
        layout.addWidget(self.apply_button)
        
        # Empty state
        self.empty_label = QLabel("Select a resource to edit its properties")
        self.empty_label.setAlignment(Qt.AlignCenter)
        self.form_layout.addWidget(self.empty_label)
    
    def load_resource_form(self, resource_type, resource_name, config):
        """
        Load a form for editing a resource.
        
        Args:
            resource_type: Type of resource
            resource_name: Name of the resource
            config: Current configuration
        """
        # Clear existing form
        self.clear_form()
        
        # Update current resource info
        self.current_resource_type = resource_type
        self.current_resource_name = resource_name
        
        # Update title
        self.title_label.setText(f"Edit {resource_type}: {resource_name}")
        
        # Generate form fields
        self.generate_form_fields(config)
        
        # Show apply button
        self.apply_button.setVisible(True)
    
    def clear_form(self):
        """Clear the form layout."""
        # Remove all widgets from the form layout
        while self.form_layout.count() > 0:
            item = self.form_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Reset fields dictionary
        self.form_fields = {}
    
    def generate_form_fields(self, config, prefix=""):
        """
        Generate form fields for the configuration.
        
        Args:
            config: Configuration dictionary
            prefix: Prefix for nested fields
        """
        for key, value in config.items():
            field_name = f"{prefix}{key}" if prefix else key
            
            if isinstance(value, dict):
                # Create a group box for nested fields
                group_box = QGroupBox(key.replace("_", " ").title())
                group_layout = QFormLayout(group_box)
                
                self.form_layout.addWidget(group_box)
                
                # Recursively generate nested fields
                nested_prefix = f"{field_name}."
                for nested_key, nested_value in value.items():
                    nested_field_name = f"{nested_prefix}{nested_key}"
                    
                    # Create field for nested value
                    field_widget = self.create_field_widget(nested_key, nested_value)
                    if field_widget:
                        group_layout.addRow(nested_key.replace("_", " ").title(), field_widget)
                        self.form_fields[nested_field_name] = field_widget
            else:
                # Create field for the value
                field_widget = self.create_field_widget(key, value)
                if field_widget:
                    self.form_layout.addRow(key.replace("_", " ").title(), field_widget)
                    self.form_fields[field_name] = field_widget
    
    def create_field_widget(self, key, value):
        """
        Create a widget for editing a field.
        
        Args:
            key: Field key
            value: Field value
            
        Returns:
            QWidget for editing the field
        """
        if isinstance(value, bool):
            # Checkbox for boolean values
            widget = QCheckBox()
            widget.setChecked(value)
            return widget
        elif isinstance(value, int):
            # Spin box for integer values
            widget = QSpinBox()
            widget.setRange(-2147483648, 2147483647)
            widget.setValue(value)
            return widget
        elif isinstance(value, float):
            # Double spin box for float values
            widget = QDoubleSpinBox()
            widget.setRange(-2147483648, 2147483647)
            widget.setValue(value)
            return widget
        elif isinstance(value, str):
            # Special handling for common fields
            if key.endswith("_type") or key in ["tier", "size", "type"]:
                # Combo box for type selections
                widget = QComboBox()
                
                # Add common options based on the key
                if key == "instance_type":
                    widget.addItems(["t2.micro", "t2.small", "t2.medium", "t3.micro", "t3.small", "t3.medium"])
                elif key == "account_tier":
                    widget.addItems(["Standard", "Premium"])
                elif key == "account_replication_type":
                    widget.addItems(["LRS", "GRS", "RAGRS", "ZRS", "GZRS", "RAGZRS"])
                else:
                    # Generic combo with current value
                    widget.addItem(value)
                
                # Set current value
                index = widget.findText(value)
                if index >= 0:
                    widget.setCurrentIndex(index)
                    
                return widget
            elif key in ["region", "location"]:
                # Combo box for regions/locations
                widget = QComboBox()
                
                if key == "region":
                    # AWS regions
                    widget.addItems([
                        "us-east-1", "us-east-2", "us-west-1", "us-west-2",
                        "eu-west-1", "eu-west-2", "eu-central-1",
                        "ap-northeast-1", "ap-northeast-2", "ap-southeast-1", "ap-southeast-2"
                    ])
                else:
                    # Azure locations
                    widget.addItems([
                        "East US", "East US 2", "Central US", "West US", "West US 2",
                        "North Europe", "West Europe", "UK South", "UK West",
                        "East Asia", "Southeast Asia", "Australia East"
                    ])
                
                # Set current value
                index = widget.findText(value)
                if index >= 0:
                    widget.setCurrentIndex(index)
                    
                return widget
            else:
                # Line edit for string values
                widget = QLineEdit(value)
                return widget
        else:
            # Default to line edit for other types
            widget = QLineEdit(str(value))
            return widget
    
    def apply_changes(self):
        """Apply changes from the form to the resource."""
        if not hasattr(self.parent(), "canvas") or not self.current_resource_type:
            return
        
        # Find the resource in the canvas
        for resource in self.parent().canvas.resources:
            if (resource.resource_type == self.current_resource_type and 
                resource.resource_name == self.current_resource_name):
                
                # Update the resource configuration
                updated_config = {}
                
                for field_name, widget in self.form_fields.items():
                    # Handle nested fields
                    if "." in field_name:
                        parts = field_name.split(".")
                        parent_key = parts[0]
                        child_key = parts[1]
                        
                        if parent_key not in updated_config:
                            updated_config[parent_key] = {}
                        
                        updated_config[parent_key][child_key] = self.get_widget_value(widget)
                    else:
                        updated_config[field_name] = self.get_widget_value(widget)
                
                resource.config = updated_config
                break
    
    def get_widget_value(self, widget):
        """
        Get the value from a form widget.
        
        Args:
            widget: Form field widget
            
        Returns:
            Value from the widget
        """
        if isinstance(widget, QCheckBox):
            return widget.isChecked()
        elif isinstance(widget, QSpinBox) or isinstance(widget, QDoubleSpinBox):
            return widget.value()
        elif isinstance(widget, QComboBox):
            return widget.currentText()
        elif isinstance(widget, QLineEdit):
            return widget.text()
        else:
            return None