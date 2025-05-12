"""
Canvas for dragging and dropping infrastructure resources.
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QScrollArea, QFrame, QPushButton, QMenu, QAction,
                            QListWidget, QListWidgetItem)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QDrag, QPixmap, QPainter, QColor, QFont

class ResourceItem(QFrame):
    """Represents a resource on the canvas."""
    
    def __init__(self, resource_type, resource_name, parent=None):
        """
        Initialize a resource item.
        
        Args:
            resource_type: Type of resource (e.g., "aws_s3_bucket")
            resource_name: Name/identifier for the resource
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.resource_type = resource_type
        self.resource_name = resource_name
        self.config = {}
        
        # Set up UI
        self.setFrameShape(QFrame.StyledPanel)
        self.setLineWidth(2)
        self.setMinimumSize(200, 100)
        self.setMaximumSize(300, 150)
        self.setStyleSheet(
            "ResourceItem {"
            "   background-color: #f0f8ff;"
            "   border: 2px solid #4682b4;"
            "   border-radius: 5px;"
            "}"
        )
        
        layout = QVBoxLayout(self)
        
        # Resource type
        type_label = QLabel(resource_type)
        type_label.setFont(QFont("Arial", 10, QFont.Bold))
        layout.addWidget(type_label)
        
        # Resource name
        name_label = QLabel(resource_name)
        layout.addWidget(name_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        edit_button = QPushButton("Edit")
        edit_button.clicked.connect(self.edit_resource)
        
        delete_button = QPushButton("Delete")
        delete_button.clicked.connect(self.remove_from_canvas)
        
        button_layout.addWidget(edit_button)
        button_layout.addWidget(delete_button)
        layout.addLayout(button_layout)
    
    def edit_resource(self):
        """Emit signal to edit this resource."""
        if hasattr(self.parent(), "resource_selected"):
            self.parent().resource_selected.emit(self.resource_type, self.resource_name, self.config)
    
    def remove_from_canvas(self):
        """Remove this resource from the canvas."""
        if hasattr(self.parent(), "remove_resource"):
            self.parent().remove_resource(self)
    
    def mousePressEvent(self, event):
        """Handle mouse press events for dragging."""
        if event.button() == Qt.LeftButton:
            # Create a drag object
            drag = QDrag(self)
            
            # Create a pixmap for dragging
            pixmap = QPixmap(self.size())
            pixmap.fill(Qt.transparent)
            
            painter = QPainter(pixmap)
            painter.setOpacity(0.7)
            self.render(painter)
            painter.end()
            
            drag.setPixmap(pixmap)
            drag.setHotSpot(event.pos())
            
            # Start the drag
            drag.exec_(Qt.MoveAction)

class DropArea(QWidget):
    """Custom widget for handling drops from the resource list."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.canvas = parent
    
    def dragEnterEvent(self, event):
        """Handle drag enter events."""
        print("Drag enter event received in DropArea")
        if event.mimeData().hasFormat("application/x-qabstractitemmodeldatalist"):
            print("Accepting drag with application/x-qabstractitemmodeldatalist")
            event.acceptProposedAction()
        elif event.mimeData().hasText():
            print("Accepting drag with text")
            event.acceptProposedAction()
        else:
            print(f"Available formats: {event.mimeData().formats()}")
    
    def dropEvent(self, event):
        """Handle drop events."""
        print("Drop event received in DropArea")
        if self.canvas and hasattr(self.canvas, 'resource_list'):
            # Get selected items from the parent canvas's resource list
            items = self.canvas.resource_list.selectedItems()
            if items:
                print(f"Selected items: {len(items)}")
                resource_type = items[0].data(Qt.UserRole)
                print(f"Resource type: {resource_type}")
                resource_name = f"{resource_type.split('_')[-1]}_{len(self.canvas.resources)}"
                self.canvas.add_resource(resource_type, resource_name)
        event.acceptProposedAction()

class DragDropCanvas(QWidget):
    """Canvas for dragging and dropping resources."""
    
    resource_selected = pyqtSignal(str, str, dict)
    
    def __init__(self, resource_manager, parent=None):
        """
        Initialize the drag and drop canvas.
        
        Args:
            resource_manager: ResourceManager instance
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.resource_manager = resource_manager
        self.resources = []
        
        # Set up UI
        main_layout = QHBoxLayout(self)
        
        # Resource list panel
        resource_panel = QWidget()
        resource_layout = QVBoxLayout(resource_panel)
        
        resource_label = QLabel("Resources")
        resource_label.setFont(QFont("Arial", 12, QFont.Bold))
        resource_layout.addWidget(resource_label)
        
        self.resource_list = QListWidget()
        self.resource_list.setDragEnabled(True)
        
        # Load resource types
        aws_resources = self.resource_manager.get_resources_by_provider("aws")
        azure_resources = self.resource_manager.get_resources_by_provider("azurerm")
        
        # Add AWS resources
        aws_category = QListWidgetItem("AWS")
        aws_category.setFont(QFont("Arial", 10, QFont.Bold))
        aws_category.setFlags(Qt.NoItemFlags)
        aws_category.setBackground(QColor("#f0f0f0"))
        self.resource_list.addItem(aws_category)
        
        for resource_type in aws_resources:
            item = QListWidgetItem(resource_type)
            item.setData(Qt.UserRole, resource_type)
            self.resource_list.addItem(item)
        
        # Add Azure resources
        azure_category = QListWidgetItem("Azure")
        azure_category.setFont(QFont("Arial", 10, QFont.Bold))
        azure_category.setFlags(Qt.NoItemFlags)
        azure_category.setBackground(QColor("#f0f0f0"))
        self.resource_list.addItem(azure_category)
        
        for resource_type in azure_resources:
            item = QListWidgetItem(resource_type)
            item.setData(Qt.UserRole, resource_type)
            self.resource_list.addItem(item)
        
        resource_layout.addWidget(self.resource_list)
        
        # Canvas area
        canvas_container = QWidget()
        canvas_layout = QVBoxLayout(canvas_container)
        
        canvas_label = QLabel("Design Canvas")
        canvas_label.setFont(QFont("Arial", 12, QFont.Bold))
        canvas_layout.addWidget(canvas_label)
        
        # Use custom DropArea instead of regular QWidget
        self.canvas_area = DropArea(self)
        self.canvas_area.setMinimumSize(600, 400)
        self.canvas_area.setStyleSheet(
            "background-color: #f9f9f9; border: 1px dashed #cccccc;"
        )
        
        # Use a scroll area to allow scrolling if many resources are added
        scroll_area = QScrollArea()
        scroll_area.setWidget(self.canvas_area)
        scroll_area.setWidgetResizable(True)
        canvas_layout.addWidget(scroll_area)
        
        # Set canvas layout
        self.canvas_layout = QVBoxLayout(self.canvas_area)
        self.canvas_layout.setAlignment(Qt.AlignTop)
        
        # Connect resource list double-click event
        self.resource_list.itemDoubleClicked.connect(self.handle_double_click)
        
        # Add panels to main layout
        main_layout.addWidget(resource_panel, 1)
        main_layout.addWidget(canvas_container, 3)
    
    def handle_double_click(self, item):
        """Handle double-click on resource list items."""
        if item.data(Qt.UserRole):  # Ensure item has resource_type data
            resource_type = item.data(Qt.UserRole)
            self.add_resource(resource_type, f"{resource_type.split('_')[-1]}_{len(self.resources)}")
    
    def add_resource(self, resource_type, resource_name):
        """
        Add a resource to the canvas.
        
        Args:
            resource_type: Type of resource
            resource_name: Name for the resource
        """
        resource_item = ResourceItem(resource_type, resource_name, self)
        
        # Get default configuration from the resource manager
        template = self.resource_manager.get_resource_template(resource_type)
        if template and "defaults" in template:
            resource_item.config = template["defaults"].copy()
        
        self.canvas_layout.addWidget(resource_item)
        self.resources.append(resource_item)
        
        # Select the newly added resource
        self.resource_selected.emit(resource_type, resource_name, resource_item.config)
    
    def remove_resource(self, resource_item):
        """
        Remove a resource from the canvas.
        
        Args:
            resource_item: ResourceItem to remove
        """
        self.canvas_layout.removeWidget(resource_item)
        self.resources.remove(resource_item)
        resource_item.deleteLater()
    
    def get_resources(self):
        """
        Get all resources on the canvas.
        
        Returns:
            List of resource dictionaries
        """
        result = []
        
        for resource in self.resources:
            result.append({
                "type": resource.resource_type,
                "name": resource.resource_name,
                "config": resource.config
            })
        
        return result