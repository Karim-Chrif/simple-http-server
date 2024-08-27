import socket
import signal
import sys
from request import Request
from response import Response

class Server:
    """
    A simple HTTP server that handles incoming requests and routes them based on predefined routes.

    Attributes:
        host (str): The host IP address to bind the server.
        port (int): The port number to bind the server.
        sock (socket.socket): The socket object used for communication.
        running (bool): Flag indicating whether the server is running.
        routes (list): List of tuples containing HTTP method, path, and handler functions.
    """

    def __init__(self, routes, host='0.0.0.0', port=65432):
        """
        Initializes the server with the given routes, host, and port.

        Args:
            routes (list): List of tuples where each tuple contains:
                - method (str): HTTP method (e.g., 'GET').
                - path (str): URL path (e.g., '/').
                - handler (callable): Function to handle requests matching this route.
            host (str): Host IP address to bind the server (default is '0.0.0.0').
            port (int): Port number to bind the server (default is 65432).
        """
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.running = False
        self.routes = routes

    def signal_handler(self, sig, frame):
        """
        Handles the SIGINT signal (Ctrl+C) to gracefully shut down the server.

        Args:
            sig (int): Signal number.
            frame (frame object): Current stack frame.
        """
        print("\nKeyboardInterrupt detected. Shutting down...")
        self.running = False
        self.shutdown()
        sys.exit(0)

    def start(self):
        """
        Starts the server, listens for incoming connections, and handles requests.
        """
        self.sock.bind((self.host, self.port))
        self.sock.listen()
        print(f'Server started on {self.host}:{self.port}')
        self.running = True
        signal.signal(signal.SIGINT, self.signal_handler)
        
        while self.running:
            try:
                self.sock.settimeout(1.0)
                conn, addr = self.sock.accept()
                print('Connected by', addr)
                self.handle_request(conn)
            except socket.timeout:
                continue
            except Exception as e:
                print(f"An error occurred: {e}")
                self.running = False

        self.shutdown()

    def handle_request(self, conn):
        """
        Handles a single incoming request by parsing it and routing it to the appropriate handler.

        Args:
            conn (socket.socket): The connection object to handle the request.
        """
        with conn:
            try:
                data = conn.recv(1024).decode()
                if not data:
                    return

                request = Request.from_raw(data)

            except ValueError:
                response = Response(400, {'error': 'Invalid request format'})
                self.send_response(conn, response)
                return

            # Find matching route
            for route_method, route_path, handler in self.routes:
                if request.method == route_method and request.path == route_path:
                    response = handler()
                    self.send_response(conn, response)
                    return
            
            # If no route matches
            response = Response(404, {'error': 'Route not found'})
            self.send_response(conn, response)

    def send_response(self, conn, response):
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

    def shutdown(self):
        """
        Shuts down the server by closing the socket.
        """
        print("\nShutting down the server...")
        self.sock.close()

def handle_root():
    """
    Handles requests to the root path '/'.

    Returns:
        Response: A Response object with status code 200 and a message.
    """
    return Response(200, {'message': 'Hello, world!'})

def handle_about():
    """
    Handles requests to the '/about' path.

    Returns:
        Response: A Response object with status code 200 and a message.
    """
    return Response(200, {'message': 'This is the about page'})

if __name__ == '__main__':
    """
    This block of code demonstrates how to use the Server class.

    It sets up the server with example routes and starts it. The example routes include:
        - A root route ('/') that returns a "Hello, world!" message.
        - An '/about' route that returns a message about the page.

    The server will listen on all network interfaces (0.0.0.0) and port 65432.
    """
    routes = [
        ('GET', '/', handle_root),
        ('GET', '/about', handle_about),
        # Add more routes here
    ]
    server = Server(routes, host='0.0.0.0', port=65432)
    server.start()
