class HumaSignalException(Exception):
    def __init__(self, message: str) -> None:
        super().__init__()
        self.message = message

    def __str__(self) -> str:
        return self.message

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}: {self.message}"


class InvalidAddressException(HumaSignalException):
    def __init__(self, message: str) -> None:
        super().__init__(message=message)


class PoolSettingsNotFoundException(HumaSignalException):
    def __init__(self, pool_address: str) -> None:
        super().__init__(
            message=f"No pool settings registered for pool address {pool_address}"
        )


class ContractCallFailedException(HumaSignalException):
    def __init__(self, message: str) -> None:
        super().__init__(message=message)


class RequestException(HumaSignalException):
    def __init__(self, message: str) -> None:
        super().__init__(message=message)


class SuperfluidException(HumaSignalException):
    def __init__(self, message: str) -> None:
        super().__init__(message=message)


class SuperfluidStreamNotFoundException(SuperfluidException):
    pass
