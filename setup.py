import platform
import os
import sys
import ctypes
import subprocess
import traceback
import tkinter as tk
import importlib
import time
import json
import shutil
from tkinter import messagebox

def load_github_token():
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                config_data = json.load(f)
                
                if 'sections' not in config_data or not isinstance(config_data['sections'], list):
                    print("'sections' is missing or not a list.")
                    return None
                
                for section in config_data['sections']:
                    if 'name' in section and section['name'] == "Github":
                        if 'options' not in section or not isinstance(section['options'], list):
                            print("'options' is missing or not a list in the 'Github' section.")
                            return None
                        
                        for option in section['options']:
                            if 'name' in option and option['name'] == "Github token":
                                if 'value' in option:
                                    token = option['value']
                                    print(f"TOKEN DETECTED: {token}")
                                    return token if token else None
                                else:
                                    print("'value' is missing in the 'Github token' option.")
                                    return None
                
                print("GitHub section or token option not found in config.json.")
                return None
        except Exception as e:
            print(f"Error reading config.json: {e}")
            return None
    else:
        print("config.json not found.")
        return None

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
        result = subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], check=True)
        if result.returncode == 0:
            print("Successfully upgraded pip.")
        else:
            print("Failed to upgrade pip.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while upgrading pip: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

def restart_script():
    try:
        script_path = os.path.abspath(__file__)
        python = sys.executable

        if os.name == "nt":
            subprocess.Popen(["start", python, script_path], shell=True)
        elif os.name == "posix":
            subprocess.Popen(["x-terminal-emulator", "-e", python, script_path])
        
        sys.exit(0)
    except Exception as e:
        print(f"Error restarting script: {e}")
        sys.exit(1)

def extract_packages_from_requirements(file_path):
    packages = []
    
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if line and not line.startswith('#'):
                package_name = line.split('==')[0]
                packages.append(package_name)

    return packages

def check_for_packages(package_list):
    missing_packages = []

    for package in package_list:
        try:
            subprocess.run(
                ["pip", "show", package],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True
            )
        except subprocess.CalledProcessError:
            missing_packages.append(package)
    
    if not missing_packages:
        print("All packages are installed and recognized.")
        return

    print(f"Can't find packages: {', '.join(missing_packages)}\nRestarting now...")
    restart_script()

def install_needed():
    installed_something = False

    try:
        import requests
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
        installed_something = True

    try:
        from github import Github
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pygithub"])
        installed_something = True

    if installed_something:
        restart_script()

def get_logged_in_user_dir():
    if os.name == 'nt':
        user_dir = os.environ.get('USERPROFILE', '')
    else:
        user_dir = os.environ.get('HOME', '')

    return user_dir

def install_requirements_file(path):
    subprocess.run(['pip', 'install', '-r', path], check=True)

def ask_yes_no(title, question):
    response = messagebox.askyesno(title, question)
    return response

def download_and_extract_repo(repo_url: str, download_dir: str, github_token: str):
    try:
        import requests
        import zipfile
    except ImportError as e:
        print(f"Error importing libraries: {e}")
        return

    parts = repo_url.rstrip('/').split('/')
    owner, repo_name = parts[-2], parts[-1]
    
    api_url = f'https://github.com/{owner}/{repo_name}/archive/refs/heads/main.zip'
    
    headers = {}
    if github_token:
        headers['Authorization'] = f'token {github_token}'
    
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
    
    zip_file_path = os.path.join(download_dir, f'{repo_name}.zip')

    if os.path.exists(zip_file_path):
        response = ask_yes_no("Overwrite", "An installation of novodo packages already exists, overwite it? (Does not remove apps/librarys)")
        if not response:
            print(f"Skipping download of {repo_name}.zip.")
            return
        else:
            print(f"Overwriting {zip_file_path}.")
            os.remove(zip_file_path)

    try:
        print(f"Downloading {repo_name} repository...")
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        
        with open(zip_file_path, 'wb') as file:
            file.write(response.content)
        print(f"Repository {repo_name} downloaded successfully as ZIP.")
        
        print("Extracting ZIP file...")
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(download_dir)
        
        extracted_folder = os.path.join(download_dir, f'{repo_name}-main')
        if os.path.exists(extracted_folder):
            for item in os.listdir(extracted_folder):
                item_path = os.path.join(extracted_folder, item)
                if os.path.isdir(item_path):
                    shutil.move(item_path, download_dir)
                else:
                    shutil.move(item_path, download_dir)
            os.rmdir(extracted_folder)
            print(f"Moved contents from {extracted_folder} to {download_dir}.")
        
        os.remove(zip_file_path)
        print(f"ZIP file {zip_file_path} deleted.")
    
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while downloading: {e}")
    except zipfile.BadZipFile as e:
        print(f"Failed to extract ZIP file: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def create_scheduled_task():
    task_name = "NovodoPackagesTask"
    user_directory = get_logged_in_user_dir()
    nov_path = os.path.join(user_directory, "novodo")
    script_path = os.path.join(nov_path, "nov.vbs" if sys.platform == "win32" else "nov.sh")
    
    try:
        if sys.platform == "win32":
            command = (
                f'SchTasks /Create /SC ONLOGON /TN "{task_name}" '
                f'/TR "{script_path}" /RL HIGHEST /F'
            )
            subprocess.run(command, check=True, shell=True)
            print(f"Scheduled task '{task_name}' created successfully on Windows.")
        
        elif sys.platform in ("linux", "darwin"):
            cron_line = f"@reboot {script_path}\n"
            cron_file = f"/tmp/{task_name}.cron"
            
            with open(cron_file, "w") as f:
                existing_cron = subprocess.run(["crontab", "-l"], stdout=subprocess.PIPE, text=True)
                f.write(existing_cron.stdout.strip() + "\n" + cron_line)
            
            subprocess.run(["crontab", cron_file], check=True)
            os.remove(cron_file)
            print(f"Scheduled task '{task_name}' added to cron.")
        
        else:
            print(f"Task scheduling is not supported on your OS: {sys.platform}")
    
    except subprocess.CalledProcessError as e:
        print(f"Failed to create scheduled task: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def is_choco_installed():
    try:
        result = subprocess.run(["choco", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            print(f"Chocolatey is installed. Version: {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        pass
    return False

def install_choco():
    print("Installing Chocolatey...")

    download_script_cmd = (
        "curl -o install.ps1 https://community.chocolatey.org/install.ps1"
    )

    install_ps_script_cmd = (
        "powershell -NoProfile -ExecutionPolicy Bypass -File install.ps1"
    )

    cleanup_cmd = "del install.ps1"

    try:
        subprocess.run(download_script_cmd, check=True, shell=True)
        
        subprocess.run(install_ps_script_cmd, check=True, shell=True)
        
        subprocess.run(cleanup_cmd, check=True, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Error during installation: {e}")
        sys.exit(1)

def is_node_installed():
    try:
        result = subprocess.run(["node", "-v"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            print(f"Node.js is installed. Version: {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        pass
    print("Node.js is not installed.")
    return False

def install_node_windows():
    print("Installing Node.js on Windows...")

    if not is_choco_installed():
        if ask_yes_no("Install choco?", "Choco is not installed and required. Do you want to install it now?"):
            install_choco()
            print("Waiting for choco to be recognised before restart (15s) (re-run the script after the window closes)")
            time.sleep(15)
            sys.exit(0)
        else:
            print("Choco is needed for setup. Exiting.")
            sys.exit(1)

    try:
        subprocess.run(["choco", "install", "nodejs", "-y"], check=True)
        if is_node_installed():
            print("Node.js installation completed successfully on Windows.")
        else:
            print("Node.js installation failed on Windows.")
    except FileNotFoundError:
        print("Chocolatey is not installed. Please install Chocolatey first from https://chocolatey.org/install.")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"Error during installation: {e}")
        sys.exit(1)

def install_node_unix():
    print("Installing Node.js on Unix-based system...")
    try:
        if os.path.exists("/usr/bin/apt"):
            subprocess.run(["sudo", "apt", "update"], check=True)
            subprocess.run(["sudo", "apt", "install", "-y", "nodejs", "npm"], check=True)
        elif os.path.exists("/usr/bin/yum"):
            subprocess.run(["sudo", "yum", "install", "-y", "nodejs", "npm"], check=True)
        elif os.path.exists("/usr/local/bin/brew"):
            subprocess.run(["brew", "install", "node"], check=True)
        else:
            print("Unsupported package manager. Please install Node.js manually.")
            sys.exit(1)

        if is_node_installed():
            print("Node.js installation completed successfully on Unix-based system.")
        else:
            print("Node.js installation failed on Unix-based system.")
    except subprocess.CalledProcessError as e:
        print(f"Error during installation: {e}")
        sys.exit(1)

def is_visual_studio_installed():
    try:
        result = subprocess.run(["vswhere", "-version", "[15.0,18.0)", "-products", "*", "-requires", "Microsoft.VisualStudio.Component.VC.Tools.x86.x64"], 
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def install_visual_studio():
    print("Installing Visual Studio...")
    try:
        subprocess.run(
            ["choco", "install", "-y", "visualstudio2019buildtools", "visualstudio2019-workload-vctools"],
            check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"Visual Studio installation failed: {e}")
        sys.exit(1)

def main():
    if os.name == "nt":
        if not is_visual_studio_installed():
            if not is_choco_installed():
                if ask_yes_no(
                    "Install Chocolatey?",
                    "Chocolatey is not installed and is required to install Visual Studio. Do you want to install it now?"
                ):
                    install_choco()
                    print("Waiting for Chocolatey installation to complete (15s). Re-run the script.")
                    time.sleep(15)
                    sys.exit(0)
                else:
                    print("Chocolatey is required for Visual Studio installation. Exiting.")
                    sys.exit(1)

            if ask_yes_no(
                "Install Visual Studio?",
                "Visual Studio is not installed or incompatible. It is required for VBScript support. Do you want to install it now?"
            ):
                install_visual_studio()
                print("Waiting for Visual Studio installation to complete (15s). Re-run the script.")
                time.sleep(15)
                sys.exit(0)
            else:
                print("Visual Studio is required for VBScript support. Exiting.")
                sys.exit(1)

    if not check_pip_installed():
        if ask_yes_no("Install pip?", "pip is not installed and required. Do you want to install it now?"):
            install_pip()
            upgrade_pip()
            restart_script()
        else:
            print("pip is needed for setup. Exiting.")
            sys.exit(1)

    if not is_node_installed():
        if ask_yes_no("Install node?", "Node is not installed and required. Do you want to install it now?"):
            system = platform.system()
            if system == "Windows":
                install_node_windows()
            elif system in ("Linux", "Darwin"):
                install_node_unix()
            else:
                print(f"Unsupported OS: {system}. Please install Node.js manually.")
                sys.exit(1)

            print("Waiting for node to be recognised before restart (15s) (re-run the script after the window closes)")
            time.sleep(15)
            sys.exit(0)
        else:
            print("Node is needed for setup. Exiting.")
            sys.exit(1)

    install_needed()

    user_directory = get_logged_in_user_dir()
    nov_path = os.path.join(user_directory, "novodo")
    os.makedirs(nov_path, exist_ok=True)

    from github import Github

    GITHUB_TOKEN = load_github_token()

    if GITHUB_TOKEN:
        g = Github(GITHUB_TOKEN)
    else:
        g = Github()

    repo = g.get_repo("NovodoOfficial/novodo-packages")
    file_path = "requirements.txt"

    requirements_path = os.path.join(nov_path, "requirements.txt")

    try:
        file = repo.get_contents(file_path)
        file_content = file.decoded_content

        with open(requirements_path, 'wb') as f:
            f.write(file_content)

    except Exception as e:
        print(f"Failed to download requirements file. Error: {e}")
        messagebox.showerror("Error", f"Failed to download requirements file. Exiting.\nError: {e}")
        sys.exit(1)

    install_requirements_file(requirements_path)

    requrements = extract_packages_from_requirements(requirements_path)

    check_for_packages(requrements)

    os.remove(requirements_path)

    download_and_extract_repo('https://github.com/NovodoOfficial/novodo-packages', nov_path, GITHUB_TOKEN)

    create_scheduled_task()

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
