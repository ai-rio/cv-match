"""Core exceptions for the application."""


class ProviderError(RuntimeError):
    """Raised when the underlying LLM provider fails"""


class StrategyError(RuntimeError):
    """Raised when a Strategy cannot parse/return expected output"""


class ValidationError(RuntimeError):
    """Raised when input validation fails"""


class AuthenticationError(RuntimeError):
    """Raised when authentication fails"""


class AuthorizationError(RuntimeError):
    """Raised when authorization fails"""


class DatabaseError(RuntimeError):
    """Raised when database operations fail"""
