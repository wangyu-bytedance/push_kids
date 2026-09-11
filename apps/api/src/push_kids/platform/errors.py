class AppError(Exception):
    status_code = 400
    code = "bad_request"

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class NotFoundError(AppError):
    status_code = 404
    code = "not_found"


class UnauthorizedError(AppError):
    status_code = 401
    code = "unauthenticated"


class ForbiddenError(AppError):
    status_code = 403
    code = "forbidden"


class ConflictError(AppError):
    status_code = 409
    code = "conflict"


class ClientUpgradeRequiredError(ConflictError):
    code = "client_upgrade_required"


class ReviewStateChangedError(ConflictError):
    code = "review_state_changed"


class ConsentRequiredError(AppError):
    """The request is valid but needs one more explicit human decision before it may proceed."""

    status_code = 409
    code = "consent_required"


class GoneError(AppError):
    status_code = 410
    code = "gone"


class TooManyRequestsError(AppError):
    status_code = 429
    code = "rate_limited"


class DependencyError(AppError):
    status_code = 503
    code = "dependency_failed"
