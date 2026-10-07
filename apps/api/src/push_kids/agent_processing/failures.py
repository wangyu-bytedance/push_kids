"""Safe, content-free operational failure categories shared by analysis stages."""


class StageFailure(Exception):
    def __init__(
        self,
        reason: str,
        *,
        retryable: bool = True,
        retry_after: int = 0,
        stage: str = "",
        unit: str = "",
    ):
        self.reason = reason
        self.retryable = retryable
        self.retry_after = max(0, min(60, retry_after))
        self.stage, self.unit = stage, unit
        super().__init__(reason)
