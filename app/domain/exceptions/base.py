class AppException(Exception):
    """Excepción raíz del dominio. Todas las fallas de negocio heredan de aquí."""

    def __init__(self, message: str, code: str = "APP_ERROR", status_code: int = 400) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code


class NotFoundException(AppException):
    def __init__(self, message: str = "Recurso no encontrado", code: str = "NOT_FOUND") -> None:
        super().__init__(message, code=code, status_code=404)


class UnauthorizedException(AppException):
    def __init__(self, message: str = "No autenticado", code: str = "UNAUTHORIZED") -> None:
        super().__init__(message, code=code, status_code=401)


class ForbiddenException(AppException):
    def __init__(self, message: str = "No autorizado", code: str = "FORBIDDEN") -> None:
        super().__init__(message, code=code, status_code=403)


class ValidationException(AppException):
    def __init__(self, message: str = "Datos inválidos", code: str = "VALIDATION_ERROR") -> None:
        super().__init__(message, code=code, status_code=422)


class ConflictException(AppException):
    def __init__(self, message: str = "Conflicto de recurso", code: str = "CONFLICT") -> None:
        super().__init__(message, code=code, status_code=409)
