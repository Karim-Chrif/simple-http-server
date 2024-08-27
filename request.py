class Request:
    """
    Represents an HTTP request.

    Attributes:
        method (str): The HTTP method of the request (e.g., 'GET').
        path (str): The URL path of the request (e.g., '/').
        headers (dict): The headers of the request.
        body (dict): The body of the request.
    """

    def __init__(self, method, path, headers=None, body=None):
        """
        Initializes the Request object with method, path, headers, and body.

        Args:
            method (str): The HTTP method of the request.
            path (str): The URL path of the request.
            headers (dict, optional): The headers of the request (default is an empty dictionary).
            body (dict, optional): The body of the request (default is an empty dictionary).
        """
        self.method = method
        self.path = path
        self.headers = headers or {}
        self.body = body or {}

    @classmethod
    def from_raw(cls, raw_data):
        """
        Creates a Request object from raw HTTP request data.

        Args:
            raw_data (str): The raw HTTP request data as a string.

        Returns:
            Request: The Request object created from the raw data.
        """
        try:
            headers, body = raw_data.split('\r\n\r\n', 1)
            request_line, *header_lines = headers.split('\r\n')
            method, path, _ = request_line.split()
            
            header_dict = {}
            for line in header_lines:
                if ': ' in line:
                    key, value = line.split(': ', 1)
                    header_dict[key] = value
            
            return cls(method, path, header_dict, body)
        except ValueError:
            return cls('', '', {}, '')
