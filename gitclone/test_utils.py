#!/usr/bin/env python3
"""
Unit tests for utility functions
"""

import unittest
import tempfile
import os
from pathlib import Path

from gitclone.utils import (
    expand_path,
    validate_url,
    get_repo_name,
    get_owner_and_repo
)

class TestUtils(unittest.TestCase):
    def test_expand_path(self):
        """Test path expansion"""
        # Test home directory
        expanded = expand_path("~/test")
        self.assertTrue(expanded.startswith(str(Path.home())))
        
        # Test environment variables
        os.environ["TEST_DIR"] = "/test"
        expanded = expand_path("$TEST_DIR/path")
        self.assertEqual(expanded, "/test/path")
        
        # Test absolute path
        expanded = expand_path("/absolute/path")
        self.assertEqual(expanded, "/absolute/path")
        
    def test_validate_url(self):
        """Test URL validation"""
        valid_urls = [
            "https://github.com/user/repo",
            "https://github.com/user/repo.git",
            "git@github.com:user/repo.git",
            "https://github.com/user/repo/tree/master",
        ]
        
        invalid_urls = [
            "not_a_url",
            "https://notgithub.com/user/repo",
            "github.com/user/repo",
            "https://github.com/",
            "",
        ]
        
        for url in valid_urls:
            self.assertTrue(validate_url(url), f"Should be valid: {url}")
            
        for url in invalid_urls:
            self.assertFalse(validate_url(url), f"Should be invalid: {url}")
            
    def test_get_repo_name(self):
        """Test repository name extraction"""
        test_cases = [
            ("https://github.com/user/repo", "repo"),
            ("https://github.com/user/repo.git", "repo"),
            ("git@github.com:user/repo.git", "repo"),
            ("https://github.com/user/repo/tree/master", "repo"),
        ]
        
        for url, expected in test_cases:
            self.assertEqual(get_repo_name(url), expected)
            
    def test_get_owner_and_repo(self):
        """Test owner and repo extraction"""
        test_cases = [
            ("https://github.com/octocat/Hello-World", ("octocat", "Hello-World")),
            ("https://github.com/octocat/Hello-World.git", ("octocat", "Hello-World")),
            ("git@github.com:octocat/Hello-World.git", ("octocat", "Hello-World")),
        ]
        
        for url, expected in test_cases:
            self.assertEqual(get_owner_and_repo(url), expected)
            
        # Invalid URLs should return (None, None)
        self.assertEqual(get_owner_and_repo("invalid"), (None, None))

if __name__ == "__main__":
    unittest.main()