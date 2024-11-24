import http.server
import socketserver
import socket
import threading
import subprocess
import json
import argparse
import ctypes
import os
import sys
from tkinter import messagebox

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, os.path.join(SCRIPT_DIR, "requirements"))

try:
    import webview
    import qrcode
    from PIL import Image
finally:
    sys.path.pop(0)

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except AttributeError:
        return os.geteuid() == 0

def elevate_privileges():
    if is_admin():
        return True

    if sys.platform == "win32":
        script = sys.executable
        params = ' '.join([f'"{arg}"' for arg in sys.argv])
        try:
            ctypes.windll.shell32.ShellExecuteW(None, "runas", script, params, None, 1)
            sys.exit()
        except Exception as e:
            print(f"Failed to gain admin privileges: {e}")
            return False

    elif sys.platform in ("linux", "darwin"):
        try:
            print("Attempting to run with sudo...")
            subprocess.check_call(["sudo", sys.executable] + sys.argv)
            sys.exit()
        except subprocess.CalledProcessError as e:
            print(f"Failed to gain admin privileges: {e}")
            return False

    else:
        print("Unsupported OS.")
        return False

if not elevate_privileges():
    messagebox.showerror("Error", "This script requires administrative privileges to run.")
    sys.exit(1)

parser = argparse.ArgumentParser()

parser.add_argument('--restart_install', action="store_true", help="Restart the script to install page")

args = parser.parse_args()

restart_install = False

if args.restart_install:
    restart_install = True

if restart_install:
    print("SKIPPING TO INSTALL")

install_progress = 0
install_step = "..."
progress_lock = threading.Lock()

PORT = 49500
httpd = None

if os.name == "nt":
    OS_TYPE = "windows"
elif os.name == "posix":
    OS_TYPE = "linux"

def clear_screen():
    if OS_TYPE == "windows":
        os.system("cls")
    if OS_TYPE == "linux":
        os.system("clear")

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

def install_requirement(type, package, requirementPercentage, index):
    if type == "pip":
        requirement = package

        requirementCapitalize = requirement.capitalize()

        command = "pip install " + requirement

        os.system(command)

    elif type == "other":
        if package == "pip":
            requirementCapitalize = "pip"

            try:
                result = subprocess.run([sys.executable, "-m", "pip", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

                if not result.returncode == 0:
                    subprocess.run([sys.executable, "-m", "ensurepip", "--default-pip"])
                    restart(["--restart_install"])
                    
            except Exception as e:
                print(f"Error installing pip:\n{e}")
                shutdown()

        elif package == "choco":
            requirementCapitalize = "Chocolatey"
            
            def is_choco_installed():
                try:
                    result = subprocess.run(["choco", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                    if result.returncode == 0:
                        return True
                except FileNotFoundError:
                    return False

            def install_choco():
                download_script_cmd = "curl --ssl-no-revoke -o install.ps1 https://community.chocolatey.org/install.ps1"

                install_ps_script_cmd = (
                    "powershell -NoProfile -ExecutionPolicy Bypass -File install.ps1"
                )

                cleanup_cmd = "del install.ps1"

                try:
                    subprocess.run(download_script_cmd, check=True, shell=True)
                    
                    subprocess.run(install_ps_script_cmd, check=True, shell=True)
                    
                    subprocess.run(cleanup_cmd, check=True, shell=True)
                except Exception as e:
                    print(f"Error installing choco:\n{e}")
                    shutdown()

            if not is_choco_installed():
                install_choco()
                restart(["--restart_install"])

        elif package == "node.js":
            requirementCapitalize = "Node JS"

            def is_node_installed():
                try:
                    result = subprocess.run(["node", "-v"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                    if result.returncode == 0:
                        return True
                except FileNotFoundError:
                    return False
            
            if not is_node_installed():
                if OS_TYPE == "windows":
                    try:
                        subprocess.run(["choco", "install", "nodejs", "-y"], check=True)
                    except Exception as e:
                        print(f"Error installing choco:\n{e}")
                        shutdown()

                elif OS_TYPE == "linux":
                    try:
                        if os.path.exists("/usr/bin/apt"):
                            subprocess.run(["sudo", "apt", "update"], check=True)
                            subprocess.run(["sudo", "apt", "install", "-y", "nodejs", "npm"], check=True)
                        elif os.path.exists("/usr/bin/yum"):
                            subprocess.run(["sudo", "yum", "install", "-y", "nodejs", "npm"], check=True)
                        elif os.path.exists("/usr/local/bin/brew"):
                            subprocess.run(["brew", "install", "node"], check=True)
                        else:
                            print(f"Unsupported package manager:\n{e}")
                            shutdown()
                    except Exception as e:
                        print(f"Error installing choco:\n{e}")
                        shutdown()

                restart(["--restart_install"])

    requirementProgress = requirementPercentage * index

    return requirementCapitalize, requirementProgress

def install():
    global install_progress
    global install_step

    requirements = [
        {
            "type": "other",
            "package": "pip"
        },
        {
            "type": "other",
            "package": "choco"
        },
        {
            "type": "other",
            "package": "node.js"
        },
        {
            "type": "pip",
            "package": "pygithub"
        },
        {
            "type": "pip",
            "package": "requests"
        },
        {
            "type": "pip",
            "package": "pywebview"
        }
    ]

    requirementCount = len(requirements)
    requirementPercentage = 100 / requirementCount
    requirementProgress = 0

    for index, requirement in enumerate(requirements):
        requirementCapitalize, requirementProgress = install_requirement(requirement["type"], requirement["package"], requirementPercentage, index)

        with progress_lock:
            install_step = requirementCapitalize
            install_progress = requirementProgress

    requirementProgress = 100

    with progress_lock:
        install_step = "finished"
        install_progress = requirementProgress

def shutdown(code=0):
    if not broadcast:
        window.destroy()
    cleanup()
    sys.exit(code)

def restart(args):
    print(f"RESTARTING\nRestart args: {", ".join(args)}")

    if not broadcast:
        window.destroy()
    cleanup()

    try:
        script_path = os.path.abspath(__file__)
        python = sys.executable

        if os.name == "nt":
            subprocess.Popen(["start", python, script_path] + args, shell=True)
        elif os.name == "posix":
            subprocess.Popen(["x-terminal-emulator", "-e", python, script_path] + args)
        
        sys.exit(0)
    except Exception as e:
        print(f"Error restarting script: {e}")
        sys.exit(1)

def cleanup():
    if httpd:
        httpd.shutdown()
        httpd.server_close()

def run_http_server(ip_address):
    global httpd
    print(f"Starting HTTP server at {ip_address}:{PORT}...")
    try:
        cleanup()

        httpd = socketserver.TCPServer((ip_address, PORT), CustomHTTPRequestHandler)

        print("NEW INSTANCE")

        httpd.serve_forever()
    except Exception as e:
        print(f"Error starting server: {e}")

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        s.connect(('8.8.8.8', 80))
        ip_address = s.getsockname()[0]
    except Exception:
        ip_address = '127.0.0.1'
    finally:
        s.close()
    return ip_address

def gen_qr(data, path):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=1,
        border=1,
    )

    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill='black', back_color='white')

    img.save(path)

def display_image_in_terminal(image_path, width_multiplier=1, height_multiplier=1, invert=False):
    blank, fill = " ", "█"

    if invert:
        blank, fill = "█", " "

    img = Image.open(image_path)

    img = img.convert('L')

    width, height = img.size

    for y in range(height):
        row = ""
        for x in range(width):
            brightness = img.getpixel((x, y))

            if brightness < 127:
                row += blank * width_multiplier
            else:
                row += fill * width_multiplier
        
        for i in range(height_multiplier):
            print(row)

ip_address = '127.0.0.1'

def is_headless():
    return os.getenv("DISPLAY") is None and os.getenv("WAYLAND_DISPLAY") is None and os.getenv("MIR_SOCKET") is None and OS_TYPE == "linux"

broadcast = is_headless()

broadcast = True

if broadcast:
    ip_address = get_local_ip()

server_thread = threading.Thread(target=run_http_server, args=(ip_address,))
server_thread.daemon = True
server_thread.start()

suffix = ""

if restart_install:
    suffix = "installation"

url = f"http://{ip_address}:{PORT}/{suffix}"

window = webview.create_window(
    'Novodo Installer',
    url,
    width=710,
    height=780,
    resizable=False,
    fullscreen=True
)

try:
    if not broadcast:
        webview.start()
    else:
        if not restart_install:
            print(f"A headless environment has been detected, enter this url on another device connected to the same network:\n{url}\n\nOr scan the QR code below:\n\n")

            qr_path = os.path.join(SCRIPT_DIR, "qr.png")
            gen_qr(url, qr_path)
            display_image_in_terminal(qr_path, 2, invert=True)

        while True:
            pass
finally:
    cleanup()
