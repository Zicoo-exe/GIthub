#!/usr/bin/env python3
"""
Unit tests for clone operations
"""

import unittest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

from gitclone.clone import clone_repo, sparse_clone, batch_clone
from gitclone.exceptions import CloneError

class TestClone(unittest.TestCase):
    @patch('gitclone.clone.run_command')
    def test_clone_repo_success(self, mock_run_command):
        """Test successful repository clone"""
        mock_run_command.return_value = ("", "", 0)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            result = clone_repo(
                repo_url="https://github.com/octocat/Hello-World",
                dest_dir=os.path.join(tmpdir, "Hello-World"),
                verbose=False
            )
            self.assertTrue(result)
            
    @patch('gitclone.clone.run_command')
    def test_clone_repo_failure(self, mock_run_command):
        """Test failed repository clone"""
        mock_run_command.return_value = ("", "Error", 1)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            result = clone_repo(
                repo_url="https://github.com/octocat/Hello-World",
                dest_dir=os.path.join(tmpdir, "Hello-World"),
                retries=1,
                verbose=False
            )
            self.assertFalse(result)
            
    @patch('gitclone.clone.run_command')
    def test_clone_repo_existing(self, mock_run_command):
        """Test clone when destination already exists"""
        with tempfile.TemporaryDirectory() as tmpdir:
            dest = os.path.join(tmpdir, "existing")
            os.makedirs(dest)
            
            result = clone_repo(
                repo_url="https://github.com/octocat/Hello-World",
                dest_dir=dest,
                verbose=False
            )
            self.assertTrue(result)
            mock_run_command.assert_not_called()
            
    @patch('gitclone.clone.run_command')
    def test_sparse_clone_success(self, mock_run_command):
        """Test successful sparse clone"""
        mock_run_command.return_value = ("", "", 0)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            result = sparse_clone(
                repo_url="https://github.com/octocat/Hello-World",
                dest_dir=os.path.join(tmpdir, "sparse"),
                paths=["README.md", "src/"],
                verbose=False
            )
            self.assertTrue(result)
            
    @patch('gitclone.clone.GitHubAPI')
    @patch('gitclone.clone.clone_repo')
    def test_batch_clone_success(self, mock_clone_repo, mock_github_api):
        """Test successful batch clone"""
        mock_github_api.return_value.get_repos.return_value = [
            {"name": "repo1", "clone_url": "https://github.com/user/repo1"},
            {"name": "repo2", "clone_url": "https://github.com/user/repo2"},
        ]
        mock_clone_repo.return_value = True
        
        with tempfile.TemporaryDirectory() as tmpdir:
            result = batch_clone(
                owner="testuser",
                dest_dir=tmpdir,
                threads=1,
                verbose=False
            )
            self.assertTrue(result)
            self.assertEqual(mock_clone_repo.call_count, 2)

if __name__ == "__main__":
    unittest.main()