import http.server
import socketserver
import os
import webview
import sys
import threading

import webview.window

PORT = 8000

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = 'setup.html'

        if self.path == '/tc':
            self.path = 'tc.html'

        if self.path == '/options':
            self.path = 'options.html'

        if self.path == '/installation':
            self.path = 'installation.html'

        if self.path == '/done':
            self.path = 'done.html'

        if self.path == '/done':
            self.path = 'done.html'

        if self.path == '/exit':
            print("Exiting")
            window.destroy()
            sys.exit(1)

        if self.path == '/launch':
            print("Exiting")
            window.destroy()
            sys.exit(0)

        return super().do_GET()

    def translate_path(self, path):
        path = super().translate_path(path)
        return os.path.join(SCRIPT_DIR, os.path.relpath(path, os.getcwd()))

def run_http_server():
    with socketserver.TCPServer(("", PORT), CustomHTTPRequestHandler) as httpd:
        url = f"http://localhost:{PORT}"
        print(f"Serving setup.html on {url}")
        httpd.serve_forever()

server_thread = threading.Thread(target=run_http_server)
server_thread.daemon = True
server_thread.start()

url = f"http://localhost:{PORT}"

window = webview.create_window(
    'Novodo Installer',
    url,
    width=750,
    height=850,
    resizable=False,
    frameless=True,
    fullscreen=True
)

webview.start()

server_thread.join()