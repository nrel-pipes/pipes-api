class CognitoAuthError(Exception):
    """Raise when Cognito authentication failed."""


class ContextValidationError(Exception):
    """Raise when given context validation failed"""


class UserPermissionDenied(Exception):
    """Raise when user does not have permission"""


class DocumentDoesNotExist(Exception):
    """Raise when user does not exist in docdb."""


class DocumentAlreadyExists(Exception):
    """Raise when user already exists in docdb."""


class VertextDoesNotExist(Exception):
    """Raise when a vertex does not exist in graphdb."""


class VertexAlreadyExists(Exception):
    """Raise when a vertex already exists in graphdb."""
