# app/core/exceptions.py


class DomainError(Exception):
    code: str = "DOMAIN_ERROR"
    message: str = "An error occurred"
    status_code: int = 400

    def __init__(self, message: str | None = None) -> None:
        if message is not None:
            self.message = message
        super().__init__(self.message)
