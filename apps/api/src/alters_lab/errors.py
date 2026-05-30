"""Structured error types for Alters Lab API.

All service-layer errors should inherit from AppError.
The global exception handler in main.py converts these to JSON responses.
"""

from __future__ import annotations


class AppError(Exception):
    """Base error for all application errors."""

    status_code: int = 500
    error_code: str = "INTERNAL_ERROR"

    def __init__(self, message: str, *, detail: dict | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.detail = detail

    def to_response(self) -> dict:
        body: dict = {"error": self.error_code, "message": self.message}
        if self.detail:
            body["detail"] = self.detail
        return body


class NotFoundError(AppError):
    status_code = 404
    error_code = "NOT_FOUND"


class ValidationError(AppError):
    status_code = 422
    error_code = "VALIDATION_ERROR"


class ConflictError(AppError):
    status_code = 409
    error_code = "CONFLICT"


class ForbiddenError(AppError):
    status_code = 403
    error_code = "FORBIDDEN"


class ProviderError(AppError):
    status_code = 502
    error_code = "PROVIDER_ERROR"


class StorageError(AppError):
    status_code = 500
    error_code = "STORAGE_ERROR"
