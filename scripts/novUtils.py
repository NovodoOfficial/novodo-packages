# H======================================================================================== Novodo script - utils =====H #

# I====================================================================================================== IMPORTS =====I #

import requests
import platform
import logging
import shutil
import signal
import json
import sys
import os
import atexit

# I====================================================================================================== IMPORTS =====I #

# F==================================================================================================== FUNCTIONS =====F #

def clearScreen():
    system = platform.system()

    if system == "Windows":
        os.system("cls")
    elif system == "Linux" or system == "Darwin":
        os.system("clear")
    else:
        raise EnvironmentError("Unsupported platform")

def get_script_info():
    current_script = sys.argv[0]
    SCRIPT_NAME    = os.path.splitext(os.path.basename(current_script))[0]
    SCRIPT_DIR     = os.path.dirname(os.path.abspath(current_script))
    SCRIPT_PATH    = os.path.abspath(current_script)
    
    return SCRIPT_NAME, SCRIPT_DIR, SCRIPT_PATH

def get_logged_in_user_dir():
    if os.name == "nt":
        user_dir = os.environ.get("USERPROFILE", "")
    else:
        user_dir = os.environ.get("HOME", "")

    return user_dir

def format_size(kb, decimal_places=2):
    units = ["KB", "MB", "GB", "TB", "PB"]
    size = kb
    unit_index = 0

    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1

    return f"{size:.{decimal_places}f} {units[unit_index]}"

def get_input(text=""):
    if text:
        logging.debug(f"INPUT PROMPTED FOR: {text}")
    else:
        logging.debug("INPUT PROMPTED")
    user_input = input(text)
    logging.debug(f"USER INPUT: {user_input}")
    return user_input

class Config:
    def load(config_dir):
        try:
            combined_data = {}

            for filename in os.listdir(config_dir):
                if filename.endswith(".json"):
                    file_path = os.path.join(config_dir, filename)
                    with open(file_path, "r") as file:
                        data = json.load(file)
                    
                    key = os.path.splitext(filename)[0]
                    combined_data[key] = data

            return combined_data
        
        except FileNotFoundError:
            return {}
    
    def save(config, config_dir):
        os.makedirs(config_dir, exist_ok=True)

        for key, value in config.items():
            file_path = os.path.join(config_dir, f"{key}.json")
            with open(file_path, "w") as file:
                json.dump(value, file, indent=4)
        
    def validate(config_path):
        try:
            with open(config_path, "r") as file:
                json_data = json.load(file)
            return True
        except:
            return False
        
    def backup(config_path, config_backup_path):
        os.makedirs(os.path.dirname(config_backup_path), exist_ok=True)

        base, ext = os.path.splitext(config_backup_path)
        backup_path = config_backup_path
        index = 1
        
        while os.path.exists(backup_path):
            backup_path = f"{base}_{index}{ext}"
            index += 1

        shutil.copy(config_path, backup_path)
        
        return backup_path
    
    @staticmethod
    def reset_to_defaults(config):
        if isinstance(config, dict):
            for key, value in config.items():
                if isinstance(value, dict):
                    if "value" in value and "default" in value:
                        value["value"] = value["default"]
                    if "options" in value and isinstance(value["options"], dict):
                        Config.reset_to_defaults(value["options"])
        return config

    def generate_template(config_dir):
        try:
            combined_data = {}

            for filename in os.listdir(config_dir):
                if filename.endswith(".json"):
                    file_path = os.path.join(config_dir, filename)
                    with open(file_path, "r") as file:
                        data = json.load(file)
                    
                    key = os.path.splitext(filename)[0]
                    combined_data[key] = data

            config = combined_data

            config_defaults = Config.reset_to_defaults(config)

            return config_defaults
        
        except FileNotFoundError:
            return {}

    def get_option(option_adress, config):
        option = config
        adress_list = option_adress.split("/")

        for i, adress in enumerate(adress_list):
            if i == len(adress_list) - 1:
                if "value" in option[adress]:
                    return option[adress]["value"]
                raise KeyError(f"'value' not found in the final option: {adress}")
            elif "options" in option[adress]:
                option = option[adress]["options"]
            else:
                raise KeyError(f"'options' not found while navigating: {adress}")

        return option
    
    def set_option(option_address, value, config):
        option = config
        address_list = option_address.split("/")
        
        for i, address in enumerate(address_list):
            if i == len(address_list) - 1:
                option[address]["value"] = value
            else:
                option = option[address]["options"]
        
        return config

class Github:
    def download_and_extract_repo(repo_url, download_dir, branch, github_token=None):
        try:
            import requests
            import zipfile
        except ImportError as e:
            logging.error(f"Error importing libraries: {e}")
            return

        parts = repo_url.rstrip("/").split("/")
        owner, repo_name = parts[-2], parts[-1]
        
        api_url = f"https://github.com/{owner}/{repo_name}/archive/refs/heads/{branch}.zip"

        headers = {}
        if github_token:
            headers["Authorization"] = f"token {github_token}"
        
        if not os.path.exists(download_dir):
            os.makedirs(download_dir)
        
        zip_file_path = os.path.join(download_dir, f"{repo_name}.zip")

        if os.path.exists(zip_file_path):
            logging.info(f"Overwriting {zip_file_path}.")
            os.remove(zip_file_path)

        try:
            logging.info(f"Downloading {repo_name} repository...")
            response = requests.get(api_url, headers=headers)
            response.raise_for_status()
            
            with open(zip_file_path, "wb") as file:
                file.write(response.content)
            logging.info(f"Repository {repo_name} downloaded successfully as ZIP.")
            
            logging.info("Extracting ZIP file...")
            with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
                zip_ref.extractall(download_dir)
            
            extracted_folder = os.path.join(download_dir, f"{repo_name}-main")
            if os.path.exists(extracted_folder):
                for item in os.listdir(extracted_folder):
                    item_path = os.path.join(extracted_folder, item)
                    dest_path = os.path.join(download_dir, item)
                    if os.path.exists(dest_path):
                        logging.info(f"Overwriting {dest_path}.")
                        if os.path.isdir(dest_path):
                            shutil.rmtree(dest_path)
                        else:
                            os.remove(dest_path)
                    shutil.move(item_path, download_dir)
                os.rmdir(extracted_folder)
                logging.info(f"Moved contents from {extracted_folder} to {download_dir}.")
        
        except requests.exceptions.RequestException as e:
            logging.error(f"An error occurred while downloading: {e}")
        except zipfile.BadZipFile as e:
            logging.error(f"Failed to extract ZIP file: {e}")
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
        finally:
            if os.path.exists(zip_file_path):
                os.remove(zip_file_path)
            if os.path.exists(extracted_folder):
                shutil.rmtree(extracted_folder)
        
    def get_repo_size(owner, repo_name, token=None):
        url = f"https://api.github.com/repos/{owner}/{repo_name}"
        headers = {}
        if token:
            headers["Authorization"] = f"token {token}"
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            repo_info = response.json()
            size_kb = repo_info.get("size", 0)
            return size_kb
        else:
            print(f"Error: {response.status_code}")
            return None

    def get_token(config_dir):
        config = Config.load(config_dir)
        adress = "system/github/token"
        token = Config.get_option(adress, config)

        return token

class Files:
    def rm_dir_file(path):
        if os.path.exists(path):
            if os.path.isfile(path):
                os.remove(path)
            elif os.path.isdir(path):
                shutil.rmtree(path)
            else:
                print(f"Path \"{path}\" is neither a file nor a directory.")

class Markdown:
    BOLD = "\033[1m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    RESET = "\033[0m"

    def hex_to_ansi(hex_color):
        if hex_color.startswith("#"):
            hex_color = hex_color[1:]

        if len(hex_color) == 6:
            r = int(hex_color[:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:], 16)
        else:
            raise ValueError("Invalid hex color format. Use \"#RRGGBB\" or \"RRGGBB\".")

        return f"\033[38;2;{r};{g};{b}m"
    
    def hex_to_ansi_bg(hex_color):
        if hex_color.startswith("#"):
            hex_color = hex_color[1:]

        if len(hex_color) == 6:
            r = int(hex_color[:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:], 16)
        else:
            raise ValueError("Invalid hex color format. Use \"#RRGGBB\" or \"RRGGBB\".")

        return f"\033[48;2;{r};{g};{b}m"

    def generate_terminal_md(markdown, terminal_width=25):
        def format_syntax(syntax, code):
            tokens = markdown.split(syntax)
            result = []

            for i in range(len(tokens)):
                if i % 2 == 0:
                    result.append(Markdown.RESET)
                else:
                    result.append(code)

                result.append(tokens[i])
            
            result.append(Markdown.RESET)

            return "".join(result)

        markdown = format_syntax("**", Markdown.BOLD)
        markdown = format_syntax("*", Markdown.ITALIC)
        markdown = format_syntax("__", Markdown.UNDERLINE)

        bar = Markdown.hex_to_ansi("888888") + "─" * terminal_width + Markdown.RESET

        markdown = markdown.replace("---", bar)

        return markdown

# F==================================================================================================== FUNCTIONS =====F #

# V==================================================================================================== CONSTANTS =====V #

# G======================================================================================================== DEBUG =====G #

DEBUG = False

# G======================================================================================================= SCRIPT =====G #

SCRIPT_NAME, SCRIPT_DIR, SCRIPT_PATH = get_script_info()                              # ? Info and locations of the script
UTILS_DIR                            = os.path.dirname(os.path.abspath(__file__))     # ? Directory of this file

# G========================================================================================================= USER =====G #

USER_DIR                             = get_logged_in_user_dir()                       # ? Directory for the current user
NOVODO_DIR                           = os.path.join(USER_DIR, ".novodo")              # ? Directory for Novodo

# G======================================================================================================= CONFIG =====G #

CONFIG_DIR                           = os.path.join(NOVODO_DIR, "config")             # ? Directory for config json tempate
CONFIG_TEMPLATE                      = Config.generate_template(CONFIG_DIR)           # ? Config json tempate

# G===================================================================================================== PACKAGES =====G #

PACKAGES_FOLDER = os.path.join(NOVODO_DIR, "packages")                                # ? Directory for Novodo packages folder

# G===================================================================================================== MESSAGES =====G #

class Messages:
    CANNOT_CONTINUE = "Cannot continue, exiting..."
    REPEATED_OPTION = "Option is not unique, exiting..."

# G================================================================================================ CONFIRM LISTS =====G #

Y_LIST = ["y", "yes"]
CONFIRM_LIST = ["c", "confirm"]

N_LIST = ["n", "no"]
CANCEL_LIST = ["c", "cancel"]

BACKUP_LIST = ["b", "backup"]

# G====================================================================================================== LOGGING =====G #

LOGGING_PATH = os.getcwd()

if os.path.isdir(NOVODO_DIR):
    LOGGING_PATH = os.path.join(NOVODO_DIR, "Novodo Packages Log.log")

LOGGING_LEVEL = logging.INFO
if DEBUG:
    LOGGING_LEVEL = logging.DEBUG

# G===================================================================================================== BRANDING =====G #

class Branding:
    HEX = "71b51b"
    ANSI = Markdown.hex_to_ansi(HEX)

    BANNER = """

██      ██  ██████████  ██      ██
████    ██  ██      ██  ██      ██
██  ██  ██  ██      ██  ██      ██
██    ████  ██      ██    ██  ██
██      ██  ██████████      ██

██████████  ████████    ██████████
██      ██  ██      ██  ██      ██
██      ██  ██      ██  ██      ██
██      ██  ██      ██  ██      ██
██████████  ████████    ██████████

""".strip()

# V==================================================================================================== CONSTANTS =====V #

# O====================================================================================================== LOGGING =====O #

exit_called = False
session_logs = []
exit_logged = False

class InMemoryHandler(logging.Handler):
    def emit(self, record):
        session_logs.append(self.format(record))

logging.basicConfig(
    level=LOGGING_LEVEL,
    format="%(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOGGING_PATH, encoding='utf-8'),
        InMemoryHandler()
    ]
)

file_handler = logging.FileHandler(LOGGING_PATH, encoding='utf-8')
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))

logging.getLogger().handlers[1] = file_handler

def handle_exit(signum=None, frame=None):
    global exit_called, exit_logged
    if not exit_called and not exit_logged:
        logging.debug("Script exited")
        exit_called = True
        exit_logged = True

signal.signal(signal.SIGINT, handle_exit)
signal.signal(signal.SIGTERM, handle_exit)
atexit.register(handle_exit)

# O====================================================================================================== LOGGING =====O #
