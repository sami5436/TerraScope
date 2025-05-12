# TerraScope Project

## Table of Contents
- [Personal Background & Motivation](#personal-background--motivation)
- [Project Overview](#project-overview)
- [Directory Structure](#directory-structure)
- [Core Concepts](#core-concepts)
  - [What is `__init__.py`?](#what-is-__init__py)
  - [Directory Purposes](#directory-purposes)
- [Object-Oriented Programming (OOP) in TerraScope](#object-oriented-programming-oop-in-terrascope)
  - [Key Classes and Their Responsibilities](#key-classes-and-their-responsibilities)
  - [OOP Principles Applied](#oop-principles-applied)
- [Detailed Function Documentation](#detailed-function-documentation)
  - [Core Module Functions](#core-module-functions)
  - [GUI Module Functions](#gui-module-functions)
  - [How Everything Connects](#how-everything-connects)

## Personal Background & Motivation

During my time at ExxonMobil, I worked extensively with Terraform to manage large-scale infrastructure. While Terraform is incredibly powerful, I noticed that many team members struggled with the HCL syntax and the lack of visual representation for infrastructure resources. This project was born from that experience - a solution to make Infrastructure as Code (IaC) more accessible to everyone.

TerraScope represents a quick and intuitive tool that bridges the gap between visual design and code generation. It's especially valuable for:
- Team members new to Terraform who need to understand infrastructure relationships
- Quick prototyping of infrastructure designs before writing code
- Visual verification of complex infrastructure dependencies
- Educational purposes to teach Terraform concepts

## Project Overview

TerraScope is a visual infrastructure builder that generates Terraform code. Built with PyQt5 and Python, it provides a drag-and-drop interface for designing cloud infrastructure that automatically generates valid Terraform configurations.

## Directory Structure

```
TerraScope/
├── core/               # Backend business logic
├── data/               # Static configuration files  
├── gui/                # User interface components
├── output/             # Generated files (Terraform, logs)
├── tests/              # Automated test suite
├── utils/              # Helper functions
├── main.py             # Application entry point
└── .gitignore          # Git ignore configuration
```

## Core Concepts

### What is `__init__.py`?
The `__init__.py` files are special Python files that mark a directory as a Python package. They:
- Allow Python to recognize the directory as a module that can be imported
- Can contain initialization code that runs when the package is imported
- Enable organized imports like `from core.resource_manager import ResourceManager`

### Directory Purposes

#### `/core` - Backend Business Logic
Contains the core functionality of the application, separated from the user interface:
- **`__init__.py`**: Initializes logging and checks for Terraform installation
- **`resource_manager.py`**: Loads and manages infrastructure resource templates from JSON
- **`terraform_writer.py`**: Converts resource configurations into Terraform HCL code  
- **`terraform_runner.py`**: Executes Terraform commands (init, plan, apply)

#### `/gui` - Graphical User Interface
Houses all visual components using PyQt5:
- **`__init__.py`**: Package initializer for GUI components
- **`app_window.py`**: Main application window that hosts all other components
- **`drag_drop_canvas.py`**: Visual canvas where users drag and drop infrastructure resources
- **`form_generator.py`**: Dynamically creates forms for editing resource properties

#### `/data` - Configuration Storage
- **`resources.json`**: JSON database of all available infrastructure resources (AWS, Azure) with their default configurations and required fields

#### `/output` - Generated Files
- Stores generated Terraform files (`main.tf`)
- Contains application logs (`terraform.log`)
- Excluded from version control via `.gitignore`

#### `/tests` - Test Suite
- **`test_resource_manager_pytest.py`**: Automated tests ensuring the ResourceManager works correctly
- Uses pytest framework for unit and integration testing

#### `/utils` - Helper Functions
- **`helpers.py`**: Utility functions for common tasks (name sanitization, file operations, etc.)

## Object-Oriented Programming (OOP) in TerraScope

### Key Classes and Their Responsibilities

#### 1. ResourceManager (Singleton Pattern)
```python
class ResourceManager:
    """Manages infrastructure resources and their templates."""
```
- **Purpose**: Central repository for all resource templates
- **Encapsulation**: Hides the complexity of loading and parsing JSON files
- **Methods**: Provides clean interfaces to query resources by type, provider, or popularity

#### 2. AppWindow (Inheritance)
```python
class AppWindow(QMainWindow):
    """Main application window for TerraScope."""
```
- **Inherits from**: PyQt5's QMainWindow
- **Composition**: Contains instances of DragDropCanvas, FormGenerator, TerraformWriter, and TerraformRunner
- **Responsibility**: Orchestrates interaction between all components

#### 3. DragDropCanvas (Custom Widget)
```python
class DragDropCanvas(QWidget):
    """Canvas for dragging and dropping resources."""
```
- **Inherits from**: QWidget
- **Custom Signals**: Uses Qt's signal-slot mechanism for communication
- **Encapsulation**: Manages its own list of resources and their visual representation

#### 4. ResourceItem (Encapsulation)
```python
class ResourceItem(QFrame):
    """Represents a resource on the canvas."""
```
- **State Management**: Each instance maintains its own configuration
- **Polymorphism**: All resource types share the same interface but have different properties

#### 5. FormGenerator (Dynamic Creation)
```python
class FormGenerator(QWidget):
    """Generates and manages forms for editing resource properties."""
```
- **Factory Pattern**: Creates appropriate form fields based on data types
- **Dynamic Behavior**: Generates different forms for different resource types

### OOP Principles Applied

1. **Encapsulation**: Each class manages its own data and provides public methods for interaction
2. **Inheritance**: GUI components extend PyQt5 classes to add custom functionality
3. **Composition**: AppWindow contains instances of other classes rather than inheriting everything
4. **Separation of Concerns**: Core logic (terraform generation) is separate from GUI code
5. **Polymorphism**: Different resource types are handled through the same interfaces

This architecture makes the codebase:
- **Maintainable**: Changes to one component don't affect others
- **Testable**: Components can be tested in isolation
- **Extensible**: New resource types or providers can be added easily
- **Reusable**: Core components could be used in a different UI (CLI, web app)

## Detailed Function Documentation

### Core Module Functions

#### ResourceManager Functions
```python
def __init__(self, resources_path: str = "data/resources.json"):
    """Initialize the ResourceManager with a path to resources JSON."""
    # Sets up the resource manager and loads templates from JSON
    # Creates empty resources dictionary and calls load_resources()

def load_resources(self) -> None:
    """Load resources from the JSON template file."""
    # Opens and parses the JSON file
    # Populates self.resources with available templates
    # Handles errors gracefully if file not found

def get_resource_template(self, resource_type: str) -> Optional[Dict]:
    """Get the template for a specific resource type."""
    # Retrieves a single resource template by its type name
    # Returns None if resource doesn't exist
    # Used by GUI to populate forms with default values

def get_resources_by_provider(self, provider: str) -> Dict[str, Dict]:
    """Get resources filtered by cloud provider."""
    # Filters resources by provider (aws, azurerm)
    # Returns dictionary of matching resources
    # Used to populate provider-specific lists in GUI

def get_popular_resources(self, limit: int = 10) -> List[str]:
    """Get the most popular resources based on metadata."""
    # Returns list of resources marked as popular
    # Limited by the limit parameter
    # Used for quick access to commonly used resources
```

#### TerraformWriter Functions
```python
def __init__(self, output_dir: str = "output"):
    """Initialize the TerraformWriter with output directory."""
    # Sets up the output directory for generated files
    # Creates directory if it doesn't exist

def create_terraform_block(self, backend_type: Optional[str] = None, 
                         backend_config: Optional[Dict] = None) -> str:
    """Create the terraform {} configuration block."""
    # Generates the main terraform configuration block
    # Optionally includes backend configuration
    # Returns HCL-formatted string

def create_resource_block(self, resource_type: str, resource_name: str, 
                         config: Dict) -> str:
    """Create a resource configuration block."""
    # Converts resource config to HCL format
    # Handles nested configurations recursively
    # Sanitizes resource names for HCL compatibility

def _format_attribute(self, key: str, value: Any, indent: int = 0) -> str:
    """Format a configuration attribute for HCL."""
    # Recursive helper function for formatting
    # Handles different data types (dict, list, string, bool)
    # Manages proper indentation for nested structures

def generate_main_tf(self, resources: List[Dict], 
                    providers: Dict[str, Dict] = None) -> bool:
    """Generate the main.tf file with resources and providers."""
    # Orchestrates the generation of complete Terraform file
    # Combines provider and resource blocks
    # Writes to output directory
```

#### TerraformRunner Functions
```python
def __init__(self, working_dir: str = "output"):
    """Initialize the TerraformRunner."""
    # Sets up working directory for Terraform execution
    # Ensures directory exists

def run_command(self, command: List[str]) -> Tuple[int, str, str]:
    """Run a Terraform command."""
    # Executes Terraform CLI commands
    # Captures stdout and stderr
    # Returns exit code and output

def init(self) -> Tuple[bool, str]:
    """Run terraform init."""
    # Initializes Terraform in the working directory
    # Downloads required providers
    # Returns success status and message

def plan(self) -> Tuple[bool, str]:
    """Run terraform plan."""
    # Creates execution plan showing what will change
    # Doesn't modify actual infrastructure
    # Returns success status and output

def apply(self, auto_approve: bool = False) -> Tuple[bool, str]:
    """Run terraform apply."""
    # Applies the Terraform configuration
    # Creates/updates actual infrastructure
    # Optional auto-approve for automation
```

### GUI Module Functions

#### AppWindow Functions
```python
def __init__(self):
    """Initialize the main application window."""
    # Creates instances of all major components
    # Sets up window properties and title
    # Initializes backend components

def setup_ui(self):
    """Set up the user interface."""
    # Creates layout hierarchy
    # Adds buttons, tabs, and panels
    # Connects signals between components
    # Sets up status bar

def save_terraform(self):
    """Save the current Terraform configuration."""
    # Collects resources from canvas
    # Uses TerraformWriter to generate files
    # Shows success/error messages

def generate_terraform(self):
    """Generate and display Terraform code."""
    # Creates preview of Terraform code
    # Updates preview tab with generated HCL
    # Doesn't save to file yet

def run_terraform(self):
    """Run Terraform commands on the generated configuration."""
    # Saves configuration first
    # Runs init, plan, and optionally apply
    # Updates output tab with results
```

#### DragDropCanvas Functions
```python
def __init__(self, resource_manager, parent=None):
    """Initialize the drag and drop canvas."""
    # Sets up resource list and canvas area
    # Loads resources from ResourceManager
    # Creates drag-drop functionality

def handle_double_click(self, item):
    """Handle double-click on resource list items."""
    # Adds resource to canvas on double-click
    # Alternative to drag-and-drop

def add_resource(self, resource_type, resource_name):
    """Add a resource to the canvas."""
    # Creates new ResourceItem widget
    # Loads default configuration
    # Emits signal to update form

def remove_resource(self, resource_item):
    """Remove a resource from the canvas."""
    # Removes widget from layout
    # Cleans up resource from internal list
    # Updates UI

def get_resources(self):
    """Get all resources on the canvas."""
    # Collects all resources with their configs
    # Returns list of dictionaries
    # Used by TerraformWriter for generation
```

#### FormGenerator Functions
```python
def __init__(self, parent=None):
    """Initialize the form generator."""
    # Sets up form container and layout
    # Creates apply button
    # Shows empty state initially

def load_resource_form(self, resource_type, resource_name, config):
    """Load a form for editing a resource."""
    # Clears existing form
    # Generates new fields based on config
    # Updates title and shows apply button

def generate_form_fields(self, config, prefix=""):
    """Generate form fields for the configuration."""
    # Recursively creates form fields
    # Handles nested configurations
    # Creates appropriate widget types

def create_field_widget(self, key, value):
    """Create a widget for editing a field."""
    # Factory method for widget creation
    # Returns appropriate widget based on value type
    # Handles special cases (regions, types, etc.)

def apply_changes(self):
    """Apply changes from the form to the resource."""
    # Collects values from all form fields
    # Updates resource configuration
    # Reflects changes in the canvas
```

### How Everything Connects

1. **Application Flow**:
   ```
   main.py → AppWindow → DragDropCanvas ↔ FormGenerator
                      ↓                      ↓
                 ResourceManager      TerraformWriter
                                           ↓
                                    TerraformRunner
   ```

2. **Signal Flow**:
   - User drags resource → Canvas emits `resource_selected` signal
   - FormGenerator receives signal → Loads appropriate form
   - User edits form → Apply button updates resource config
   - Generate button → TerraformWriter creates HCL code
   - Run button → TerraformRunner executes commands

3. **Data Flow**:
   - `resources.json` → ResourceManager → GUI components
   - User input → Resource configurations → TerraformWriter
   - Generated HCL → TerraformRunner → Cloud infrastructure

4. **Component Relationships**:
   - **AppWindow** acts as the orchestrator, containing all other components
   - **ResourceManager** provides data to both Canvas and FormGenerator
   - **DragDropCanvas** and **FormGenerator** communicate via Qt signals
   - **TerraformWriter** and **TerraformRunner** are independent but work in sequence
   - All components log to the same log file for debugging

This architecture ensures loose coupling while maintaining clear communication paths between components, making the system both maintainable and extensible.
