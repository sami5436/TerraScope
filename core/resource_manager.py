# core/resource_manager.py
"""
ResourceManager handles loading, validation, and management of
infrastructure resources from templates.
"""
import json
import os
from typing import Dict, List, Any, Optional

class ResourceManager:
    """creating a new class that Manages infrastructure resources and their templates."""
    
    # kinda like the constructors in the original code, but this is a class that manages resources.
    def __init__(self, resources_path: str = "data/resources.json"):
        """
        Initialize the ResourceManager.
        
        Args:
            resources_path: Path to the JSON file containing resource templates
        """
        
        self.resources_path = resources_path # Path to the JSON file
        self.resources: Dict[str, Dict] = {} # Dictionary to hold resource templates
        self.load_resources() # Load resources from the JSON file
    
    def load_resources(self) -> None:
        """Load resources from the JSON template file."""
        try:
            with open(self.resources_path, 'r') as f:
                self.resources = json.load(f) # Load JSON data
                print(f"Loaded {len(self.resources)} resource types") # counts how many resources were loaded
        except Exception as e:
            print(f"Error loading resources: {e}")
            self.resources = {}
    
    def get_resource_template(self, resource_type: str) -> Optional[Dict]:
        """
        Get the template for a specific resource type.
        
        Args:
            resource_type: The type of resource to retrieve
            
        Returns:
            Resource template dictionary or None if not found
        """
        return self.resources.get(resource_type)
    
    def get_resource_groups(self) -> List[str]:
        """
        Get available resource groups (e.g., AWS, Azure).
        
        Returns:
            List of resource group names
        """
        groups = set() 
        for resource in self.resources.values(): # Iterate through all resources
            if "provider" in resource: # Check if the resource has a provider
                groups.add(resource["provider"]) # Add the provider to the set
        return list(groups) 
    
    def get_resources_by_provider(self, provider: str) -> Dict[str, Dict]:
        """
        Get resources filtered by provider.
        
        Args:
            provider: Provider name (e.g., "aws", "azure")
            
        Returns:
            Dictionary of resources for the specified provider
        """
        return {
            k: v for k, v in self.resources.items()  
            if v.get("provider", "").lower() == provider.lower()
            # Filter resources by provider
        }
    
    def get_popular_resources(self, limit: int = 10) -> List[str]:
        """
        Get the most popular resources based on metadata.
        
        Args:
            limit: Maximum number of resources to return
            
        Returns:
            List of popular resource type names
        """
        popular = [k for k, v in self.resources.items() if v.get("popular", False)]
        return popular[:limit]