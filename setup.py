import os
import sys
import ctypes
import subprocess
import traceback
import tkinter as tk
from tkinter import messagebox

# Check if the user is an admin
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except AttributeError:
        return os.geteuid() == 0

# Elevate privileges if necessary
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

# Check if pip is installed
def check_pip_installed():
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', '--version'])
        print("pip is installed.")
        return True
    except subprocess.CalledProcessError:
        print("pip is not installed.")
        return False
    except FileNotFoundError:
        print("Python is not installed correctly, or there's an issue with your environment.")
        return False

# Install pip if not installed
def install_pip():
    if sys.platform == "win32":
        subprocess.check_call([sys.executable, "-m", "ensurepip", "--upgrade"])
    elif sys.platform == "linux" or sys.platform == "linux2":
        subprocess.check_call([sys.executable, "-m", "ensurepip", "--upgrade"])
    else:
        print(f"Unsupported platform: {sys.platform}")
        return
    print("pip installation complete.")

def upgrade_pip():
    try:
        # Run the pip upgrade command
        result = subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], check=True)
        if result.returncode == 0:
            print("Successfully upgraded pip.")
        else:
            print("Failed to upgrade pip.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while upgrading pip: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

# Restart the script to recognize pip
def restart_script():
    print("Restarting the script to recognize pip...")
    python = sys.executable
    os.execv(python, [python] + sys.argv)

# Install required packages
def install_needed():
    try:
        import requests
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
        restart_script()

# Get the logged-in user's directory
def get_logged_in_user_dir():
    if os.name == 'nt':
        user_dir = os.environ.get('USERPROFILE', '')
    else:
        user_dir = os.environ.get('HOME', '')

    return user_dir

def install_requirements_file(path):
    subprocess.run([ 'pip', 'install', '-r', path], check=True)

# Tkinter Yes/No dialog
def ask_yes_no(title, question):
    response = messagebox.askyesno(title, question)
    return response

# Main function to run the program
def main():
    if not check_pip_installed():
        if ask_yes_no("Install pip?", "pip is not installed. Do you want to install it now?"):
            install_pip()
            upgrade_pip()
            restart_script()
        else:
            print("pip is needed for setup. Exiting.")
            sys.exit(1)

    install_needed()

    import requests
    
    user_directory = get_logged_in_user_dir()
    nov_path = os.path.join(user_directory, "novodo")
    os.makedirs(nov_path, exist_ok=True)

    requirements_path = os.path.join(nov_path, "requirements.txt")
    url = "https://raw.githubusercontent.com/NovodoOfficial/novodo-packages/main/requirements.txt"

    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to download requirements file. Status code: {response.status_code}")
        messagebox.showerror("Error", "Failed to download requirements file. Exiting.")
        sys.exit(1)

    with open(requirements_path, 'wb') as file:
        file.write(response.content)

    install_requirements_file(requirements_path)

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()

    if not elevate_privileges():
        messagebox.showerror("Error", "This script requires administrative privileges to run.")
        sys.exit(1)
    else:
        try:
            main()
            
        except Exception as e:
            print("An error occurred")
            traceback.print_exc()
            messagebox.showerror("Error", "An error occurred during execution.")
            sys.exit(1)
