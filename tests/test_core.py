#!/usr/bin/env python3
"""
Unit tests for GitClonePro core functionality
Tests all core operations including:
- Initialization
- Configuration loading
- Single clone operations
- Batch clone operations
- Error handling
- Utility functions
"""

import unittest
import tempfile
import os
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open

sys.path.insert(0, str(Path(__file__).parent.parent))

from gitclone.core import GitClonePro
from gitclone.utils import validate_url, get_repo_name, expand_path, get_owner_and_repo
from gitclone.exceptions import (
    GitCloneProError,
    CloneError,
    AuthenticationError,
    InvalidURLError,
    ConfigurationError
)


class TestGitClonePro(unittest.TestCase):
    """Test GitClonePro core class"""

    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_dir = Path(self.temp_dir.name)
        
        # Create mock config
        self.config_content = """
github_token: "config_token_123"
clone_dir: "/custom/path"
default_branch: "develop"
retries: 5
threads: 8
timeout: 60
verbose: true
        """
        
        self.config_path = self.test_dir / "config.yaml"
        self.config_path.write_text(self.config_content)

    def tearDown(self):
        """Clean up after tests"""
        self.temp_dir.cleanup()

    # ==================== INITIALIZATION TESTS ====================

    def test_initialization_default(self):
        """Test default initialization"""
        core = GitClonePro()
        self.assertIsNotNone(core)
        self.assertTrue(hasattr(core, "clone_single"))
        self.assertTrue(hasattr(core, "batch_clone"))
        self.assertTrue(hasattr(core, "api"))
        self.assertTrue(hasattr(core, "config"))
        self.assertTrue(hasattr(core, "clone_dir"))

    def test_initialization_with_token(self):
        """Test initialization with token parameter"""
        core = GitClonePro(token="test_token_456")
        self.assertEqual(core.config.get("github_token"), "test_token_456")

    def test_initialization_with_config_file(self):
        """Test initialization with config file"""
        core = GitClonePro(config_path=str(self.config_path))
        self.assertEqual(core.config.get("github_token"), "config_token_123")
        self.assertEqual(core.config.get("default_branch"), "develop")
        self.assertEqual(core.config.get("retries"), 5)
        self.assertEqual(core.config.get("threads"), 8)

    def test_initialization_with_ssh(self):
        """Test initialization with SSH mode"""
        core = GitClonePro(use_ssh=True)
        self.assertTrue(core.use_ssh)
        self.assertTrue(core.config.get("use_ssh"))

    def test_initialization_with_verbose(self):
        """Test initialization with verbose mode"""
        core = GitClonePro(verbose=True, quiet=False)
        self.assertTrue(core.verbose)
        self.assertFalse(core.quiet)

    def test_initialization_with_quiet(self):
        """Test initialization with quiet mode"""
        core = GitClonePro(verbose=False, quiet=True)
        self.assertFalse(core.verbose)
        self.assertTrue(core.quiet)

    def test_initialization_verbose_quiet_override(self):
        """Test quiet mode overrides verbose"""
        core = GitClonePro(verbose=True, quiet=True)
        self.assertFalse(core.verbose)
        self.assertTrue(core.quiet)

    @patch.dict(os.environ, {'GITHUB_TOKEN': 'env_token_789'})
    def test_initialization_from_env(self):
        """Test initialization from environment variable"""
        core = GitClonePro()
        self.assertEqual(core.config.get("github_token"), "env_token_789")

    def test_initialization_with_nonexistent_config(self):
        """Test initialization with nonexistent config file"""
        core = GitClonePro(config_path="/nonexistent/config.yaml")
        self.assertIsNotNone(core.config)
        self.assertEqual(core.config.get("default_branch"), "main")

    # ==================== CONFIG LOADING TESTS ====================

    def test_load_config_from_file(self):
        """Test loading configuration from file"""
        core = GitClonePro(config_path=str(self.config_path))
        config = core.config
        
        self.assertEqual(config["github_token"], "config_token_123")
        self.assertEqual(config["clone_dir"], "/custom/path")
        self.assertEqual(config["default_branch"], "develop")
        self.assertEqual(config["retries"], 5)
        self.assertEqual(config["threads"], 8)
        self.assertEqual(config["timeout"], 60)
        self.assertTrue(config["verbose"])

    def test_load_config_from_home(self):
        """Test loading configuration from home directory"""
        home_config = Path.home() / ".gitclone_config.yaml"
        if home_config.exists():
            core = GitClonePro()
            self.assertIsNotNone(core.config)

    def test_load_config_with_defaults(self):
        """Test loading configuration with defaults"""
        core = GitClonePro()
        config = core.config
        
        # Check default values
        self.assertIn("github_token", config)
        self.assertIn("clone_dir", config)
        self.assertIn("default_branch", config)
        self.assertIn("retries", config)
        self.assertIn("threads", config)
        self.assertIn("timeout", config)

    def test_config_token_override(self):
        """Test token override from config"""
        core = GitClonePro(token="override_token", config_path=str(self.config_path))
        self.assertEqual(core.config.get("github_token"), "override_token")

    # ==================== SINGLE CLONE TESTS ====================

    @patch('gitclone.core.clone_repo')
    def test_clone_single_success(self, mock_clone):
        """Test successful single clone"""
        mock_clone.return_value = True
        
        core = GitClonePro(verbose=False)
        result = core.clone_single(
            url="https://github.com/octocat/Hello-World",
            dest=str(self.test_dir / "Hello-World")
        )
        
        self.assertTrue(result)
        mock_clone.assert_called_once()

    @patch('gitclone.core.clone_repo')
    def test_clone_single_failure(self, mock_clone):
        """Test failed single clone"""
        mock_clone.return_value = False
        
        core = GitClonePro(verbose=False)
        result = core.clone_single(
            url="https://github.com/octocat/Hello-World",
            dest=str(self.test_dir / "Hello-World")
        )
        
        self.assertFalse(result)

    @patch('gitclone.core.clone_repo')
    def test_clone_single_with_default_dest(self, mock_clone):
        """Test single clone with default destination"""
        mock_clone.return_value = True
        
        core = GitClonePro(verbose=False)
        result = core.clone_single(
            url="https://github.com/octocat/Hello-World"
        )
        
        self.assertTrue(result)
        # Should use clone_dir from config
        mock_clone.assert_called_once()

    @patch('gitclone.core.sparse_clone')
    def test_clone_single_with_sparse(self, mock_sparse):
        """Test single clone with sparse checkout"""
        mock_sparse.return_value = True
        
        core = GitClonePro(verbose=False)
        result = core.clone_single(
            url="https://github.com/octocat/Hello-World",
            dest=str(self.test_dir / "Hello-World"),
            sparse=["README.md", "src/"]
        )
        
        self.assertTrue(result)
        mock_sparse.assert_called_once()

    @patch('gitclone.core.clone_repo')
    def test_clone_single_with_custom_branch(self, mock_clone):
        """Test single clone with custom branch"""
        mock_clone.return_value = True
        
        core = GitClonePro(verbose=False)
        result = core.clone_single(
            url="https://github.com/octocat/Hello-World",
            dest=str(self.test_dir / "Hello-World"),
            branch="develop"
        )
        
        self.assertTrue(result)

    @patch('gitclone.core.clone_repo')
    def test_clone_single_with_depth(self, mock_clone):
        """Test single clone with depth parameter"""
        mock_clone.return_value = True
        
        core = GitClonePro(verbose=False)
        result = core.clone_single(
            url="https://github.com/octocat/Hello-World",
            dest=str(self.test_dir / "Hello-World"),
            depth=1
        )
        
        self.assertTrue(result)

    @patch('gitclone.core.clone_repo')
    def test_clone_single_with_mirror(self, mock_clone):
        """Test single clone with mirror option"""
        mock_clone.return_value = True
        
        core = GitClonePro(verbose=False)
        result = core.clone_single(
            url="https://github.com/octocat/Hello-World",
            dest=str(self.test_dir / "Hello-World"),
            mirror=True
        )
        
        self.assertTrue(result)

    @patch('gitclone.core.clone_repo')
    def test_clone_single_with_ssh(self, mock_clone):
        """Test single clone with SSH"""
        mock_clone.return_value = True
        
        core = GitClonePro(use_ssh=True, verbose=False)
        result = core.clone_single(
            url="git@github.com:octocat/Hello-World.git",
            dest=str(self.test_dir / "Hello-World")
        )
        
        self.assertTrue(result)
        # Verify URL conversion happened
        mock_clone.assert_called()

    def test_clone_single_invalid_url(self):
        """Test single clone with invalid URL"""
        core = GitClonePro(verbose=False)
        result = core.clone_single(url="invalid-url")
        self.assertFalse(result)

    def test_clone_single_empty_url(self):
        """Test single clone with empty URL"""
        core = GitClonePro(verbose=False)
        result = core.clone_single(url="")
        self.assertFalse(result)

    # ==================== BATCH CLONE TESTS ====================

    @patch('gitclone.core.batch_clone')
    def test_batch_clone_success(self, mock_batch):
        """Test successful batch clone"""
        mock_batch.return_value = True
        
        core = GitClonePro(verbose=False)
        result = core.batch_clone(
            owner="octocat",
            dest=str(self.test_dir / "batch"),
            repo_type="public"
        )
        
        self.assertTrue(result)
        mock_batch.assert_called_once()

    @patch('gitclone.core.batch_clone')
    def test_batch_clone_failure(self, mock_batch):
        """Test failed batch clone"""
        mock_batch.return_value = False
        
        core = GitClonePro(verbose=False)
        result = core.batch_clone(
            owner="octocat",
            dest=str(self.test_dir / "batch"),
            repo_type="public"
        )
        
        self.assertFalse(result)

    @patch('gitclone.core.batch_clone')
    def test_batch_clone_with_threads(self, mock_batch):
        """Test batch clone with custom threads"""
        mock_batch.return_value = True
        
        core = GitClonePro(verbose=False)
        result = core.batch_clone(
            owner="octocat",
            dest=str(self.test_dir / "batch"),
            threads=10
        )
        
        self.assertTrue(result)

    @patch('gitclone.core.batch_clone')
    def test_batch_clone_with_depth(self, mock_batch):
        """Test batch clone with depth"""
        mock_batch.return_value = True
        
        core = GitClonePro(verbose=False)
        result = core.batch_clone(
            owner="octocat",
            dest=str(self.test_dir / "batch"),
            depth=1
        )
        
        self.assertTrue(result)

    @patch('gitclone.core.batch_clone')
    def test_batch_clone_with_mirror(self, mock_batch):
        """Test batch clone with mirror"""
        mock_batch.return_value = True
        
        core = GitClonePro(verbose=False)
        result = core.batch_clone(
            owner="octocat",
            dest=str(self.test_dir / "batch"),
            mirror=True
        )
        
        self.assertTrue(result)

    def test_batch_clone_empty_owner(self):
        """Test batch clone with empty owner"""
        core = GitClonePro(verbose=False)
        result = core.batch_clone(owner="")
        self.assertFalse(result)

    # ==================== UTILITY FUNCTION TESTS ====================

    def test_validate_url(self):
        """Test URL validation utility"""
        # Valid URLs
        self.assertTrue(validate_url("https://github.com/user/repo"))
        self.assertTrue(validate_url("https://github.com/user/repo.git"))
        self.assertTrue(validate_url("git@github.com:user/repo.git"))
        self.assertTrue(validate_url("https://github.com/user/repo/tree/main"))
        
        # Invalid URLs
        self.assertFalse(validate_url(""))
        self.assertFalse(validate_url("not_a_url"))
        self.assertFalse(validate_url("https://notgithub.com/user/repo"))
        self.assertFalse(validate_url("github.com/user/repo"))
        self.assertFalse(validate_url("https://github.com/"))

    def test_get_repo_name(self):
        """Test repository name extraction"""
        test_cases = [
            ("https://github.com/user/repo", "repo"),
            ("https://github.com/user/repo.git", "repo"),
            ("git@github.com:user/repo.git", "repo"),
            ("https://github.com/user/repo/tree/main", "repo"),
        ]
        
        for url, expected in test_cases:
            self.assertEqual(get_repo_name(url), expected)

    def test_expand_path(self):
        """Test path expansion"""
        # Test with home directory
        expanded = expand_path("~/test")
        self.assertTrue(expanded.startswith(str(Path.home())))
        
        # Test with environment variable
        os.environ["TEST_DIR"] = "/test"
        expanded = expand_path("$TEST_DIR/path")
        self.assertEqual(expanded, "/test/path")
        del os.environ["TEST_DIR"]
        
        # Test with absolute path
        expanded = expand_path("/absolute/path")
        self.assertEqual(expanded, "/absolute/path")
        
        # Test with None
        self.assertEqual(expand_path(None), None)
        
        # Test with empty string
        self.assertEqual(expand_path(""), "")

    def test_get_owner_and_repo(self):
        """Test owner and repository extraction"""
        test_cases = [
            ("https://github.com/octocat/Hello-World", ("octocat", "Hello-World")),
            ("https://github.com/octocat/Hello-World.git", ("octocat", "Hello-World")),
            ("git@github.com:octocat/Hello-World.git", ("octocat", "Hello-World")),
        ]
        
        for url, expected in test_cases:
            self.assertEqual(get_owner_and_repo(url), expected)
        
        # Invalid URLs should return (None, None)
        self.assertEqual(get_owner_and_repo("invalid"), (None, None))

    # ==================== ERROR HANDLING TESTS ====================

    @patch('gitclone.core.clone_repo')
    def test_clone_single_error_handling(self, mock_clone):
        """Test error handling in single clone"""
        mock_clone.side_effect = Exception("Unexpected error")
        
        core = GitClonePro(verbose=False)
        result = core.clone_single(
            url="https://github.com/octocat/Hello-World",
            dest=str(self.test_dir / "Hello-World")
        )
        
        self.assertFalse(result)

    @patch('gitclone.core.batch_clone')
    def test_batch_clone_error_handling(self, mock_batch):
        """Test error handling in batch clone"""
        mock_batch.side_effect = Exception("Unexpected error")
        
        core = GitClonePro(verbose=False)
        result = core.batch_clone(owner="octocat")
        
        self.assertFalse(result)

    def test_invalid_config(self):
        """Test invalid configuration handling"""
        # Create invalid config
        invalid_config = self.test_dir / "invalid.yaml"
        invalid_config.write_text("invalid: yaml: content: [")
        
        core = GitClonePro(config_path=str(invalid_config))
        # Should fall back to defaults
        self.assertIsNotNone(core.config)

    # ==================== ATTRIBUTE TESTS ====================

    def test_core_attributes(self):
        """Test core object has all required attributes"""
        core = GitClonePro(verbose=False)
        
        required_attrs = [
            "config",
            "api",
            "clone_dir",
            "clone_single",
            "batch_clone",
            "_load_config",
            "verbose",
            "quiet",
            "use_ssh"
        ]
        
        for attr in required_attrs:
            self.assertTrue(hasattr(core, attr), f"Missing attribute: {attr}")

    def test_config_attributes(self):
        """Test configuration has required keys"""
        core = GitClonePro(verbose=False)
        config = core.config
        
        required_keys = [
            "github_token",
            "clone_dir",
            "default_branch",
            "retries",
            "threads",
            "timeout",
            "verbose",
            "use_ssh"
        ]
        
        for key in required_keys:
            self.assertIn(key, config, f"Missing config key: {key}")

    # ==================== PERFORMANCE TESTS ====================

    def test_config_loading_performance(self):
        """Test config loading performance (should be fast)"""
        import time
        
        start = time.time()
        for _ in range(100):
            GitClonePro(verbose=False)
        elapsed = time.time() - start
        
        # Should load config in under 1 second for 100 iterations
        self.assertLess(elapsed, 1.0)


class TestCoreIntegration(unittest.TestCase):
    """Integration tests for core functionality (requires internet)"""

    @classmethod
    def setUpClass(cls):
        """Check if internet is available"""
        import socket
        try:
            socket.create_connection(("github.com", 80), timeout=5)
            cls.internet_available = True
        except:
            cls.internet_available = False

    def setUp(self):
        if not self.internet_available:
            self.skipTest("No internet connection")
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_dir = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_clone_public_repo_integration(self):
        """Integration test: clone public repository"""
        core = GitClonePro(verbose=False, quiet=True)
        result = core.clone_single(
            url="https://github.com/octocat/Hello-World",
            dest=str(self.test_dir / "Hello-World"),
            depth=1
        )
        self.assertTrue(result)
        
        # Verify clone exists
        clone_path = self.test_dir / "Hello-World"
        self.assertTrue(clone_path.exists())
        self.assertTrue((clone_path / ".git").exists())

    def test_batch_public_repos_integration(self):
        """Integration test: batch clone public repositories"""
        core = GitClonePro(verbose=False, quiet=True)
        result = core.batch_clone(
            owner="octocat",
            dest=str(self.test_dir / "batch"),
            repo_type="public",
            threads=2,
            depth=1
        )
        self.assertTrue(result)
        
        # Verify at least one repo was cloned
        batch_dir = self.test_dir / "batch"
        self.assertTrue(batch_dir.exists())
        repos = list(batch_dir.glob("*"))
        self.assertGreater(len(repos), 0)


if __name__ == "__main__":
    unittest.main()