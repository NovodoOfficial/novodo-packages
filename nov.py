from flask import Flask, render_template, redirect, jsonify, url_for, send_from_directory
import requests
import json
import os
import base64
import sys
from datetime import datetime

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
app = Flask(__name__)

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

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=DEBUG_OVERIDE)
