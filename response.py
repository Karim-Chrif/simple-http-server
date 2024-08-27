import json

class Response:
    """
    Represents an HTTP response.

    Attributes:
        status_code (int): The HTTP status code of the response.
        status_text (str): The HTTP status text corresponding to the status code.
        content (dict): The content to be included in the response body.
    """

    status_messages = {200: 'OK', 400: 'Bad Request', 404: 'Not Found'}

    def __init__(self, status_code, content=None):
        """
        Initializes the Response object with status code and content.

        Args:
            status_code (int): The HTTP status code of the response.
            content (dict, optional): The content to include in the response body (default is an empty dictionary).
        """
        self.status_code = status_code
        self.status_text = self.status_messages.get(status_code, 'Unknown')
        self.content = content or {}

    def to_http_response(self):
        """
        Converts the Response object to an HTTP response string.

        Returns:
            str: The HTTP response string.
        """
        response = f"HTTP/1.1 {self.status_code} {self.status_text}\r\n"
        response += "Content-Type: application/json\r\n\r\n"
        response += json.dumps(self.content)
        return response
