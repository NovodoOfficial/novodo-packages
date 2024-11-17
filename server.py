import time
import subprocess
import requests
import json
import os
import base64
import sys
import code
from threading import Thread
from io import StringIO
from flask import Flask, render_template, redirect, jsonify, url_for, request
from datetime import datetime

print("SERVER STARTED")

DEBUG_OVERIDE = True

def get_logged_in_user_dir():
    if os.name == 'nt':
        user_dir = os.environ.get('USERPROFILE', '')
    else:
        user_dir = os.environ.get('HOME', '')

    return user_dir

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

cwd = os.getcwd()
script_path = sys.argv[0]
args = ' '.join(sys.argv[1:])

command = f'python -u "{script_path}" {args}'

timestamp = datetime.now().strftime("%m/%d/%Y %H:%M:%S.%f")[:-3]

timestamp = f"{timestamp} {cwd}"

command_history = [(command, timestamp, "SERVER STARTED")]

app = Flask(__name__)

app.jinja_env.globals.update(enumerate=enumerate)

os.makedirs(APPS_FOLDER, exist_ok=True)

def format_date(date_str):
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
        return date_obj.strftime("%d/%m/%Y, %I:%M:%S %p")
    except ValueError:
        return date_str

def load_token():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as file:
            config = json.load(file)
            return config.get('github', {}).get('token')
    else:
        print(f"Configuration file {CONFIG_FILE} not found. Continuing without token.")
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

@app.route('/refresh')
def refresh_forks():
    token = load_token()
    forks = get_forks(OWNER, REPO, token)
    save_forks(forks)
    return redirect('/')

@app.route('/')
def index():
    forks_data = []
    if os.path.exists(FORKS_FILE):
        with open(FORKS_FILE, 'r') as file:
            forks_data = json.load(file)
    return render_template('index.html', forks=forks_data)

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
                return redirect(f"/apps/{user}/{repo}/view")
    return 404

@app.route('/settings')
def settings():
    config = load_config()
    user_agent = request.user_agent.string.lower()

    return render_template('settings.html', config=config, user_agent=user_agent)

def load_config():
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_config(config_data):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config_data, f, indent=4)

@app.route('/api/settings/save', methods=['POST'])
def save():
    config = load_config()
    updated = False
    restart_needed = False

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
                            if 'restart_required' in option.get('attributes', []):
                                restart_needed = True
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
                                    if 'restart_required' in option.get('attributes', []):
                                        restart_needed = True
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
                                if 'restart_required' in option.get('attributes', []):
                                    restart_needed = True
                        else:
                            return jsonify({"error": f"Value for {option_name} must be between {min_limit} and {max_limit}."}), 400
                    except ValueError:
                        return jsonify({"error": f"Invalid value for {option_name}. Expected an integer."}), 400

            elif input_type == 'switch':
                new_value = value is not None
                if option['value'] != new_value:
                    option['value'] = new_value
                    updated = True
                    if 'restart_required' in option.get('attributes', []):
                        restart_needed = True

    if updated:
        save_config(config)
        if restart_needed:
            def restart_async():
                time.sleep(1)
                restart_script()

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
    
def restart_script():
    try:
        print("SERVER RESTARTING")

        python = sys.executable
        script_dir = os.path.dirname(os.path.abspath(__file__))
        app_script = os.path.join(script_dir, 'nov.py')

        subprocess.Popen([python, app_script])

        os._exit(0)
    except Exception as e:
        print(f"Error restarting script: {e}")

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
                sys.exit(0)
            
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

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(401)
def unauthorised(error):
    return render_template('401.html'), 401
