#!/usr/bin/env python3
"""
Unit tests for GitHub API client
Tests all API interactions including:
- Repository listing
- Rate limit handling
- Error handling
- Pagination
- Authentication
"""

import unittest
import json
import time
from unittest.mock import patch, MagicMock
from urllib.error import HTTPError, URLError

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from gitclone.api import GitHubAPI
from gitclone.exceptions import RateLimitError, AuthenticationError


class TestGitHubAPI(unittest.TestCase):
    """Test GitHub API client functionality"""

    def setUp(self):
        """Set up test environment"""
        self.api = GitHubAPI(token="test_token_123")
        self.test_owner = "octocat"
        self.test_repo = "Hello-World"
        self.base_url = "https://api.github.com"

    def tearDown(self):
        """Clean up after tests"""
        pass

    # ==================== INITIALIZATION TESTS ====================

    def test_init_with_token(self):
        """Test API initialization with token"""
        api = GitHubAPI(token="test_token")
        self.assertEqual(api.token, "test_token")
        self.assertEqual(api.timeout, 30)

    def test_init_without_token(self):
        """Test API initialization without token"""
        api = GitHubAPI()
        self.assertIsNone(api.token)
        self.assertEqual(api.timeout, 30)

    def test_init_with_custom_timeout(self):
        """Test API initialization with custom timeout"""
        api = GitHubAPI(timeout=60)
        self.assertEqual(api.timeout, 60)

    # ==================== REQUEST TESTS ====================

    @patch('gitclone.api.urlopen')
    def test_request_success(self, mock_urlopen):
        """Test successful API request"""
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "id": 1,
            "name": "test",
            "full_name": "user/test"
        }).encode()
        mock_response.headers = {
            "X-RateLimit-Remaining": "5000",
            "X-RateLimit-Reset": "1234567890"
        }
        mock_urlopen.return_value.__enter__.return_value = mock_response

        result = self.api._request("/users/octocat")
        
        self.assertIsNotNone(result)
        self.assertEqual(result["id"], 1)
        self.assertEqual(result["name"], "test")
        self.assertEqual(self.api.rate_limit_remaining, 5000)

    @patch('gitclone.api.urlopen')
    def test_request_with_params(self, mock_urlopen):
        """Test API request with query parameters"""
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps([]).encode()
        mock_response.headers = {"X-RateLimit-Remaining": "5000"}
        mock_urlopen.return_value.__enter__.return_value = mock_response

        result = self.api._request("/users/octocat/repos", {"page": 1, "per_page": 10})
        
        self.assertIsNotNone(result)
        # Verify URL was called with params
        call_args = mock_urlopen.call_args[0][0].full_url
        self.assertIn("page=1", call_args)
        self.assertIn("per_page=10", call_args)

    @patch('gitclone.api.urlopen')
    def test_request_http_error(self, mock_urlopen):
        """Test API request with HTTP error"""
        error = HTTPError(
            url="https://api.github.com/users/octocat",
            code=404,
            msg="Not Found",
            hdrs={},
            fp=None
        )
        mock_urlopen.side_effect = error

        result = self.api._request("/users/octocat")
        self.assertIsNone(result)

    @patch('gitclone.api.urlopen')
    def test_request_connection_error(self, mock_urlopen):
        """Test API request with connection error"""
        mock_urlopen.side_effect = URLError("Connection refused")

        result = self.api._request("/users/octocat")
        self.assertIsNone(result)

    @patch('gitclone.api.urlopen')
    def test_request_json_decode_error(self, mock_urlopen):
        """Test API request with invalid JSON response"""
        mock_response = MagicMock()
        mock_response.read.return_value = b"invalid json"
        mock_response.headers = {"X-RateLimit-Remaining": "5000"}
        mock_urlopen.return_value.__enter__.return_value = mock_response

        result = self.api._request("/users/octocat")
        self.assertIsNone(result)

    @patch('gitclone.api.urlopen')
    def test_request_rate_limit(self, mock_urlopen):
        """Test API request with rate limit handling"""
        # First call raises rate limit error
        error = HTTPError(
            url="https://api.github.com/users/octocat",
            code=403,
            msg="rate limit exceeded",
            hdrs={"X-RateLimit-Reset": str(int(time.time()) + 1)},
            fp=None
        )
        
        # Second call succeeds
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({"id": 1}).encode()
        mock_response.headers = {"X-RateLimit-Remaining": "4999"}
        
        mock_urlopen.side_effect = [error, mock_response.__enter__.return_value]

        # Mock sleep to speed up test
        with patch('time.sleep', return_value=None):
            result = self.api._request("/users/octocat")
        
        self.assertIsNotNone(result)
        self.assertEqual(result["id"], 1)

    # ==================== REPOSITORY TESTS ====================

    @patch('gitclone.api.urlopen')
    def test_get_repos_success(self, mock_urlopen):
        """Test successful repository listing"""
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps([
            {"name": "repo1", "clone_url": "https://github.com/user/repo1", "private": False, "fork": False},
            {"name": "repo2", "clone_url": "https://github.com/user/repo2", "private": True, "fork": False},
            {"name": "repo3", "clone_url": "https://github.com/user/repo3", "private": False, "fork": True},
        ]).encode()
        mock_response.headers = {"X-RateLimit-Remaining": "5000"}
        mock_urlopen.return_value.__enter__.return_value = mock_response

        repos = self.api.get_repos(self.test_owner)
        
        self.assertEqual(len(repos), 3)
        self.assertEqual(repos[0]["name"], "repo1")
        self.assertEqual(repos[1]["name"], "repo2")
        self.assertEqual(repos[2]["name"], "repo3")

    @patch('gitclone.api.urlopen')
    def test_get_repos_filter_public(self, mock_urlopen):
        """Test getting only public repositories"""
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps([
            {"name": "repo1", "private": False},
            {"name": "repo2", "private": True},
            {"name": "repo3", "private": False},
        ]).encode()
        mock_response.headers = {"X-RateLimit-Remaining": "5000"}
        mock_urlopen.return_value.__enter__.return_value = mock_response

        repos = self.api.get_repos(self.test_owner, repo_type="public")
        
        # Should filter out private repos
        self.assertEqual(len(repos), 2)
        for repo in repos:
            self.assertFalse(repo.get("private", False))

    @patch('gitclone.api.urlopen')
    def test_get_repos_filter_private(self, mock_urlopen):
        """Test getting only private repositories"""
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps([
            {"name": "repo1", "private": False},
            {"name": "repo2", "private": True},
            {"name": "repo3", "private": True},
        ]).encode()
        mock_response.headers = {"X-RateLimit-Remaining": "5000"}
        mock_urlopen.return_value.__enter__.return_value = mock_response

        repos = self.api.get_repos(self.test_owner, repo_type="private")
        
        # Should filter out public repos
        self.assertEqual(len(repos), 2)
        for repo in repos:
            self.assertTrue(repo.get("private", False))

    @patch('gitclone.api.urlopen')
    def test_get_repos_exclude_forks(self, mock_urlopen):
        """Test excluding forked repositories"""
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps([
            {"name": "repo1", "fork": False},
            {"name": "repo2", "fork": True},
            {"name": "repo3", "fork": False},
        ]).encode()
        mock_response.headers = {"X-RateLimit-Remaining": "5000"}
        mock_urlopen.return_value.__enter__.return_value = mock_response

        repos = self.api.get_repos(self.test_owner, include_forks=False)
        
        # Should filter out forks
        self.assertEqual(len(repos), 2)
        for repo in repos:
            self.assertFalse(repo.get("fork", False))

    @patch('gitclone.api.urlopen')
    def test_get_repos_with_pagination(self, mock_urlopen):
        """Test repository listing with pagination"""
        # Mock multiple pages
        def mock_urlopen_side_effect(*args, **kwargs):
            mock_response = MagicMock()
            mock_response.headers = {"X-RateLimit-Remaining": "5000"}
            
            # Parse page parameter from URL
            url = args[0].full_url if hasattr(args[0], 'full_url') else str(args[0])
            if "page=1" in url:
                mock_response.read.return_value = json.dumps([
                    {"name": "repo1"},
                    {"name": "repo2"},
                ]).encode()
            elif "page=2" in url:
                mock_response.read.return_value = json.dumps([
                    {"name": "repo3"},
                ]).encode()
            else:
                mock_response.read.return_value = json.dumps([]).encode()
            
            return mock_response.__enter__.return_value

        mock_urlopen.side_effect = mock_urlopen_side_effect

        repos = self.api.get_repos(self.test_owner, per_page=2)
        
        self.assertEqual(len(repos), 3)
        self.assertEqual(repos[0]["name"], "repo1")
        self.assertEqual(repos[1]["name"], "repo2")
        self.assertEqual(repos[2]["name"], "repo3")

    @patch('gitclone.api.urlopen')
    def test_get_repos_empty(self, mock_urlopen):
        """Test getting repositories when none exist"""
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps([]).encode()
        mock_response.headers = {"X-RateLimit-Remaining": "5000"}
        mock_urlopen.return_value.__enter__.return_value = mock_response

        repos = self.api.get_repos("emptyuser")
        
        self.assertEqual(len(repos), 0)

    @patch('gitclone.api.urlopen')
    def test_get_repo_success(self, mock_urlopen):
        """Test getting a single repository"""
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "name": self.test_repo,
            "clone_url": f"https://github.com/{self.test_owner}/{self.test_repo}",
            "private": False,
            "fork": False,
            "description": "A test repository",
            "stargazers_count": 100,
            "forks_count": 50
        }).encode()
        mock_response.headers = {"X-RateLimit-Remaining": "5000"}
        mock_urlopen.return_value.__enter__.return_value = mock_response

        repo = self.api.get_repo(self.test_owner, self.test_repo)
        
        self.assertIsNotNone(repo)
        self.assertEqual(repo["name"], self.test_repo)
        self.assertEqual(repo["clone_url"], f"https://github.com/{self.test_owner}/{self.test_repo}")
        self.assertEqual(repo["stargazers_count"], 100)

    @patch('gitclone.api.urlopen')
    def test_get_repo_not_found(self, mock_urlopen):
        """Test getting a nonexistent repository"""
        error = HTTPError(
            url=f"https://api.github.com/repos/{self.test_owner}/nonexistent",
            code=404,
            msg="Not Found",
            hdrs={},
            fp=None
        )
        mock_urlopen.side_effect = error

        repo = self.api.get_repo(self.test_owner, "nonexistent")
        self.assertIsNone(repo)

    # ==================== ORGANIZATION TESTS ====================

    @patch('gitclone.api.urlopen')
    def test_is_organization_true(self, mock_urlopen):
        """Test checking if a name is an organization (true)"""
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "type": "Organization"
        }).encode()
        mock_response.headers = {"X-RateLimit-Remaining": "5000"}
        mock_urlopen.return_value.__enter__.return_value = mock_response

        result = self.api._is_organization("google")
        self.assertTrue(result)

    @patch('gitclone.api.urlopen')
    def test_is_organization_false(self, mock_urlopen):
        """Test checking if a name is an organization (false)"""
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "type": "User"
        }).encode()
        mock_response.headers = {"X-RateLimit-Remaining": "5000"}
        mock_urlopen.return_value.__enter__.return_value = mock_response

        result = self.api._is_organization("octocat")
        self.assertFalse(result)

    @patch('gitclone.api.urlopen')
    def test_is_organization_error(self, mock_urlopen):
        """Test checking if a name is an organization with error"""
        error = HTTPError(
            url="https://api.github.com/users/nonexistent",
            code=404,
            msg="Not Found",
            hdrs={},
            fp=None
        )
        mock_urlopen.side_effect = error

        result = self.api._is_organization("nonexistent")
        self.assertFalse(result)

    # ==================== RATE LIMIT TESTS ====================

    @patch('gitclone.api.urlopen')
    def test_check_rate_limit(self, mock_urlopen):
        """Test checking rate limit status"""
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "resources": {
                "core": {
                    "limit": 5000,
                    "remaining": 4999,
                    "reset": 1234567890
                }
            }
        }).encode()
        mock_response.headers = {"X-RateLimit-Remaining": "4999"}
        mock_urlopen.return_value.__enter__.return_value = mock_response

        rate_limit = self.api.check_rate_limit()
        
        self.assertEqual(rate_limit["remaining"], 4999)
        self.assertEqual(rate_limit["reset"], 1234567890)

    @patch('gitclone.api.urlopen')
    def test_rate_limit_tracking(self, mock_urlopen):
        """Test rate limit tracking from headers"""
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps([]).encode()
        mock_response.headers = {
            "X-RateLimit-Remaining": "4500",
            "X-RateLimit-Reset": "1234567890"
        }
        mock_urlopen.return_value.__enter__.return_value = mock_response

        self.api._request("/users/octocat")
        
        self.assertEqual(self.api.rate_limit_remaining, 4500)
        self.assertEqual(self.api.rate_limit_reset, 1234567890)

    # ==================== AUTHENTICATION TESTS ====================

    @patch('gitclone.api.urlopen')
    def test_auth_header_with_token(self, mock_urlopen):
        """Test authentication header is set when token is provided"""
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({}).encode()
        mock_response.headers = {"X-RateLimit-Remaining": "5000"}
        mock_urlopen.return_value.__enter__.return_value = mock_response

        self.api._request("/user")
        
        # Check that Authorization header was set
        call_args = mock_urlopen.call_args[0][0]
        self.assertEqual(call_args.headers["Authorization"], "token test_token_123")

    @patch('gitclone.api.urlopen')
    def test_auth_header_without_token(self, mock_urlopen):
        """Test authentication header is not set without token"""
        api = GitHubAPI()
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({}).encode()
        mock_response.headers = {"X-RateLimit-Remaining": "5000"}
        mock_urlopen.return_value.__enter__.return_value = mock_response

        api._request("/users/octocat")
        
        # Check that Authorization header is not set
        call_args = mock_urlopen.call_args[0][0]
        self.assertNotIn("Authorization", call_args.headers)

    # ==================== EDGE CASES ====================

    def test_empty_endpoint(self):
        """Test request with empty endpoint"""
        result = self.api._request("")
        self.assertIsNone(result)

    def test_none_endpoint(self):
        """Test request with None endpoint"""
        result = self.api._request(None)
        self.assertIsNone(result)

    @patch('gitclone.api.urlopen')
    def test_request_timeout(self, mock_urlopen):
        """Test request timeout handling"""
        import socket
        mock_urlopen.side_effect = socket.timeout("Connection timed out")

        result = self.api._request("/users/octocat")
        self.assertIsNone(result)


class TestGitHubAPIIntegration(unittest.TestCase):
    """Integration tests for GitHub API (requires internet)"""

    @classmethod
    def setUpClass(cls):
        """Check if internet is available"""
        import socket
        try:
            socket.create_connection(("api.github.com", 443), timeout=5)
            cls.internet_available = True
        except:
            cls.internet_available = False

    def setUp(self):
        if not self.internet_available:
            self.skipTest("No internet connection")
        self.api = GitHubAPI()

    def test_live_api_get_repos(self):
        """Test live API repository listing"""
        repos = self.api.get_repos("octocat", per_page=5)
        self.assertGreater(len(repos), 0)

    def test_live_api_get_repo(self):
        """Test live API getting a single repository"""
        repo = self.api.get_repo("octocat", "Hello-World")
        self.assertIsNotNone(repo)
        self.assertEqual(repo["name"], "Hello-World")

    def test_live_api_rate_limit(self):
        """Test live API rate limit check"""
        rate_limit = self.api.check_rate_limit()
        self.assertIn("remaining", rate_limit)
        self.assertIn("reset", rate_limit)


if __name__ == "__main__":
    unittest.main()