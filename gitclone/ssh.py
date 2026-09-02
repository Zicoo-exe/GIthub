"""
SSH key management for GitClonePro
"""

import os
import subprocess
from pathlib import Path
from typing import Optional, List

from .logger import log

class SSHManager:
    """Manage SSH keys and connections for Git operations"""
    
    def __init__(self, key_path: Optional[str] = None):
        """
        Initialize SSH manager
        
        Args:
            key_path: Path to SSH private key (default: ~/.ssh/id_rsa)
        """
        if key_path:
            self.key_path = Path(key_path).expanduser()
        else:
            self.key_path = Path.home() / ".ssh" / "id_rsa"
            
        self.public_key_path = self.key_path.with_suffix(".pub")
        
    def key_exists(self) -> bool:
        """Check if SSH key exists"""
        return self.key_path.exists() and self.public_key_path.exists()
        
    def generate_key(self, comment: str = "gitclone@user") -> bool:
        """
        Generate a new SSH key pair
        
        Args:
            comment: Comment for the key
            
        Returns:
            True if successful
        """
        if self.key_exists():
            log(f"[!] SSH key already exists: {self.key_path}", "WARNING")
            return True
            
        log(f"[*] Generating SSH key: {self.key_path}", "INFO")
        
        # Create .ssh directory
        self.key_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Generate key
        cmd = [
            "ssh-keygen",
            "-t", "rsa",
            "-b", "4096",
            "-C", comment,
            "-f", str(self.key_path),
            "-N", ""  # No passphrase
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            log(f"[+] SSH key generated: {self.key_path}", "SUCCESS")
            return True
        except subprocess.CalledProcessError as e:
            log(f"[!] Failed to generate SSH key: {e.stderr}", "ERROR")
            return False
            
    def get_public_key(self) -> Optional[str]:
        """
        Get public key content
        
        Returns:
            Public key as string or None
        """
        if not self.public_key_path.exists():
            log(f"[!] Public key not found: {self.public_key_path}", "ERROR")
            return None
            
        with open(self.public_key_path, 'r') as f:
            return f.read().strip()
            
    def add_to_ssh_agent(self) -> bool:
        """
        Add key to SSH agent
        
        Returns:
            True if successful
        """
        if not self.key_exists():
            log("[!] SSH key not found", "ERROR")
            return False
            
        # Check if agent is running
        try:
            subprocess.run(["ssh-add", "-l"], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            log("[!] SSH agent not running or key not added", "WARNING")
            # Try to start agent
            try:
                subprocess.run(["eval", "$(ssh-agent)"], shell=True, check=True)
            except:
                pass
                
        # Add key
        try:
            subprocess.run(["ssh-add", str(self.key_path)], check=True, capture_output=True)
            log(f"[+] SSH key added to agent: {self.key_path}", "SUCCESS")
            return True
        except subprocess.CalledProcessError as e:
            log(f"[!] Failed to add key to agent: {e.stderr}", "ERROR")
            return False
            
    def test_connection(self, host: str = "github.com") -> bool:
        """
        Test SSH connection to GitHub
        
        Args:
            host: Host to connect to
            
        Returns:
            True if connection successful
        """
        log(f"[*] Testing SSH connection to {host}...", "INFO")
        
        cmd = ["ssh", "-T", f"git@{host}", "-o", "StrictHostKeyChecking=no"]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if "successfully authenticated" in result.stdout or "successfully authenticated" in result.stderr:
                log("[+] SSH connection successful", "SUCCESS")
                return True
            elif "Permission denied" in result.stderr:
                log("[!] SSH permission denied - check your GitHub SSH keys", "ERROR")
                return False
            else:
                log(f"[!] SSH connection failed: {result.stderr}", "ERROR")
                return False
        except subprocess.TimeoutExpired:
            log("[!] SSH connection timed out", "ERROR")
            return False
        except FileNotFoundError:
            log("[!] SSH command not found - is SSH installed?", "ERROR")
            return False
            
    def setup_github_ssh(self, token: Optional[str] = None) -> bool:
        """
        Setup SSH for GitHub (generate key and add to GitHub)
        
        Args:
            token: GitHub token for API access
            
        Returns:
            True if successful
        """
        # Generate key if needed
        if not self.key_exists():
            if not self.generate_key():
                return False
                
        # Add to SSH agent
        if not self.add_to_ssh_agent():
            log("[!] Could not add key to SSH agent - continuing anyway", "WARNING")
            
        # Test connection
        if self.test_connection():
            return True
            
        # If test fails, try to add public key to GitHub
        if token:
            log("[*] Adding public key to GitHub...", "INFO")
            
            public_key = self.get_public_key()
            if not public_key:
                return False
                
            # Use GitHub API to add key
            import json
            import urllib.request
            from urllib.request import Request, urlopen
            from urllib.error import HTTPError
            
            url = "https://api.github.com/user/keys"
            headers = {
                "Authorization": f"token {token}",
                "Accept": "application/vnd.github.v3+json",
                "Content-Type": "application/json",
            }
            
            data = json.dumps({
                "title": f"GitClonePro ({os.uname().nodename})",
                "key": public_key
            }).encode()
            
            request = Request(url, data=data, headers=headers, method="POST")
            
            try:
                with urlopen(request) as response:
                    log("[+] SSH key added to GitHub successfully", "SUCCESS")
                    return True
            except HTTPError as e:
                log(f"[!] Failed to add SSH key: {e.code} - {e.reason}", "ERROR")
                return False
        else:
            log("[!] SSH connection failed. Add your public key to GitHub:", "ERROR")
            print("\n" + "="*60)
            print("Add this public key to GitHub:")
            print("-"*60)
            print(self.get_public_key() or "No public key found")
            print("="*60 + "\n")
            return False