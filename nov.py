import os
import json
import requests
from datetime import datetime
from flask import Flask, render_template, redirect, url_for

app = Flask(__name__)

# GitHub repository details
OWNER = 'NovodoOfficial'
REPO = 'novodo-template'
GITHUB_API_URL = f"https://api.github.com/repos/{OWNER}/{REPO}/forks"

# Path to the file where we store the fork data
FORKS_DATA_FILE = 'forks_data.json'

# Path to the config.json file
CONFIG_FILE = 'config.json'

def load_github_token():
    try:
        with open(CONFIG_FILE, 'r') as f:
            config_data = json.load(f)
            return config_data.get('github', {}).get('token')
    except (IOError, json.JSONDecodeError) as e:
        print(f"Error loading GitHub token from config file: {e}")
        return None

# Fetch the GitHub token from the config.json file
GITHUB_TOKEN = load_github_token()

if not GITHUB_TOKEN:
    print("GitHub token is missing or invalid in the config.json file.")
    exit(1)

def save_forks_to_file(forks_data):
    try:
        with open(FORKS_DATA_FILE, 'w') as f:
            json.dump(forks_data, f, indent=4)
    except IOError as e:
        print(f"Error saving forks data to file: {e}")

def load_forks_from_file():
    if os.path.exists(FORKS_DATA_FILE):
        try:
            with open(FORKS_DATA_FILE, 'r') as f:
                return json.load(f)
        except (IOError, json.JSONDecodeError) as e:
            print(f"Error loading forks data from file: {e}")
    return []  # Return an empty list if the file doesn't exist or is invalid

def get_forks():
    try:
        # Set the authorization header with the GitHub token
        headers = {'Authorization': f'token {GITHUB_TOKEN}'}

        # Fetch the list of forks from GitHub with authentication
        response = requests.get(GITHUB_API_URL, headers=headers)
        response.raise_for_status()  # Will throw an error if the request fails
        forks = response.json()

        forks_data = []
        for fork in forks:
            # Try fetching the details.json file from the root directory of each fork
            details_url = f"https://raw.githubusercontent.com/{fork['full_name']}/main/details.json"
            try:
                details_response = requests.get(details_url)
                details_response.raise_for_status()  # Will throw an error if not found
                details_data = details_response.json()
                
                # Extract the 'name' from 'app_info' in details.json, if available
                app_name = details_data.get('app_info', {}).get('name', fork['name'])  # Fallback to the GitHub fork name
                app_description = details_data.get('app_info', {}).get('description', 'No description available')
                app_version = details_data.get('app_info', {}).get('version', 'Unknown version')
                tags = details_data.get('tags', [])
            except requests.RequestException as e:
                print(f"Error fetching details.json for fork {fork['name']}: {e}")
                # If there's an error fetching details.json, fall back to the GitHub fork name
                app_name = fork['name']
                app_description = 'No description available'
                app_version = 'Unknown version'
                tags = []

            # Add fork info to the list
            forks_data.append({
                'name': app_name,
                'description': app_description,
                'version': app_version,
                'tags': tags,
                'html_url': fork['html_url'],
                'owner': fork['owner']['login'],
                'created_at': fork['created_at'],
                'updated_at': fork['updated_at']
            })

        # Save the fetched data to the file
        save_forks_to_file(forks_data)
        return forks_data
    except requests.RequestException as e:
        print(f"Error fetching forks from GitHub: {e}")
        return []

@app.route('/')
def index():
    forks = load_forks_from_file()  # Load the data from the file
    return render_template('index.html', forks=forks, owner=OWNER, repo=REPO)

@app.route('/refresh')
def refresh_forks():
    forks_data = get_forks()  # Fetch fresh data from GitHub
    save_forks_to_file(forks_data)  # Save the fresh data to the file
    return redirect(url_for('display_forks'))  # Redirect to the main page to display the updated data

# Add a custom filter for date formatting
@app.template_filter('dateformat')
def dateformat(value):
    if value:
        date_obj = datetime.strptime(value, '%Y-%m-%dT%H:%M:%SZ')
        return date_obj.strftime('%Y-%m-%d')
    return value

if __name__ == '__main__':
    app.run(debug=True)
