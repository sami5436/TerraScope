"""
Core initialization module for TerraScope.
Handles package initialization and configuration.
"""
import os
import sys
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("output/terraform.log", mode='a'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def initialize_app():
    """Initialize the application and verify dependencies."""
    logger.info("Initializing TerraScope application...")
    
    # Check for Terraform installation
    try:
        import subprocess
        result = subprocess.run(['terraform', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            logger.info(f"Terraform detected: {result.stdout.splitlines()[0]}")
        else:
            logger.warning("Terraform not found in PATH. Some features may not work.")
    except Exception as e:
        logger.warning(f"Error checking Terraform: {e}")
    
    # Add project root to path
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if project_root not in sys.path:
        sys.path.append(project_root)
    
    logger.info("Initialization complete")