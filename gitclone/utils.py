"""
Utility functions for GitClonePro
"""

import os
import re
from pathlib import Path
from typing import Optional, Dict, Any

def expand_path(path: str) -> str:
    """
    Expand user home directory and environment variables

    Args:
        path: Path string

    Returns:
        Expanded path
    """
    if not path:
        return path

    # Expand ~
    path = os.path.expanduser(path)

    # Expand environment variables
    path = os.path.expandvars(path)

    # Convert to absolute path
    return os.path.abspath(path)

def validate_url(url: str) -> bool:
    """
    Validate GitHub repository URL

    Args:
        url: URL to validate

    Returns:
        True if valid
    """
    if not url:
        return False

    # Check for git@ or https://
    if not (url.startswith("https://") or url.startswith("git@")):
        return False

    # Check for github.com
    if "github.com" not in url:
        return False

    # Check for at least user/repo
    if not re.search(r"github\.com[/:][\w\-]+/[\w\-]+", url):
        return False

    return True

def get_repo_name(url: str) -> str:
    """
    Extract repository name from URL

    Args:
        url: GitHub URL

    Returns:
        Repository name
    """
    # Remove .git suffix
    url = url.rstrip('/')
    if url.endswith('.git'):
        url = url[:-4]

    # Extract last part
    return url.split('/')[-1]

def get_owner_and_repo(url: str) -> tuple:
    """
    Extract owner and repository name from URL

    Args:
        url: GitHub URL

    Returns:
        (owner, repo) or (None, None)
    """
    # Remove .git suffix
    url = url.rstrip('/')
    if url.endswith('.git'):
        url = url[:-4]

    # For HTTPS
    if url.startswith("https://"):
        parts = url.replace("https://", "").split("/")
        if len(parts) >= 3 and parts[0] == "github.com":
            return parts[1], parts[2]

    # For SSH
    if url.startswith("git@"):
        parts = url.replace("git@", "").split(":")
        if len(parts) >= 2:
            repo_parts = parts[1].split("/")
            if len(repo_parts) >= 2:
                return repo_parts[0], repo_parts[1]

    return None, None