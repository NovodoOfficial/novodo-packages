import http.server
import socketserver
import os
import webview
import sys
import threading
import subprocess

PORT = 8000
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
httpd = None

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = 'setup.html'
        elif self.path == '/tc':
            self.path = 'tc.html'
        elif self.path == '/options':
            self.path = 'options.html'
        elif self.path == '/installation':
            self.path = 'installation.html'
            install()
            # install plugins
        elif self.path == '/done':
            self.path = 'done.html'
        elif self.path == '/exit':
            print("Exiting")
            shutdown()
        elif self.path == '/launch':
            print("Launching")
            shutdown()
        return super().do_GET()

    def translate_path(self, path):
        path = super().translate_path(path)
        return os.path.join(SCRIPT_DIR, os.path.relpath(path, os.getcwd()))

def install():
    def piptest():
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "--version"])
        except subprocess.CalledProcessError:
            try:
                subprocess.check_call([sys.executable, "-m", "ensurepip", "--default-pip"])
            except Exception as e:
                print(f"Failed to install pip: {e}")
                shutdown()
    piptest()

    requirements = [
        "pillow"
    ]

    for i in requirements:
        os.sytem("pip install", i)
        # feed back to html so that the text can say installing x... or update percent

    dots = ["/", "──", "\\", "|"]

    for a in range(50):
        for b in dots:
            print(f"Loading {b}")

    # requirements_string = " ".join(requirements)

    # os.system(f"pip install {requirements_string}")

    
def shutdown(code=0):
    window.destroy()
    cleanup()
    print("TEST")
    sys.exit(code)

def cleanup():
    if httpd:
        # fix shutdown
        httpd.server_close()

def run_http_server():
    global httpd
    httpd = socketserver.TCPServer(("", PORT), CustomHTTPRequestHandler)
    url = f"http://localhost:{PORT}"
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

try:
    webview.start()
finally:
    cleanup()
