class CustomException(Exception):
    """Base class for all custom exceptions in the application."""
    pass

class NotFoundException(CustomException):
    """Exception raised when a resource is not found."""
    def __init__(self, message="Resource not found"):
        self.message = message
        super().__init__(self.message)

class ValidationException(CustomException):
    """Exception raised for validation errors."""
    def __init__(self, message="Validation error"):
        self.message = message
        super().__init__(self.message)

class UnauthorizedException(CustomException):
    """Exception raised for unauthorized access."""
    def __init__(self, message="Unauthorized access"):
        self.message = message
        super().__init__(self.message)

class ConflictException(CustomException):
    """Exception raised for conflicts in the application."""
    def __init__(self, message="Conflict occurred"):
        self.message = message
        super().__init__(self.message)