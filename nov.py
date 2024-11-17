from waitress import serve
from server import app
import json
import socket

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

if __name__ == '__main__':
    CONFIG_FILE = "config.json"

    config = load_config()

    port = config["sections"][1]["options"][1]["value"]

    broadcast = config["sections"][1]["options"][0]["value"]

    host = '127.0.0.1'
    message = "Hosting on http://127.0.0.1/ or \"http://localhost/\""

    if broadcast:
        host = '0.0.0.0'
        current_ip = get_current_ip()
        message = f"Hosting on http://127.0.0.1/ or \"http://localhost/\" or {current_ip}"

    print(message)

    serve(app, host=host, port=port)
