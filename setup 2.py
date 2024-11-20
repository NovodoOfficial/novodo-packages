from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse
import os

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Serve the setup/setup.html file
        file_path = 'setup/setup.html'
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as file:
                html_content = file.read()
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(html_content.encode('utf-8'))
        else:
            # Return a 404 error if the file doesn't exist
            self.send_response(404)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"<h1>404 - File Not Found</h1>")

    def do_POST(self):
        # Handle form submission and print the result in the terminal
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        # Parse the form data
        form_data = urllib.parse.parse_qs(post_data.decode('utf-8'))
        user_input = form_data.get('user_input', [''])[0]  # Get the input value
        print(f"User Input: {user_input}")  # Print the input in the terminal

        # Serve the done.html file
        file_path = 'done.html'
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as file:
                html_content = file.read()
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(html_content.encode('utf-8'))
        else:
            # Return a 404 error if the file doesn't exist
            self.send_response(404)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"<h1>404 - Done File Not Found</h1>")

# Run the server
def run(server_class=HTTPServer, handler_class=RequestHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Server started on port {port}. Open http://localhost:{port} in your browser.")
    httpd.serve_forever()

if __name__ == "__main__":
    run()
