#!/usr/bin/env python3
"""
Unit tests for progress bar functionality
"""

import unittest
from gitclone.progress import ProgressManager, get_progress_manager

class TestProgress(unittest.TestCase):
    def test_progress_manager_init(self):
        """Test progress manager initialization"""
        pm = ProgressManager(enabled=True, verbose=False)
        self.assertTrue(pm.enabled)
        self.assertFalse(pm.verbose)
        
    def test_progress_manager_disabled(self):
        """Test progress manager with disabled progress"""
        pm = ProgressManager(enabled=False)
        self.assertFalse(pm.enabled)
        
    def test_spinner_context(self):
        """Test spinner context manager"""
        pm = ProgressManager(enabled=True, verbose=False)
        
        with pm.spinner("Testing"):
            pass  # Just ensure it doesn't crash
            
    def test_progress_bar_creation(self):
        """Test progress bar creation"""
        pm = ProgressManager(enabled=True)
        bar = pm.create_progress_bar(total=10, desc="Test")
        self.assertIsNotNone(bar)
        pm.close_progress(bar)
        
    def test_global_progress_manager(self):
        """Test global progress manager"""
        pm1 = get_progress_manager()
        pm2 = get_progress_manager()
        self.assertIs(pm1, pm2)  # Should be same instance

if __name__ == "__main__":
    unittest.main()