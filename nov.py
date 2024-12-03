from waitress import serve
from server import app
from PIL import Image
import socket
import qrcode
import json
import os

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

def get_current_ip():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            ip_address = s.getsockname()[0]
        return ip_address
    except Exception as e:
        return f"Error: {e}"

def load_config():
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def is_headless():
    return os.getenv("DISPLAY") is None and os.getenv("WAYLAND_DISPLAY") is None and os.getenv("MIR_SOCKET") is None and OS_TYPE == "linux"

if __name__ == '__main__':
    if os.name == "nt":
        OS_TYPE = "windows"
    elif os.name == "posix":
        OS_TYPE = "linux"

    CONFIG_FILE = "config.json"

    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    
    headless = is_headless()

    config = load_config()

    port = config["sections"][1]["options"][1]["value"]

    broadcast = config["sections"][1]["options"][0]["value"]

    host = '127.0.0.1'
    message = f"Hosting on http://127.0.0.1:{port}/ or \"http://localhost:{port}/\""

    generate_qr_code = False
    qr_path = os.path.join(SCRIPT_DIR, "qr.png")
    
    if broadcast:
        host = '0.0.0.0'
        current_ip = get_current_ip()
        generate_qr_code = True

        url = f"http://{current_ip}:{port}/"

        message = f"Hosting on http://127.0.0.1:{port}/ or \"http://localhost:{port}/\" or \"{url}\"\nEnter one of these URLs on another device connected to the same network or scan the QR code below:\n\n"
    
    elif not broadcast and headless:
        host = '0.0.0.0'
        current_ip = get_current_ip()
        generate_qr_code = True

        url = f"\"http://{current_ip}:{port}/\""

        message = f"Broadcast setting is off but a headless environment has been detected, must be acessed remotely for intended use.\nHosting on \"{url}\"\nEnter this URL on another device connected to the same network or scan the QR code below:\n\n"

    print(message)

    if generate_qr_code:
        display_image_in_terminal(qr_path, 2, invert=True)
        qr_path = os.path.join(SCRIPT_DIR, "qr.png")
        gen_qr(url, qr_path)

    serve(app, host=host, port=port)
