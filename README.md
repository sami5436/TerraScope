# TerraScope Project Structure and Architecture

## Directory Structure Overview

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
