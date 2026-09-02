"""
Custom exceptions for GitClonePro
"""

class GitCloneProError(Exception):
    """Base exception for GitClonePro"""
    pass

class CloneError(GitCloneProError):
    """Raised when cloning fails"""
    pass

class AuthenticationError(GitCloneProError):
    """Raised when authentication fails"""
    pass

class RateLimitError(GitCloneProError):
    """Raised when GitHub API rate limit is exceeded"""
    pass

class InvalidURLError(GitCloneProError):
    """Raised when URL is invalid"""
    pass

class RepositoryNotFoundError(GitCloneProError):
    """Raised when repository is not found"""
    pass

class SparseCheckoutError(GitCloneProError):
    """Raised when sparse checkout fails"""
    pass

class BatchCloneError(GitCloneProError):
    """Raised when batch clone has failures"""
    pass

class ConfigurationError(GitCloneProError):
    """Raised when configuration is invalid"""
    pass