"""
Core functionality for GitClonePro
"""

import os
import sys
import yaml
from pathlib import Path
from typing import Optional, List, Dict, Any

from .api import GitHubAPI
from .clone import clone_repo, batch_clone, sparse_clone
from .utils import load_config, expand_path, validate_url
from .logger import log

class GitClonePro:
    """Main class for GitClonePro"""

    def __init__(
        self,
        config_path: Optional[str] = None,
        token: Optional[str] = None,
        use_ssh: bool = False,
        verbose: bool = True,
        quiet: bool = False
    ):
        """
        Initialize GitClonePro with configuration

        Args:
            config_path: Path to YAML config file
            token: GitHub Personal Access Token
            use_ssh: Use SSH instead of HTTPS
            verbose: Enable verbose output
            quiet: Suppress all output
        """
        self.verbose = verbose and not quiet
        self.quiet = quiet
        self.use_ssh = use_ssh

        # Load configuration
        self.config = self._load_config(config_path)

        # Override with provided values
        if token:
            self.config["github_token"] = token
        if use_ssh:
            self.config["use_ssh"] = True

        # Validate token
        if self.config.get("github_token"):
            log("[+] GitHub token loaded", "DEBUG")
        else:
            log("[!] No GitHub token provided - rate limits will apply", "WARNING")

        # Initialize GitHub API
        self.api = GitHubAPI(
            token=self.config.get("github_token"),
            timeout=self.config.get("timeout", 30)
        )

        # Set default clone directory
        self.clone_dir = expand_path(
            self.config.get("clone_dir", os.getcwd())
        )

        log(f"[+] Clone directory: {self.clone_dir}", "DEBUG")

    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load configuration from file and defaults"""
        config = {
            "github_token": "",
            "clone_dir": "~/git_clones",
            "default_branch": "main",
            "retries": 3,
            "threads": 4,
            "timeout": 30,
            "verbose": True,
            "log_file": "~/.gitclone.log",
            "log_level": "INFO",
            "use_ssh": False,
            "validate_certificates": True,
        }

        # Try to load from specified path
        if config_path:
            config_path = expand_path(config_path)
            if Path(config_path).exists():
                with open(config_path, 'r') as f:
                    user_config = yaml.safe_load(f)
                    config.update(user_config)
                log(f"[+] Loaded config from {config_path}", "DEBUG")
            else:
                log(f"[!] Config file not found: {config_path}", "WARNING")

        # Try default locations
        else:
            default_paths = [
                Path.cwd() / "config.yaml",
                Path.cwd() / "config.yml",
                Path.home() / ".gitclone_config.yaml",
                Path.home() / ".config/gitclone/config.yaml",
                Path("/etc/gitclone/config.yaml"),
            ]

            for path in default_paths:
                if path.exists():
                    with open(path, 'r') as f:
                        user_config = yaml.safe_load(f)
                        config.update(user_config)
                    log(f"[+] Loaded config from {path}", "DEBUG")
                    break

        # Environment variable override
        if os.environ.get("GITHUB_TOKEN"):
            config["github_token"] = os.environ["GITHUB_TOKEN"]
            log("[+] Using GITHUB_TOKEN from environment", "DEBUG")

        return config

    def clone_single(
        self,
        url: str,
        dest: Optional[str] = None,
        branch: Optional[str] = None,
        depth: Optional[int] = None,
        mirror: bool = False,
        sparse: Optional[List[str]] = None,
        exclude: Optional[List[str]] = None
    ) -> bool:
        """
        Clone a single repository

        Args:
            url: GitHub repository URL
            dest: Destination directory
            branch: Branch to clone
            depth: Shallow clone depth
            mirror: Clone as mirror
            sparse: List of files/folders to clone
            exclude: List of files/folders to exclude

        Returns:
            True if successful, False otherwise
        """
        # Validate URL
        if not validate_url(url):
            log(f"[!] Invalid URL: {url}", "ERROR")
            return False

        # Set defaults
        if not branch:
            branch = self.config.get("default_branch", "main")

        if not dest:
            # Extract repo name from URL
            repo_name = url.rstrip('/').split('/')[-1]
            if repo_name.endswith('.git'):
                repo_name = repo_name[:-4]
            dest = str(Path(self.clone_dir) / repo_name)

        dest = expand_path(dest)

        # Convert to SSH if requested
        if self.use_ssh and "https://github.com/" in url:
            url = url.replace("https://github.com/", "git@github.com:")
            if not url.endswith('.git'):
                url += '.git'

        # Embed token if provided and using HTTPS
        token = self.config.get("github_token")
        if token and "https://" in url and "@" not in url:
            url = url.replace("https://", f"https://{token}@")

        # Handle sparse clone
        if sparse:
            log(f"[*] Sparse cloning: {', '.join(sparse)}", "INFO")
            return sparse_clone(
                repo_url=url,
                dest_dir=dest,
                paths=sparse,
                branch=branch,
                depth=depth,
                token=token,
                retries=self.config.get("retries", 3)
            )

        # Standard clone
        return clone_repo(
            repo_url=url,
            dest_dir=dest,
            branch=branch,
            depth=depth,
            mirror=mirror,
            token=token,
            retries=self.config.get("retries", 3)
        )

    def batch_clone(
        self,
        owner: str,
        dest: Optional[str] = None,
        repo_type: str = "all",
        include_forks: bool = False,
        threads: Optional[int] = None,
        depth: Optional[int] = None,
        mirror: bool = False,
        branch: Optional[str] = None,
        exclude: Optional[List[str]] = None
    ) -> bool:
        """
        Clone all repositories from a user or organization

        Args:
            owner: GitHub username or organization
            dest: Destination directory
            repo_type: Type of repositories to clone
            include_forks: Include forked repositories
            threads: Number of parallel threads
            depth: Shallow clone depth
            mirror: Clone as mirror
            branch: Branch to clone
            exclude: List of files/folders to exclude

        Returns:
            True if successful, False otherwise
        """
        if not dest:
            dest = str(Path(self.clone_dir) / owner)

        dest = expand_path(dest)

        if not threads:
            threads = self.config.get("threads", 4)

        if not branch:
            branch = self.config.get("default_branch", "main")

        token = self.config.get("github_token")

        log(f"[*] Batch cloning {owner} (type: {repo_type}, threads: {threads})", "INFO")

        return batch_clone(
            owner=owner,
            dest_dir=dest,
            repo_type=repo_type,
            include_forks=include_forks,
            token=token,
            threads=threads,
            depth=depth,
            mirror=mirror,
            branch=branch,
            exclude=exclude,
            use_ssh=self.use_ssh,
            retries=self.config.get("retries", 3)
        )