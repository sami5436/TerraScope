"""
Automated test suite for ResourceManager using pytest
Run with: pytest test_resource_manager_pytest.py -v
"""

import pytest
import json
import os
import tempfile
from pathlib import Path

# Setup necessary directories before importing core modules
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
output_dir = os.path.join(project_root, "output")
os.makedirs(output_dir, exist_ok=True)

# Import the ResourceManager
import sys
sys.path.insert(0, project_root)
from core.resource_manager import ResourceManager


@pytest.fixture
def resources_json():
    """Fixture that provides the actual resources.json content"""
    return {
        "aws_s3_bucket": {
            "provider": "aws",
            "defaults": {
                "bucket": "my-terraform-bucket",
                "acl": "private",
                "tags": {
                    "Environment": "Dev",
                    "CreatedBy": "Terrascope"
                }
            },
            "required_fields": ["bucket"],
            "popular": True,
            "description": "AWS S3 Bucket for object storage"
        },
        "aws_instance": {
            "provider": "aws",
            "defaults": {
                "ami": "ami-0c55b159cbfafe1f0",
                "instance_type": "t2.micro",
                "tags": {
                    "Name": "TerrascopeInstance",
                    "Environment": "Dev"
                }
            },
            "required_fields": ["ami", "instance_type"],
            "popular": True,
            "description": "AWS EC2 Instance"
        },
        "azurerm_resource_group": {
            "provider": "azurerm",
            "defaults": {
                "name": "terrascope-resources",
                "location": "East US",
                "tags": {
                    "environment": "dev"
                }
            },
            "required_fields": ["name", "location"],
            "popular": True,
            "description": "Azure Resource Group"
        }
    }

# unit tests follow the AAA pattern

@pytest.fixture
def temp_resources_file(resources_json):
    """Create a temporary resources.json file for testing"""
    # Arrange: Create a temporary file with the JSON content
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(resources_json, f)
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    os.unlink(temp_path)


@pytest.fixture
def resource_manager(temp_resources_file):
    """Create a ResourceManager instance with test data"""
    # Act: Initialize ResourceManager with the temporary file
    return ResourceManager(resources_path=temp_resources_file)


class TestResourceManager:
    """Test suite for ResourceManager"""
    # Assertions are made in each test method: outcome of the action matches your expectations. 
    def test_initialization(self, resource_manager):
        """Test that ResourceManager initializes correctly"""
        assert resource_manager is not None # Check if the instance is created
        assert isinstance(resource_manager.resources, dict) # Check if resources is a dictionary
        assert len(resource_manager.resources) > 0 # Check if resources are loaded
    
    # Test loading resources from JSON file
    def test_load_resources(self, resource_manager):
        """Test loading resources from JSON file"""
        assert len(resource_manager.resources) == 3 # Check if the correct number of resources are loaded
        assert "aws_s3_bucket" in resource_manager.resources # Check if specific resources are loaded
        assert "aws_instance" in resource_manager.resources # Check if specific resources are loaded
        assert "azurerm_resource_group" in resource_manager.resources
    
    # Test getting specific resource templates
    def test_get_resource_template(self, resource_manager):
        """Test getting specific resource templates"""
        # Test existing resource
        s3_template = resource_manager.get_resource_template("aws_s3_bucket") # Get the S3 bucket template
        assert s3_template is not None # Check if the template is not None
        assert s3_template["provider"] == "aws" # Check if the provider is AWS
        assert "defaults" in s3_template # Check if defaults are present
        assert s3_template["defaults"]["bucket"] == "my-terraform-bucket" # Check if the default bucket name is correct
        
        # Test non-existent resource
        non_existent = resource_manager.get_resource_template("fake_resource")
        assert non_existent is None # Check if the non-existent resource returns None
    
    def test_get_resources_by_provider(self, resource_manager):
        """Test filtering resources by provider"""
        # Test AWS resources
        aws_resources = resource_manager.get_resources_by_provider("aws")
        assert len(aws_resources) == 2
        assert "aws_s3_bucket" in aws_resources
        assert "aws_instance" in aws_resources
        assert "azurerm_resource_group" not in aws_resources
        
        # Test Azure resources
        azure_resources = resource_manager.get_resources_by_provider("azurerm")
        assert len(azure_resources) == 1
        assert "azurerm_resource_group" in azure_resources
        assert "aws_s3_bucket" not in azure_resources
        
        # Test non-existent provider
        fake_resources = resource_manager.get_resources_by_provider("fake_provider")
        assert len(fake_resources) == 0
    
    def test_get_resource_groups(self, resource_manager):
        """Test getting available resource groups/providers"""
        groups = resource_manager.get_resource_groups()
        assert len(groups) == 2
        assert "aws" in groups
        assert "azurerm" in groups
    
    def test_get_popular_resources(self, resource_manager):
        """Test getting popular resources"""
        # All resources in test data are popular
        popular = resource_manager.get_popular_resources()
        assert len(popular) == 3
        
        # Test limit
        popular_limited = resource_manager.get_popular_resources(limit=2)
        assert len(popular_limited) == 2
    
    def test_resource_structure(self, resource_manager):
        """Test the structure of loaded resources"""
        for resource_type, resource in resource_manager.resources.items():
            # Every resource should have these fields
            assert "provider" in resource
            assert "defaults" in resource
            assert "required_fields" in resource
            assert "popular" in resource
            assert "description" in resource
            
            # Test types
            assert isinstance(resource["provider"], str)
            assert isinstance(resource["defaults"], dict)
            assert isinstance(resource["required_fields"], list)
            assert isinstance(resource["popular"], bool)
            assert isinstance(resource["description"], str)
    
    def test_required_fields(self, resource_manager):
        """Test required fields are properly loaded"""
        s3_template = resource_manager.get_resource_template("aws_s3_bucket")
        assert s3_template["required_fields"] == ["bucket"]
        
        ec2_template = resource_manager.get_resource_template("aws_instance")
        assert set(ec2_template["required_fields"]) == {"ami", "instance_type"}
        
        rg_template = resource_manager.get_resource_template("azurerm_resource_group")
        assert set(rg_template["required_fields"]) == {"name", "location"}
    
    def test_resource_defaults(self, resource_manager):
        """Test default values are properly loaded"""
        s3_template = resource_manager.get_resource_template("aws_s3_bucket")
        defaults = s3_template["defaults"]
        assert defaults["bucket"] == "my-terraform-bucket"
        assert defaults["acl"] == "private"
        assert "tags" in defaults
        assert defaults["tags"]["Environment"] == "Dev"
    
    
    def test_empty_json(self):
        """Test behavior with empty JSON file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({}, f)
            temp_path = f.name
        
        try:
            rm = ResourceManager(resources_path=temp_path)
            assert len(rm.resources) == 0
            assert rm.get_resource_template("any_resource") is None
            assert len(rm.get_resources_by_provider("any_provider")) == 0
            assert len(rm.get_resource_groups()) == 0
            assert len(rm.get_popular_resources()) == 0
        finally:
            os.unlink(temp_path)


@pytest.mark.parametrize("resource_type,expected_provider", [
    ("aws_s3_bucket", "aws"),
    ("aws_instance", "aws"),
    ("azurerm_resource_group", "azurerm"),
])
def test_resource_provider_mapping(resource_manager, resource_type, expected_provider):
    """Parametrized test for resource-provider mapping"""
    resource = resource_manager.get_resource_template(resource_type)
    assert resource["provider"] == expected_provider


@pytest.mark.parametrize("provider,expected_count", [
    ("aws", 2),
    ("azurerm", 1),
    ("gcp", 0),
])
def test_provider_resource_count(resource_manager, provider, expected_count):
    """Parametrized test for resource counts by provider"""
    resources = resource_manager.get_resources_by_provider(provider)
    assert len(resources) == expected_count


# Integration tests
class TestResourceManagerIntegration:
    """Integration tests using the full resources.json file"""
    
    @pytest.fixture
    def full_resource_manager(self):
        """Create ResourceManager with the actual resources.json file"""
        # Assuming the actual resources.json exists in data/resources.json
        if not os.path.exists("data/resources.json"):
            pytest.skip("data/resources.json not found")
        return ResourceManager()
    
    def test_aws_resource_count(self, full_resource_manager):
        """Test the number of AWS resources in the full file"""
        aws_resources = full_resource_manager.get_resources_by_provider("aws")
        assert len(aws_resources) >= 10  # Based on your provided JSON
    
    def test_azure_resource_count(self, full_resource_manager):
        """Test the number of Azure resources in the full file"""
        azure_resources = full_resource_manager.get_resources_by_provider("azurerm")
        assert len(azure_resources) >= 10  # Based on your provided JSON
    
    def test_all_resources_have_required_structure(self, full_resource_manager):
        """Test that all resources have the required structure"""
        for resource_type, resource in full_resource_manager.resources.items():
            assert "provider" in resource, f"{resource_type} missing provider"
            assert "defaults" in resource, f"{resource_type} missing defaults"
            assert "required_fields" in resource, f"{resource_type} missing required_fields"
            assert "popular" in resource, f"{resource_type} missing popular"
            assert "description" in resource, f"{resource_type} missing description"
    
    def test_popular_resources_mix(self, full_resource_manager):
        """Test that popular resources include both AWS and Azure"""
        popular = full_resource_manager.get_popular_resources()
        providers = {full_resource_manager.resources[r]["provider"] for r in popular}
        assert "aws" in providers
        assert "azurerm" in providers


if __name__ == "__main__":
    # Run with pytest
    pytest.main([__file__, "-v"])