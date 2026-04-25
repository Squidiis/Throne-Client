class ThroneError(Exception):
    """Base exception for all Throne SDK errors."""
    pass

class WishlistNotFoundError(ThroneError):
    """Raised when the username doesn't exist on Throne."""
    pass

class ThroneRateLimitError(ThroneError):
    """Raised when Throne blocks us for too many requests (429)."""
    pass

class ThroneConnectionError(ThroneError):
    """Raised when the browser fails to start or the page won't load."""
    pass