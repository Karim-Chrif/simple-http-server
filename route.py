from typing import Callable

from response import Response

class Route:
    """
    Represents a route in the HTTP server, including method, path, and handler.

    Attributes:
        method (str): HTTP method (e.g., 'GET').
        path (str): URL path (e.g., '/').
        handler (Callable[[], Response]): Function to handle requests matching this route.
    """

    def __init__(self, method: str, path: str, handler: Callable[[], Response]):
        """
        Initializes the Route with method, path, and handler.

        Args:
            method (str): HTTP method (e.g., 'GET').
            path (str): URL path (e.g., '/').
            handler (Callable[[], Response]): Function to handle requests matching this route.
        """
        self.method = method
        self.path = path
        self.handler = handler

    def matches(self, method: str, path: str) -> bool:
        """
        Checks if the route matches the given method and path.

        Args:
            method (str): HTTP method to check.
            path (str): URL path to check.

        Returns:
            bool: True if the route matches, False otherwise.
        """
        return self.method == method and self.path == path
