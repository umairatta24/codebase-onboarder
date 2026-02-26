import requests
import os
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

def get_repo_info(owner, repo):
    """Get basic information about the repository."""
    url = f"https://api.github.com/repos/{owner}/{repo}"
    response = requests.get(url, headers=HEADERS)
    return response.json()

def get_repo_contents(owner, repo, path=""):
    """Get the list of files and folders at a given path in the repo."""
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    response = requests.get(url, headers=HEADERS)
    return response.json()

def get_file_content(owner, repo, file_path):
    """Get the actual content of a single file."""
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}"
    response = requests.get(url, headers=HEADERS)
    data = response.json()

    if "content" in data:
        import base64
        return base64.b64decode(data["content"]).decode("utf-8", errors="ignore")
    return ""

def get_readme(owner, repo):
    """Get the README file content."""
    url = f"https://api.github.com/repos/{owner}/{repo}/readme"
    response = requests.get(url, headers=HEADERS)
    data = response.json()

    if "content" in data:
        import base64
        return base64.b64decode(data["content"]).decode("utf-8", errors="ignore")
    return "No README found."

def collect_repo_data(owner, repo):
    """Collect all the information we need from the repo."""
    print(f"Fetching repo info for {owner}/{repo}...")
    repo_info = get_repo_info(owner, repo)

    print("Fetching README...")
    readme = get_readme(owner, repo)

    print("Fetching file structure...")
    contents = get_repo_contents(owner, repo)

    # If GitHub returns an error (e.g. repo too large), contents will be a dict not a list
    if isinstance(contents, dict):
        print(f"Warning: Could not fetch file structure. GitHub said: {contents.get('message', 'Unknown error')}")
        contents = []

    # Get list of files (not folders) from the top level
    files = [item for item in contents if item.get("type") == "file"]

    # Read up to 5 source files so we don't send too much to Claude
    source_files = {}
    count = 0
    for item in files:
        if count >= 5:
            break
        name = item["name"]
        # Skip files that aren't useful to read
        if name.endswith((".md", ".lock", ".png", ".jpg", ".gif", ".svg")):
            continue
        print(f"Reading file: {name}")
        content = get_file_content(owner, repo, name)
        if content:
            source_files[name] = content
            count += 1

    return {
        "name": repo_info.get("name", repo),
        "description": repo_info.get("description", "No description provided."),
        "language": repo_info.get("language", "Unknown"),
        "stars": repo_info.get("stargazers_count", 0),
        "readme": readme,
        "source_files": source_files
    }