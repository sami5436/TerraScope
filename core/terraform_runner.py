# core/terraform_runner.py
"""
TerraformRunner executes terraform commands on generated infrastructure code.
"""
import subprocess
import os
import logging
from typing import Dict, List, Tuple, Optional

logger = logging.getLogger(__name__)

class TerraformRunner:
    """Handles execution of Terraform CLI commands."""
    
    def __init__(self, working_dir: str = "output"):
        """
        Initialize the TerraformRunner.
        
        Args:
            working_dir: Directory where Terraform commands will be executed
        """
        self.working_dir = working_dir
        self._ensure_dir_exists()
    
    def _ensure_dir_exists(self) -> None:
        """Ensure the working directory exists."""
        os.makedirs(self.working_dir, exist_ok=True)
    
    def run_command(self, command: List[str]) -> Tuple[int, str, str]:
        """
        Run a Terraform command.
        
        Args:
            command: List of command parts (e.g., ["init", "-no-color"])
            
        Returns:
            Tuple of (return_code, stdout, stderr)
        """
        full_command = ["terraform"] + command
        logger.info(f"Running: {' '.join(full_command)}")
        
        try:
            process = subprocess.Popen(
                full_command,
                cwd=self.working_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = process.communicate()
            return_code = process.returncode
            
            if return_code == 0:
                logger.info(f"Command completed successfully")
            else:
                logger.error(f"Command failed with code {return_code}")
                
            return return_code, stdout, stderr
        except Exception as e:
            logger.error(f"Error running Terraform command: {e}")
            return 1, "", str(e)
    
    def init(self) -> Tuple[bool, str]:
        """
        Run terraform init.
        
        Returns:
            Tuple of (success, message)
        """
        code, stdout, stderr = self.run_command(["init", "-no-color"])
        return code == 0, stdout if code == 0 else stderr
    
    def plan(self) -> Tuple[bool, str]:
        """
        Run terraform plan.
        
        Returns:
            Tuple of (success, message)
        """
        code, stdout, stderr = self.run_command(["plan", "-no-color"])
        return code == 0, stdout if code == 0 else stderr
    
    def apply(self, auto_approve: bool = False) -> Tuple[bool, str]:
        """
        Run terraform apply.
        
        Args:
            auto_approve: Whether to automatically approve the apply
            
        Returns:
            Tuple of (success, message)
        """
        command = ["apply", "-no-color"]
        if auto_approve:
            command.append("-auto-approve")
            
        code, stdout, stderr = self.run_command(command)
        return code == 0, stdout if code == 0 else stderr
    
    def destroy(self, auto_approve: bool = False) -> Tuple[bool, str]:
        """
        Run terraform destroy.
        
        Args:
            auto_approve: Whether to automatically approve the destroy
            
        Returns:
            Tuple of (success, message)
        """
        command = ["destroy", "-no-color"]
        if auto_approve:
            command.append("-auto-approve")
            
        code, stdout, stderr = self.run_command(command)
        return code == 0, stdout if code == 0 else stderr
