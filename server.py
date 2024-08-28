import json
import socket
import signal
import sys
from datetime import datetime
from typing import Callable, List, Optional, Tuple
from request import Request
from response import Response
from route import Route

# Define status messages
STATUS_MESSAGES = {
    200: 'OK',
    400: 'Bad Request',
    403: 'Forbidden',
    404: 'Not Found'
}

def log_message(message: str) -> None:
    """
    Logs a message with a timestamp.

    Args:
        message (str): The message to log.
    """
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {message}")

class Server:
    """
    A simple HTTP server that handles incoming requests and routes them based on predefined routes.

    Attributes:
        host (str): The host IP address to bind the server.
        port (int): The port number to bind the server.
        sock (socket.socket): The socket object used for communication.
        running (bool): Flag indicating whether the server is running.
        routes (List[Route]): List of Route objects containing HTTP method, path, and handler functions.
        auth_handler (Optional[Callable[[dict], bool]]): Optional function to handle authorization checks.
    """

    def __init__(self, routes: List[Route], auth_handler: Optional[Callable[[dict], bool]] = None, host: str = '0.0.0.0', port: int = 65432):
        """
        Initializes the server with the given routes, host, and port.

        Args:
            routes (List[Route]): List of Route objects.
            auth_handler (Optional[Callable[[dict], bool]]): Function to handle authorization checks (default is None).
            host (str): Host IP address to bind the server (default is '0.0.0.0').
            port (int): Port number to bind the server (default is 65432).
        """
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.running = False
        self.routes = routes
        self.auth_handler = auth_handler

    def signal_handler(self, sig: int, frame: any) -> None:
        """
        Handles the SIGINT signal (Ctrl+C) to gracefully shut down the server.

        Args:
            sig (int): Signal number.
            frame (signal.FrameType): Current stack frame.
        """
        log_message("KeyboardInterrupt detected. Shutting down...")
        self.running = False
        self.shutdown()
        sys.exit(0)

    def start(self) -> None:
        """
        Starts the server, listens for incoming connections, and handles requests.
        """
        self.sock.bind((self.host, self.port))
        self.sock.listen()
        log_message(f'Server started on {self.host}:{self.port}')
        self.running = True
        signal.signal(signal.SIGINT, self.signal_handler)
        
        while self.running:
            try:
                self.sock.settimeout(1.0)
                conn, addr = self.sock.accept()
                self.handle_request(conn, addr)
            except socket.timeout:
                continue
            except Exception as e:
                log_message(f"An error occurred: {e}")
                self.running = False

        self.shutdown()

    def handle_request(self, conn: socket.socket, addr: Tuple[str, int]) -> None:
        """
        Handles a single incoming request by parsing it and routing it to the appropriate handler.

        Args:
            conn (socket.socket): The connection object to handle the request.
            addr (Tuple[str, int]): The client IP address and port number.
        """
        with conn:
            try:
                data = conn.recv(1024).decode()
                if not data:
                    return
                
                request = Request.from_raw(data)

                if 'Content-Type' in request.headers and request.headers['Content-Type'] != 'application/json':
                    response = Response(400, {'error': 'Invalid Content-Type'})
                    self.send_response(conn, response)
                    log_message(f"Request from {addr[0]} for {request.path} resulted in 400 Bad Request")
                    return                    
            except ValueError:
                response = Response(400, {'error': 'Invalid request format'})
                self.send_response(conn, response)
                log_message(f"Request from {addr[0]} for {request.path} resulted in 400 Bad Request")
                return

            # Authorization
            if self.auth_handler and not self.auth_handler(request.headers):
                response = Response(403, {'error': 'Forbidden'})
                self.send_response(conn, response)
                log_message(f"Request from {addr[0]} for {request.path} resulted in 403 Forbidden")
                return
            
            # Find matching route
            for route in self.routes:
                if route.matches(request.method, request.path):
                    response = route.handler(request)
                    self.send_response(conn, response)
                    log_message(f"Request from {addr[0]} for {request.path} resulted in {response.status_code} {STATUS_MESSAGES.get(response.status_code, 'Unknown')}")
                    return
            
            # If no route matches
            response = Response(404, {'error': 'Route not found'})
            self.send_response(conn, response)
            log_message(f"Request from {addr[0]} for {request.path} resulted in 404 Not Found")

    def send_response(self, conn: socket.socket, response: Response) -> None:
        """
        Sends an HTTP response to the client.

        Args:
            conn (socket.socket): The connection object to send the response.
            response (Response): The Response object to be sent.
        
        Raises:
            ValueError: If the response is not an instance of the Response class.
        """
        if not isinstance(response, Response):
            raise ValueError("Expected a Response object")
        conn.sendall(response.to_http_response().encode('utf-8'))

    def shutdown(self) -> None:
        """
        Shuts down the server by closing the socket.
        """
        log_message("Shutting down the server...")
        self.sock.close()

def handle_root(request:Request) -> Response:
    """
    Handles requests to the root path '/'.

    Returns:
        Response: A Response object with status code 200 and a message.
    """
    return Response(200, {'message': 'Hello, world!','body':request.body})

def handle_about(request:Request) -> Response:
    """
    Handles requests to the '/about' path.

    Returns:
        Response: A Response object with status code 200 and a message.
    """
    return Response(200, {'message': 'This is the about page'})

def custom_auth_handler(headers: dict) -> bool:
    """
    Example authorization handler that checks for the presence of the 'Authorization' header.

    Args:
        headers (dict): Dictionary of request headers.

    Returns:
        bool: True if the 'Authorization' header is present, False otherwise.
    """
    return 'Authorization' in headers

if __name__ == '__main__':
    """
    This block of code demonstrates how to use the Server class.

    It sets up the server with example routes and starts it. The example routes include:
        - A root route ('/') that returns a "Hello, world!" message.
        - An '/about' route that returns a message about the page.

    The server will listen on all network interfaces (0.0.0.0) and port 65432.
    """
    routes = [
        Route('GET', '/', handle_root),
        Route('GET', '/about', handle_about),
        # Add more routes here
    ]
    server = Server(routes, auth_handler=custom_auth_handler, host='0.0.0.0', port=65432)
    server.start()
