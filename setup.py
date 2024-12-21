# H========================================================================================= Novodo script - main =====H #

# I====================================================================================================== IMPORTS =====I #

import urllib.request
import importlib.util
import tempfile
import sys
import os

# I====================================================================================================== IMPORTS =====I #

# F==================================================================================================== FUNCTIONS =====F #

def fetch_github_file(owner, repo, branch, filepath):
    url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{filepath}"
    try:
        with urllib.request.urlopen(url) as response:
            return response.read().decode('utf-8')
    except urllib.error.HTTPError as e:
        raise Exception(f"Error fetching file: {e.code}")

def get_logged_in_user_dir():
    if os.name == "nt":
        user_dir = os.environ.get("USERPROFILE", "")
    else:
        user_dir = os.environ.get("HOME", "")

    return user_dir

# F==================================================================================================== FUNCTIONS =====F #

# M========================================================================================================= MAIN =====M #

def mainSetup():
    USER_DIR = get_logged_in_user_dir()
    NOVODO_DIR = os.path.join(USER_DIR, ".novodo")

    os.makedirs(NOVODO_DIR, exist_ok=True)

    owner = "NovodoOfficial"
    repo = "novodo-packages"
    branch = "main"
    filepath = "scripts/novUtils.py"

    content = fetch_github_file(owner, repo, branch, filepath)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Temporary directory created at: {temp_dir}")
        
        temp_file_path = os.path.join(temp_dir, "novUtils.py")
        with open(temp_file_path, "w", encoding="utf-8") as temp_file:
            temp_file.write(content)
        print(f"File downloaded and saved as: {temp_file_path}")
        
        spec = importlib.util.spec_from_file_location("novUtils", temp_file_path)
        utils = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(utils)

    if os.path.isfile(NOVODO_DIR):
        print(f"File found at, \"{NOVODO_DIR}\2, remove it? ([Y]es/[N]o)")

        if utils.get_input().lower() in utils.Y_LIST:
            os.remove(NOVODO_DIR)
            print(f"File removed: {NOVODO_DIR}")

        else:
            print("File not removed, exiting...")
            sys.exit(1)

    repo_url = f"https://raw.githubusercontent.com/{owner}/{repo}/"

    utils.Github.download_and_extract_repo(repo_url, NOVODO_DIR, branch)

# M========================================================================================================= MAIN =====M #

# R========================================================================================================== RUN =====R #

if __name__ == "__main__":
    try:
        mainSetup()
        
    except KeyboardInterrupt:
        print("KeyboardInterrupt Exit")
        sys.exit(0)

# R========================================================================================================== RUN =====R #