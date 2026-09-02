"""
GitClonePro - Universal GitHub Clone Tool
Author: KL__Zicoo
License: MIT
"""

__version__ = "2.0.0"
__author__ = "KL__Zicoo"
__license__ = "MIT"
__description__ = "Advanced GitHub clone tool with sparse, batch, mirror, and parallel support"

from .core import GitClonePro
from .clone import clone_repo, batch_clone, sparse_clone
from .api import GitHubAPI
from .utils import validate_url, get_repo_name, get_owner_and_repo, expand_path
from .logger import setup_logger, get_logger, log

__all__ = [
    # Main class
    "GitClonePro",
    # Functions
    "clone_repo",
    "batch_clone", 
    "sparse_clone",
    "validate_url",
    "get_repo_name",
    "get_owner_and_repo",
    "expand_path",
    # API
    "GitHubAPI",
    # Logging
    "setup_logger",
    "get_logger",
    "log",
    # Metadata
    "__version__",
    "__author__",
    "__license__",
    "__description__",
]