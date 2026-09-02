"""
Progress tracking utilities for GitClonePro
"""

import sys
import time
from typing import Optional, Iterator
from contextlib import contextmanager

try:
    from tqdm import tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False
    # Fallback to simple progress bar
    class tqdm:
        def __init__(self, iterable=None, desc=None, total=None, unit=None, **kwargs):
            self.iterable = iterable
            self.desc = desc
            self.total = total
            self.unit = unit or "items"
            self.n = 0
            
        def __iter__(self):
            if self.total is None and self.iterable is not None:
                self.total = len(self.iterable)
            for item in self.iterable:
                self.n += 1
                self._update()
                yield item
                
        def _update(self):
            if self.total:
                percent = (self.n / self.total) * 100
                bar = "█" * int(self.n / self.total * 20) + "░" * (20 - int(self.n / self.total * 20))
                sys.stdout.write(f"\r{self.desc}: {bar} {self.n}/{self.total} ({percent:.1f}%)")
                sys.stdout.flush()
                
        def update(self, n=1):
            self.n += n
            self._update()
            
        def close(self):
            sys.stdout.write("\n")
            sys.stdout.flush()
            
        def __enter__(self):
            return self
            
        def __exit__(self, *args):
            self.close()

class ProgressManager:
    """Manage progress bars for cloning operations"""
    
    def __init__(self, enabled: bool = True, verbose: bool = False):
        self.enabled = enabled
        self.verbose = verbose
        self.bars = []
        
    @contextmanager
    def spinner(self, message: str = "Processing"):
        """Show a spinner animation"""
        if not self.enabled or self.verbose:
            yield
            return
            
        spinner_chars = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
        try:
            sys.stdout.write(f"{message} ")
            for i in range(30):
                sys.stdout.write(f"\b{spinner_chars[i % len(spinner_chars)]}")
                sys.stdout.flush()
                time.sleep(0.1)
            sys.stdout.write("\b✓\n")
        except KeyboardInterrupt:
            sys.stdout.write("\b✗\n")
            raise
            
    def create_progress_bar(self, total: int, desc: str = "Cloning", unit: str = "repo") -> tqdm:
        """Create a progress bar"""
        if not self.enabled:
            return tqdm(iterable=range(total), desc=desc, total=total, unit=unit, disable=True)
            
        return tqdm(
            total=total,
            desc=desc,
            unit=unit,
            ncols=80,
            bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]"
        )
        
    def update_progress(self, bar: tqdm, n: int = 1):
        """Update progress bar"""
        if bar:
            bar.update(n)
            
    def close_progress(self, bar: tqdm):
        """Close progress bar"""
        if bar:
            bar.close()
            
    def log_progress(self, message: str, level: str = "INFO"):
        """Log message with progress context"""
        if self.verbose:
            from .logger import log
            log(message, level)

# Global progress manager
_progress_manager = ProgressManager()

def get_progress_manager() -> ProgressManager:
    """Get global progress manager"""
    return _progress_manager

def set_progress_enabled(enabled: bool):
    """Enable or disable progress bars"""
    _progress_manager.enabled = enabled