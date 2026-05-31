# =============================================================================
# Custom HTTP exceptions for consistent API error responses
# =============================================================================

from fastapi import HTTPException, status


def not_found(resource: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{resource} not found")


def bad_request(message: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)
