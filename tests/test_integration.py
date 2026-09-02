#!/usr/bin/env python3
"""
Integration tests for GitClonePro
Requires internet connection and GitHub access
"""

import unittest
import tempfile
import os
from pathlib import Path

from gitclone.core import GitClonePro

class TestIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Skip integration tests if internet is not available"""
        import socket
        try:
            socket.create_connection(("github.com", 80), timeout=5)
            cls.internet_available = True
        except:
            cls.internet_available = False
            
    def setUp(self):
        if not self.internet_available:
            self.skipTest("No internet connection")
            
    def test_clone_public_repo(self):
        """Test cloning a public repository"""
        with tempfile.TemporaryDirectory() as tmpdir:
            core = GitClonePro(verbose=False, quiet=True)
            result = core.clone_single(
                url="https://github.com/octocat/Hello-World",
                dest=tmpdir
            )
            self.assertTrue(result)
            
            # Check if repo was cloned
            repo_path = Path(tmpdir) / "Hello-World"
            self.assertTrue(repo_path.exists())
            self.assertTrue((repo_path / ".git").exists())
            
    def test_batch_public_repos(self):
        """Test batch cloning public repositories"""
        with tempfile.TemporaryDirectory() as tmpdir:
            core = GitClonePro(verbose=False, quiet=True)
            result = core.batch_clone(
                owner="octocat",
                dest=tmpdir,
                repo_type="public",
                threads=2
            )
            self.assertTrue(result)
            
            # Check if at least one repo was cloned
            cloned_repos = list(Path(tmpdir).iterdir())
            self.assertGreater(len(cloned_repos), 0)
            
    def test_sparse_clone(self):
        """Test sparse checkout clone"""
        with tempfile.TemporaryDirectory() as tmpdir:
            core = GitClonePro(verbose=False, quiet=True)
            result = core.clone_single(
                url="https://github.com/octocat/Hello-World",
                dest=tmpdir,
                sparse=["README.md"]
            )
            self.assertTrue(result)
            
            # Check if README.md exists
            readme_path = Path(tmpdir) / "Hello-World" / "README.md"
            self.assertTrue(readme_path.exists())

if __name__ == "__main__":
    unittest.main()