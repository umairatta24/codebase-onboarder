import requests
import os
from dotenv import load_dotenv
from tqdm import tqdm

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

def prioritize_files(files):
    """Score and rank files by how useful they are for understanding a codebase."""

    # High value — these files tell you the most about a project
    high_priority = [
        "main.py", "app.py", "index.py", "server.py", "cli.py",
        "main.js", "index.js", "app.js", "server.js",
        "main.ts", "index.ts", "app.ts",
        "main.go", "main.rs", "main.java",
        "setup.py", "pyproject.toml", "package.json", "pom.xml",
        "Makefile", "Dockerfile"
    ]

    # Low value — these rarely explain what a project does
    low_priority_extensions = (
        ".gitignore", ".travis.yml", ".eslintrc", ".prettierrc",
        ".editorconfig", ".babelrc", ".lock", ".txt",
        ".rst", ".cfg", ".ini", ".toml", ".md"
    )

    low_priority_names = (
        "LICENSE", "MANIFEST.in", "HISTORY", "CHANGELOG",
        "CONTRIBUTING", "AUTHORS", "NOTICE", "README"
    )

    def score(item):
        name = item["name"]
        # Skip binary and media files entirely
        if name.endswith((".png", ".jpg", ".gif", ".svg", ".ico", ".pdf")):
            return -1
        # High priority files get top score
        if name in high_priority:
            return 2
        # Low priority files get bottom score
        if name.endswith(low_priority_extensions) or name.startswith("."):
            return 0
        if any(name.upper().startswith(n) for n in low_priority_names):
            return 0
        # Everything else (actual source files) gets middle score
        return 1

    # Sort by score descending, filter out anything with score -1
    ranked = sorted(
        [f for f in files if score(f) >= 0],
        key=score,
        reverse=True
    )

    return ranked

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
    eligible_files = prioritize_files(files)[:5]

    for item in tqdm(eligible_files, desc="Reading source files", unit="file"):
        name = item["name"]
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