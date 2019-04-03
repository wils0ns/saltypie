class SaltConnectionError(Exception):
    """Raised when saltypie fails to connect to salt-'s web server"""
    pass


class SaltAuthenticationError(Exception):
    """Raised when saltypie fails to authentication against salt's web server"""
    pass


class SaltReturnParseError(Exception):
    """Raised when saltypie is unable to parse the returned content of an API call."""
    pass

