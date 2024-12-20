import urllib.request

def fetch_github_file(owner, repo, branch, filepath):
    url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{filepath}"
    try:
        with urllib.request.urlopen(url) as response:
            return response.read().decode('utf-8')
    except urllib.error.HTTPError as e:
        raise Exception(f"Error fetching file: {e.code}")

owner = "NovodoOfficial"
repo = "novodo-packages"
branch = "main"
filepath = "scripts/novUtils.py"

content = fetch_github_file(owner, repo, branch, filepath)
print(content)
