class WebDAVException(Exception):
    pass

class UnauthorizedException(WebDAVException):
    def __init__(self, method, path, kwargs):
        self.method = method
        self.path = path
        self.kwargs = kwargs

    def __str__(self) -> str:
        return f"Unauthorized request: {self.method} to {self.path}"

class RemoteResourceNotFoundException(WebDAVException):
    def __init__(self, remote_path):
        self.remote_path = remote_path

    def __str__(self) -> str:
        return f"Remote resource not found: {self.remote_path}"