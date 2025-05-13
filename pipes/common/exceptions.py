class CognitoAuthError(Exception):
    """Raise when Cognito authentication failed."""


class ContextValidationError(Exception):
    """Raise when given context validation failed"""


class DomainValidationError(Exception):
    """Raise when given domain validation failed"""


class UserPermissionDenied(Exception):
    """Raise when user does not have permission"""


class DocumentDoesNotExist(Exception):
    """Raise when user does not exist in docdb."""


class DocumentAlreadyExists(Exception):
    """Raise when user already exists in docdb."""

class CognitoUserAlreadyExists(Exception):
    """Raise when user already exists in docdb."""

class CognitoDoesNotExists(Exception):
    """Raise when user already exists in docdb."""

class EdgeDoesNotExist(Exception):
    """Raise when an edge does not exist in graph db."""


class EdgeAlreadyExists(Exception):
    """Raise when an edge already exists in graph db."""


class VertextDoesNotExist(Exception):
    """Raise when a vertex does not exist in graphdb."""


class VertexAlreadyExists(Exception):
    """Raise when a vertex already exists in graphdb."""
