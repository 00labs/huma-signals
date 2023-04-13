class HumaSignalException(Exception):
    def __init__(self, message: str) -> None:
        super().__init__()
        self.message = message

    def __str__(self) -> str:
        return self.message

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}: {self.message}"


class RequestException(HumaSignalException):
    def __init__(self, message: str) -> None:
        super().__init__(message=message)
