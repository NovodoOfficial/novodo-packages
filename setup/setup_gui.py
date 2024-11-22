import http.server
import socketserver
import os
import webview
import sys
import threading
import subprocess
import json

install_progress = 0
install_step = "..."
progress_lock = threading.Lock()

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
            threading.Thread(target=install).start()
            self.path = 'installation.html'
        elif self.path == '/done':
            self.path = 'done.html'
        elif self.path == '/exit':
            print("Exiting")
            shutdown()
        elif self.path == '/launch':
            print("Launching")
            shutdown()
        
        return super().do_GET()

    def do_POST(self):
        if self.path == '/progress':
            print("POST request for progress received")

            response = {
                "progress": install_progress,
                "step": f"Installing {install_step}"
            }

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(response).encode("utf-8"))

            return
        
        super().do_POST()

    def translate_path(self, path):
        print(path)
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
    
    global install_progress
    global install_step

    """
    Add installation for pip, chocolatey, nodejs

    requirements = [
        {
            "type": "custom",
            "package": "pip"
        },
        {
            "type": "pip",
            "package": "requests"
        },
        {
            "type": "pip",
            "package": "requests"
        }
    ]
    """

    requirements = [
        "requests",
        "pygithub"
    ]
    
    requirementCount = len(requirements)
    requirementPercentage = 100 / requirementCount
    requirementProgress = 0

    for index, requirement in enumerate(requirements):
        requirementCapitalize = requirement.capitalize()
        
        requirementStr = "Installing " + requirementCapitalize + " ..."
        
        requirementProgress = requirementPercentage * index

        with progress_lock:
            install_step = requirementCapitalize
            install_progress = requirementProgress

        print(f"Requirements:\n{requirementStr}\nProgress:\n{requirementProgress}")
        
        command = "pip install " + requirement

        os.system(command)

    requirementProgress = 100

    print(f"Requirements:\n{requirementStr}\nProgress:\n{requirementProgress}")

    with progress_lock:
        install_progress = requirementProgress

def shutdown(code=0):
    window.destroy()
    cleanup()
    sys.exit(code)

def cleanup():
    if httpd:
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
