"""
Custom exceptions for AI Parliament application.
Provides more specific error handling and better error messages.
"""
from typing import Optional, Any


class ParliamentException(Exception):
    """Base exception for all Parliament-related errors."""

    def __init__(self, message: str, details: Optional[Any] = None):
        self.message = message
        self.details = details
        super().__init__(self.message)


class DebateNotFoundError(ParliamentException):
    """Raised when a requested debate doesn't exist."""

    def __init__(self, debate_id: int):
        super().__init__(
            f"Debate with ID {debate_id} not found",
            {"debate_id": debate_id}
        )


class PaperNotFoundError(ParliamentException):
    """Raised when a requested policy paper doesn't exist."""

    def __init__(self, paper_id: int):
        super().__init__(
            f"Policy paper with ID {paper_id} not found",
            {"paper_id": paper_id}
        )


class DebateGenerationError(ParliamentException):
    """Raised when debate generation fails."""

    def __init__(self, paper_id: int, reason: str):
        super().__init__(
            f"Failed to generate debate for paper {paper_id}: {reason}",
            {"paper_id": paper_id, "reason": reason}
        )


class MPResponseError(ParliamentException):
    """Raised when MP response generation fails."""

    def __init__(self, mp_role: str, reason: str):
        super().__init__(
            f"Failed to generate response for {mp_role}: {reason}",
            {"mp_role": mp_role, "reason": reason}
        )


class VoteGenerationError(ParliamentException):
    """Raised when vote generation fails."""

    def __init__(self, mp_role: str, debate_id: int, reason: str):
        super().__init__(
            f"Failed to generate vote for {mp_role} in debate {debate_id}: {reason}",
            {"mp_role": mp_role, "debate_id": debate_id, "reason": reason}
        )


class OpenAIServiceError(ParliamentException):
    """Raised when OpenAI API calls fail."""

    def __init__(self, operation: str, reason: str):
        super().__init__(
            f"OpenAI API error during {operation}: {reason}",
            {"operation": operation, "reason": reason}
        )


class InvalidMPRoleError(ParliamentException):
    """Raised when an invalid MP role is provided."""

    def __init__(self, role: str, valid_roles: list):
        super().__init__(
            f"Invalid MP role '{role}'. Valid roles: {', '.join(valid_roles)}",
            {"provided_role": role, "valid_roles": valid_roles}
        )


class ArxivFetchError(ParliamentException):
    """Raised when fetching papers from ArXiv fails."""

    def __init__(self, reason: str):
        super().__init__(
            f"Failed to fetch papers from ArXiv: {reason}",
            {"reason": reason}
        )


class DatabaseError(ParliamentException):
    """Raised when database operations fail."""

    def __init__(self, operation: str, reason: str):
        super().__init__(
            f"Database error during {operation}: {reason}",
            {"operation": operation, "reason": reason}
        )


class ValidationError(ParliamentException):
    """Raised when input validation fails."""

    def __init__(self, field: str, reason: str):
        super().__init__(
            f"Validation error for field '{field}': {reason}",
            {"field": field, "reason": reason}
        )


class RateLimitExceededError(ParliamentException):
    """Raised when rate limits are exceeded."""

    def __init__(self, limit: int, window: str):
        super().__init__(
            f"Rate limit exceeded: {limit} requests per {window}",
            {"limit": limit, "window": window}
        )
