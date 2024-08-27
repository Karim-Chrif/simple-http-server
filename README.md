# Simple HTTP Server

This project provides a simple HTTP server implementation in Python. The server is capable of handling basic HTTP requests and routing them based on predefined routes. It also supports basic authorization handling.

## Features

- **HTTP Request Handling**: Handles `GET` requests and routes them to appropriate handlers.
- **Custom Authorization**: Allows the developer to provide a custom authorization handler.
- **Extensible Routing**: Easily add or modify routes and handlers.

## Installation

1. **Clone the Repository**:

    ```sh
    git clone https://github.com/Karim-Chrif/simple-http-server.git
    ```

2. **Navigate to the Project Directory**:

    ```sh
    cd simple-http-server
    ```

3. **Create a Virtual Environment** (optional but recommended):

    ```sh
    python -m venv venv
    ```

4. **Activate the Virtual Environment**:

    - On Windows:

        ```sh
        venv\Scripts\activate
        ```

    - On macOS/Linux:

        ```sh
        source venv/bin/activate
        ```

5. **Install Dependencies**:

    ```sh
    pip install -r requirements.txt
    ```

## Usage

1. **Define Route Handlers**:

    In `server.py`, define functions to handle specific routes. For example:

    ```python
    def handle_root():
        return Response(200, {'message': 'Hello, world!'})

    def handle_about():
        return Response(200, {'message': 'This is the about page'})
    ```

2. **Create and Start the Server**:

    ```python
    from server import Server

    def custom_auth_handler(headers):
        # Implement your authorization logic here
        return 'Authorization' in headers

    if __name__ == '__main__':
        routes = [
            ('GET', '/', handle_root),
            ('GET', '/about', handle_about),
            # Add more routes here
        ]
        server = Server(routes, auth_handler=custom_auth_handler, host='0.0.0.0', port=65432)
        server.start()
    ```

3. **Run the Server**:

    Execute the server script:

    ```sh
    python server.py
    ```

## Configuration

- **Routes**: Add or modify routes in the `routes` list.
- **Authorization**: Provide a custom authorization function to the `Server` class.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

For any questions or comments, please reach out to [carimshrif@gmail.com](mailto:carimshrif@gmail.com).

