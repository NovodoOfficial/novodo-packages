from flask import Flask, render_template, redirect, jsonify, url_for, request, make_response
from datetime import datetime
from threading import Thread
from io import StringIO
import subprocess
import requests
import argparse
import shutil
import base64
import time
import uuid
import json
import code
import sys
import os

print("SERVER STARTED")

DEBUG_OVERIDE = True

def format_date(date_str):
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
        return date_obj.strftime("%d/%m/%Y, %I:%M:%S %p")
    except ValueError:
        return date_str

def load_token():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
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

def get_release_info(user, repo, token=None):
    url = f"https://api.github.com/repos/{user}/{repo}"
    headers = {'Authorization': f'token {token}'} if token else {}

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        repo_data = response.json()
        release_date = repo_data.get('created_at', 'Not available')
        
        default_branch = repo_data.get('default_branch', 'main')
        commit_url = f"https://api.github.com/repos/{user}/{repo}/commits/{default_branch}"
        commit_response = requests.get(commit_url, headers=headers)
        
        if commit_response.status_code == 200:
            commit_data = commit_response.json()
            updated_date = commit_data.get('commit', {}).get('committer', {}).get('date', 'Not available')
            return {
                "released": release_date,
                "updated": updated_date
            }
        else:
            print(f"Failed to fetch last commit info for {user}/{repo}: {commit_response.status_code} - {commit_response.text}")
            return None

    else:
        print(f"Failed to fetch repo info for {user}/{repo}: {response.status_code} - {response.text}")
    return None

def get_forks(owner, repo, token=None):
    forks = []
    url = f"https://api.github.com/repos/{owner}/{repo}/forks"
    headers = {'Authorization': f'token {token}'} if token else {}

    page = 1
    while True:
        response = requests.get(url, headers=headers, params={'page': page, 'per_page': 100})
        if response.status_code == 200:
            data = response.json()
            if not data:
                break
            for fork in data:
                app_json_content = get_app_json(fork['owner']['login'], fork['name'], token)
                release_info = get_release_info(fork['owner']['login'], fork['name'], token)
                
                if app_json_content and release_info:
                    formatted_released = format_date(release_info["released"])
                    formatted_updated = format_date(release_info["updated"])

                    app_json_content["details"]["snapshotting"]["released"] = formatted_released
                    app_json_content["details"]["snapshotting"]["updated"] = formatted_updated

                    forks.append({
                        "user": fork['owner']['login'],
                        "repo": fork['name'],
                        "app.json": app_json_content
                    })
            page += 1
        else:
            print(f"Failed to fetch forks: {response.status_code} - {response.text}")
            break

    return forks

def get_app_json(user, repo, token=None):
    url = f"https://api.github.com/repos/{user}/{repo}/contents/app.json"
    headers = {'Authorization': f'token {token}'} if token else {}

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if 'content' in data and data['encoding'] == 'base64':
            try:
                content = json.loads(base64.b64decode(data['content']).decode('utf-8'))
                return content
            except (json.JSONDecodeError, ValueError) as e:
                print(f"Invalid JSON in app.json for {user}/{repo}: {e}")
                return None
    elif response.status_code == 404:
        print(f"No app.json found in {user}/{repo}.")
    else:
        print(f"Failed to fetch app.json for {user}/{repo}: {response.status_code} - {response.text}")
    return None

def save_forks(forks):
    with open(FORKS_FILE, 'w') as file:
        json.dump(forks, file, indent=4)
    print(f"Saved {len(forks)} forks to {FORKS_FILE}")

def get_logged_in_user_dir():
    if os.name == 'nt':
        user_dir = os.environ.get('USERPROFILE', '')
    else:
        user_dir = os.environ.get('HOME', '')

    return user_dir

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

def install_requirements_file(path):
    subprocess.run(['pip', 'install', '-r', path], check=True)

def download(user, repo, fork_data):
    os.makedirs(APPS_FOLDER, exist_ok=True)
    token = load_token()

    url = f"https://github.com/{user}/{repo}"

    app_path = os.path.join(APPS_FOLDER, user, repo)

    os.makedirs(app_path, exist_ok=True)

    download_and_extract_repo(url, app_path, token)

    requirements_path = os.path.join(app_path, "requirements.txt")

    install_requirements_file(requirements_path)

def load_config():
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_config(config_data):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config_data, f, indent=4)

def restart_script(restart_args=[]):
    try:
        print("SERVER RESTARTING")

        python = sys.executable
        script_dir = os.path.dirname(os.path.abspath(__file__))
        app_script = os.path.join(script_dir, 'nov.py')

        subprocess.Popen([python, app_script] + restart_args)

        os._exit(0)
    except Exception as e:
        print(f"Error restarting script: {e}")

user_directory = get_logged_in_user_dir()
nov_path = os.path.join(user_directory, "novodo")

script_path = os.path.abspath(__file__)

target_script_path = os.path.join(nov_path, "nov.py")

conditions = os.path.isdir(nov_path) and script_path == target_script_path

if not conditions and not DEBUG_OVERIDE:
    print("Missing files, install novodo with \"setup.py\" before running")
    sys.exit(1)

APPS_FOLDER = os.path.join(nov_path, "apps")

OWNER = 'NovodoOfficial'
REPO = 'novodo-template'
FORKS_FILE = 'forks.json'
CONFIG_FILE = 'config.json'

config = load_config()

password = config["sections"][2]["options"][0]["value"]

PASSWORD = password
UUID_COOKIE_NAME = "session_uuid"
SECURE = False

global_session_uuid = None

cwd = os.getcwd()
script_path = sys.argv[0]
args = ' '.join(sys.argv[1:])

command = f'python -u "{script_path}" {args}'

timestamp = datetime.now().strftime("%m/%d/%Y %H:%M:%S.%f")[:-3]

timestamp = f"{timestamp} {cwd}"

command_history = [(command, timestamp, "SERVER STARTED")]

app = Flask(__name__)

app.jinja_env.globals.update(enumerate=enumerate)

parser = argparse.ArgumentParser(description="Start the Flask app with optional UUID regeneration.")
parser.add_argument('--new_uuid', action='store_true', help="Regenerate the global session UUID.")
args = parser.parse_args()

global_session_uuid_file = "session_uuid.txt"
if args.new_uuid or not os.path.exists(global_session_uuid_file):
    global_session_uuid = str(uuid.uuid4())
    with open(global_session_uuid_file, 'w') as f:
        f.write(global_session_uuid)
else:
    with open(global_session_uuid_file, 'r') as f:
        global_session_uuid = f.read().strip()

print(f"Global session UUID: {global_session_uuid}")

def is_authenticated():
    session_uuid = request.cookies.get(UUID_COOKIE_NAME)
    return session_uuid == global_session_uuid

@app.route('/login', methods=['GET', 'POST'])
def login():
    if not PASSWORD:
        response = make_response(redirect(url_for('index')))
        response.set_cookie(UUID_COOKIE_NAME, global_session_uuid, httponly=True, secure=SECURE)
        return response

    if request.method == 'POST':
        password = request.form.get('password', '')
        if password == PASSWORD:
            response = make_response(redirect(url_for('index')))
            response.set_cookie(UUID_COOKIE_NAME, global_session_uuid, httponly=True, secure=SECURE)
            return response
        else:
            return render_template("login.html", error="Invalid password")
    return render_template("login.html")

@app.route('/')
def index():
    forks_data = []
    if os.path.exists(FORKS_FILE):
        with open(FORKS_FILE, 'r') as file:
            forks_data = json.load(file)
    return render_template('index.html', forks=forks_data)

@app.route('/refresh')
def refresh_forks():
    token = load_token()
    forks = get_forks(OWNER, REPO, token)
    save_forks(forks)
    return redirect('/')

@app.route('/apps/<user>/<repo>/view')
def view_app(user, repo):
    if os.path.exists(FORKS_FILE):
        with open(FORKS_FILE, 'r') as file:
            forks_data = json.load(file)
            fork_data = next((fork for fork in forks_data if fork['user'] == user and fork['repo'] == repo), None)
            if fork_data:
                return render_template('fork.html', fork=fork_data)
    return 404

@app.route('/api/apps/<user>/<repo>/download')
def download_app(user, repo):
    if os.path.exists(FORKS_FILE):
        with open(FORKS_FILE, 'r') as file:
            forks_data = json.load(file)
            fork_data = next((fork for fork in forks_data if fork['user'] == user and fork['repo'] == repo), None)
            if fork_data:
                download(user, repo, fork_data)
                return redirect(f"/apps/{user}/{repo}/view")
    return 404

@app.route('/settings')
def settings():
    config = load_config()
    user_agent = request.user_agent.string.lower()

    return render_template('settings.html', config=config, user_agent=user_agent)

@app.route('/api/settings/save', methods=['POST'])
def save():
    config = load_config()
    updated = False

    triggered_attributes = set()

    for section in config['sections']:
        for option in section['options']:
            option_name = option['name']
            input_type = option['input']

            limits = option.get('limits', {})
            min_limit = limits.get('min', 0)
            max_limit = limits.get('max', 0)

            value = request.form.get(option_name)

            if input_type == 'box':
                if option['type'] == 'str':
                    if len(value) >= min_limit and (max_limit == 0 or len(value) <= max_limit):
                        if option['value'] != value:
                            option['value'] = value
                            updated = True
                            triggered_attributes.update(option.get('attributes', []))
                    else:
                        return jsonify({"error": f"Value for {option_name} must be between {min_limit} and {max_limit} characters."}), 400

                elif option['type'] == 'int':
                    if value:
                        try:
                            value = int(value)
                            if value >= min_limit and (max_limit == 0 or value <= max_limit):
                                if option['value'] != value:
                                    option['value'] = value
                                    updated = True
                                    triggered_attributes.update(option.get('attributes', []))
                            else:
                                return jsonify({"error": f"Value for {option_name} must be between {min_limit} and {max_limit}."}), 400
                        except ValueError:
                            return jsonify({"error": f"Invalid value for {option_name}. Expected an integer."}), 400

            elif input_type == 'slider':
                if value:
                    try:
                        value = int(value)
                        if value >= min_limit and (max_limit == 0 or value <= max_limit):
                            if option['value'] != value:
                                option['value'] = value
                                updated = True
                                triggered_attributes.update(option.get('attributes', []))
                        else:
                            return jsonify({"error": f"Value for {option_name} must be between {min_limit} and {max_limit}."}), 400
                    except ValueError:
                        return jsonify({"error": f"Invalid value for {option_name}. Expected an integer."}), 400

            elif input_type == 'switch':
                new_value = value is not None
                if option['value'] != new_value:
                    option['value'] = new_value
                    updated = True
                    triggered_attributes.update(option.get('attributes', []))

    restart_needed = 'restart_required' in triggered_attributes

    auth_update = 'auth_update' in triggered_attributes

    if updated:
        save_config(config)

        restart_args = []

        if auth_update:
            restart_args.append("--new_uuid")
            restart_needed = True

        if restart_needed:
            def restart_async():
                time.sleep(1)
                restart_script(restart_args)

            Thread(target=restart_async).start()

            config = load_config()

            port = config["sections"][1]["options"][1]["value"]

            return redirect(f"http://localhost:{port}/")
        
        return redirect(url_for('settings'))
    else:
        return jsonify({"error": "No valid changes were made."}), 400
    
@app.route('/api/settings/reset/all')
def reset_all():
    config = load_config()
    updated = False

    for section in config['sections']:
        for option in section['options']:
            if 'default' in option:
                option['value'] = option['default']
                updated = True

    if updated:
        save_config(config)
        return redirect(url_for('settings'))
    else:
        return redirect(url_for('settings'))

@app.route('/api/settings/reset/<section>/<int:option_idx>')
def reset_option(section, option_idx):
    config = load_config()
    updated = False
    restart_needed = False

    for sec in config['sections']:
        if sec['name'] == section:
            if 0 <= option_idx < len(sec['options']):
                option = sec['options'][option_idx]
                if 'default' in option:
                    option['value'] = option['default']
                    updated = True
                    if "restart_required" in option.get('attributes', []):
                        restart_needed = True
                break

    if updated:
        save_config(config)
        if restart_needed:
            from threading import Thread
            Thread(target=restart_script).start()
        return redirect(url_for('settings'))
    else:
        return redirect(url_for('settings'))

@app.route('/debug', methods=['GET', 'POST'])
def debug_console():
    config = load_config()

    if not config["sections"][3]["options"][0]["value"] == True:
        if request.method == 'POST':
            return jsonify({"error": "Unauthorized"}), 401
        return render_template('401.html'), 401

    output = ''
    timestamp = datetime.now().strftime("%m/%d/%Y %H:%M:%S.%f")[:-3]
    
    if request.method == 'POST':
        user_input = request.form.get('command')

        if user_input:
            if user_input in ["stop", "exit", "end"]:
                def restart_async():
                    time.sleep(1)
                    os._exit(0)

                Thread(target=restart_async).start()

                return "Script stopped", 200
            
            if user_input == "restart":
                def restart_async():
                    time.sleep(1)
                    restart_script()

                Thread(target=restart_async).start()

                config = load_config()

                port = config["sections"][1]["options"][1]["value"]

                return redirect(f"http://localhost:{port}/")

            if user_input in ["clear", "cls"]:
                global command_history

                command_history = [(user_input, timestamp, "Cleared")]
                return render_template("debug.html", output=output, history=command_history)

            try:
                command_history.append((user_input, timestamp, ''))

                old_stdout = sys.stdout
                sys.stdout = StringIO()

                console = code.InteractiveConsole(locals=globals())
                console.push(user_input)

                output = sys.stdout.getvalue()
                sys.stdout = old_stdout

                command_history[-1] = (user_input, timestamp, output)

            except Exception as e:
                output = f"Error: {str(e)}"

    return render_template("debug.html", output=output, history=command_history)

@app.route('/api/server/stop')
def shutdown():
    def restart_async():
        time.sleep(1)
        os._exit(0)

    Thread(target=restart_async).start()

    return "Script stopped", 200

@app.route('/api/server/restart')
def restart():
    def restart_async():
        time.sleep(1)
        restart_script()

    Thread(target=restart_async).start()

    config = load_config()

    port = config["sections"][1]["options"][1]["value"]

    return redirect(f"http://localhost:{port}/")

@app.route('/api/server/lockdown')
def lockdown():
    def restart_async():
        time.sleep(1)
        restart_script(["--new_uuid"])

    Thread(target=restart_async).start()

    config = load_config()

    port = config["sections"][1]["options"][1]["value"]

    return redirect(f"http://localhost:{port}/login")

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(401)
def unauthorised(error):
    return render_template('401.html'), 401

@app.before_request
def require_login():
    if request.endpoint not in ('login', 'static') and not is_authenticated():
        return redirect(url_for('login'))