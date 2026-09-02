"""
GitHub API interaction layer
"""

import json
import time
from typing import Optional, List, Dict, Any
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode

from .logger import log

class GitHubAPI:
    """GitHub API client with rate limit handling"""

    BASE_URL = "https://api.github.com"

    def __init__(self, token: Optional[str] = None, timeout: int = 30):
        """
        Initialize GitHub API client

        Args:
            token: GitHub Personal Access Token
            timeout: Request timeout in seconds
        """
        self.token = token
        self.timeout = timeout
        self.rate_limit_remaining = None
        self.rate_limit_reset = None

    def _request(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """
        Make a request to the GitHub API

        Args:
            endpoint: API endpoint (e.g., /users/octocat/repos)
            params: Query parameters

        Returns:
            Parsed JSON response or None
        """
        url = f"{self.BASE_URL}{endpoint}"

        if params:
            url += "?" + urlencode(params)

        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "GitClonePro/2.0"
        }

        if self.token:
            headers["Authorization"] = f"token {self.token}"

        request = Request(url, headers=headers)

        try:
            log(f"[API] GET {endpoint}", "DEBUG")
            with urlopen(request, timeout=self.timeout) as response:
                # Parse rate limit headers
                self.rate_limit_remaining = int(
                    response.headers.get("X-RateLimit-Remaining", "0")
                )
                self.rate_limit_reset = int(
                    response.headers.get("X-RateLimit-Reset", "0")
                )

                if self.rate_limit_remaining < 10:
                    log(f"[!] Rate limit low: {self.rate_limit_remaining} remaining", "WARNING")

                data = response.read().decode()
                return json.loads(data)

        except HTTPError as e:
            if e.code == 403 and "rate limit" in str(e):
                reset_time = int(e.headers.get("X-RateLimit-Reset", "0"))
                wait_time = max(0, reset_time - time.time()) + 5
                log(f"[!] Rate limit exceeded. Waiting {wait_time:.0f} seconds...", "ERROR")
                time.sleep(wait_time)
                return self._request(endpoint, params)

            log(f"[API] HTTP Error {e.code}: {e.reason}", "ERROR")
            return None

        except URLError as e:
            log(f"[API] Connection error: {e.reason}", "ERROR")
            return None

        except json.JSONDecodeError as e:
            log(f"[API] Invalid JSON response: {e}", "ERROR")
            return None

    def get_repos(
        self,
        owner: str,
        repo_type: str = "all",
        include_forks: bool = False,
        per_page: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get all repositories for a user or organization

        Args:
            owner: GitHub username or organization
            repo_type: Type filter (all, public, private, forks, sources)
            include_forks: Include forked repositories
            per_page: Results per page (max 100)

        Returns:
            List of repository objects
        """
        repos = []
        page = 1

        # Determine endpoint
        if self._is_organization(owner):
            endpoint = f"/orgs/{owner}/repos"
        else:
            endpoint = f"/users/{owner}/repos"

        while True:
            params = {
                "page": page,
                "per_page": per_page,
                "type": repo_type if repo_type != "all" else "all"
            }

            data = self._request(endpoint, params)

            if not data:
                break

            # Filter forks if needed
            if not include_forks:
                data = [r for r in data if not r.get("fork", False)]

            repos.extend(data)

            if len(data) < per_page:
                break

            page += 1

        # Additional filtering
        if repo_type == "private":
            repos = [r for r in repos if r.get("private", False)]
        elif repo_type == "public":
            repos = [r for r in repos if not r.get("private", False)]
        elif repo_type == "sources":
            repos = [r for r in repos if not r.get("fork", False) and not r.get("private", False)]

        log(f"[API] Found {len(repos)} repositories for {owner}", "INFO")
        return repos

    def _is_organization(self, name: str) -> bool:
        """
        Check if a name is an organization

        Args:
            name: GitHub username or organization name

        Returns:
            True if organization, False if user
        """
        # Try to get user info
        user_data = self._request(f"/users/{name}")
        if user_data and user_data.get("type") == "Organization":
            return True
        return False

    def get_repo(self, owner: str, repo: str) -> Optional[Dict[str, Any]]:
        """
        Get a single repository

        Args:
            owner: Repository owner
            repo: Repository name

        Returns:
            Repository object or None
        """
        return self._request(f"/repos/{owner}/{repo}")

    def check_rate_limit(self) -> Dict[str, int]:
        """
        Check current rate limit status

        Returns:
            Dictionary with remaining and reset time
        """
        data = self._request("/rate_limit")
        if data:
            return {
                "remaining": data.get("resources", {}).get("core", {}).get("remaining", 0),
                "reset": data.get("resources", {}).get("core", {}).get("reset", 0)
            }
        return {"remaining": 0, "reset": 0}