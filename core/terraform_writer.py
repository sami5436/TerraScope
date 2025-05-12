# core/terraform_writer.py
"""
TerraformWriter generates HCL (HashiCorp Configuration Language) from 
resource templates and user configurations.
"""
import os
import json
from typing import Dict, List, Any, Optional

class TerraformWriter:
    """Generates Terraform HCL files from resource configurations."""
    
    def __init__(self, output_dir: str = "output"):
        """
        Initialize the TerraformWriter.
        
        Args:
            output_dir: Directory where Terraform files will be written
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def create_terraform_block(self, backend_type: Optional[str] = None, 
                               backend_config: Optional[Dict] = None) -> str:
        """
        Create the terraform {} configuration block.
        
        Args:
            backend_type: Type of backend (e.g., "s3", "azurerm")
            backend_config: Backend configuration parameters
            
        Returns:
            HCL string for the terraform block
        """
        terraform_block = "terraform {\n  required_version = \">= 1.0.0\"\n"
        
        if backend_type and backend_config:
            terraform_block += f"  backend \"{backend_type}\" {{\n"
            for key, value in backend_config.items():
                # Format the value based on type
                if isinstance(value, str):
                    terraform_block += f'    {key} = "{value}"\n'
                elif isinstance(value, bool):
                    terraform_block += f"    {key} = {str(value).lower()}\n"
                else:
                    terraform_block += f"    {key} = {value}\n"
            terraform_block += "  }\n"
        
        terraform_block += "}\n"
        return terraform_block
    
    def create_provider_block(self, provider: str, config: Dict) -> str:
        """
        Create a provider configuration block.
        
        Args:
            provider: Provider name (e.g., "aws", "azurerm")
            config: Provider configuration parameters
            
        Returns:
            HCL string for the provider block
        """
        provider_block = f'provider "{provider}" {{\n'
        
        for key, value in config.items():
            # Format the value based on type
            if isinstance(value, str):
                provider_block += f'  {key} = "{value}"\n'
            elif isinstance(value, bool):
                provider_block += f"  {key} = {str(value).lower()}\n"
            else:
                provider_block += f"  {key} = {value}\n"
        
        provider_block += "}\n"
        return provider_block
    
    def create_resource_block(self, resource_type: str, resource_name: str, 
                              config: Dict) -> str:
        """
        Create a resource configuration block.
        
        Args:
            resource_type: Type of resource (e.g., "aws_s3_bucket")
            resource_name: Name/identifier for the resource
            config: Resource configuration parameters
            
        Returns:
            HCL string for the resource block
        """
        # Sanitize resource name to be valid HCL identifier
        safe_name = resource_name.replace("-", "_").replace(" ", "_").lower()
        
        resource_block = f'resource "{resource_type}" "{safe_name}" {{\n'
        
        # Process nested configurations recursively
        for key, value in config.items():
            resource_block += self._format_attribute(key, value, indent=2)
        
        resource_block += "}\n"
        return resource_block
    
    def _format_attribute(self, key: str, value: Any, indent: int = 0) -> str:
        """
        Format a configuration attribute for HCL.
        
        Args:
            key: Attribute name
            value: Attribute value
            indent: Indentation level
            
        Returns:
            Formatted HCL string for the attribute
        """
        spaces = " " * indent
        
        if isinstance(value, dict):
            result = f"{spaces}{key} {{\n"
            for nested_key, nested_value in value.items():
                result += self._format_attribute(nested_key, nested_value, indent + 2)
            result += f"{spaces}}}\n"
            return result
        elif isinstance(value, list):
            if not value:
                return f"{spaces}{key} = []\n"
            
            if isinstance(value[0], dict):
                result = ""
                for item in value:
                    result += f"{spaces}{key} {{\n"
                    for nested_key, nested_value in item.items():
                        result += self._format_attribute(nested_key, nested_value, indent + 2)
                    result += f"{spaces}}}\n"
                return result
            else:
                formatted_items = []
                for item in value:
                    if isinstance(item, str):
                        formatted_items.append(f'"{item}"')
                    elif isinstance(item, bool):
                        formatted_items.append(str(item).lower())
                    else:
                        formatted_items.append(str(item))
                
                return f"{spaces}{key} = [{', '.join(formatted_items)}]\n"
        elif isinstance(value, str):
            # Check if the string is a reference (starts with var., local., etc.)
            if (value.startswith("var.") or value.startswith("local.") or 
                value.startswith("module.") or value.startswith("data.")):
                return f"{spaces}{key} = {value}\n"
            else:
                return f'{spaces}{key} = "{value}"\n'
        elif isinstance(value, bool):
            return f"{spaces}{key} = {str(value).lower()}\n"
        else:
            return f"{spaces}{key} = {value}\n"
    
    def write_terraform_file(self, filename: str, content: str) -> bool:
        """
        Write content to a Terraform file.
        
        Args:
            filename: Name of the file to write
            content: HCL content to write
            
        Returns:
            True if successful, False otherwise
        """
        try:
            file_path = os.path.join(self.output_dir, filename)
            with open(file_path, 'w') as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"Error writing file {filename}: {e}")
            return False
    
    def generate_main_tf(self, resources: List[Dict], 
                          providers: Dict[str, Dict] = None) -> bool:
        """
        Generate the main.tf file with resources and providers.
        
        Args:
            resources: List of resource configurations
            providers: Dictionary of provider configurations
            
        Returns:
            True if successful, False otherwise
        """
        content = ""
        
        # Add provider blocks
        if providers:
            for provider_name, provider_config in providers.items():
                content += self.create_provider_block(provider_name, provider_config)
                content += "\n"
        
        # Add resource blocks
        for resource in resources:
            content += self.create_resource_block(
                resource["type"], 
                resource["name"], 
                resource["config"]
            )
            content += "\n"
        
        return self.write_terraform_file("main.tf", content)
