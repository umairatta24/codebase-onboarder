import argparse
import sys
from github_client import collect_repo_data
from ai_client import generate_onboarding_guide
from file_writer import save_guide

def parse_github_url(url):
    """Extract the owner and repo name from a GitHub URL.
    
    Example: https://github.com/facebook/react
    Returns: ("facebook", "react")
    """
    # Remove trailing slash if present
    url = url.rstrip("/")
    
    # Split the URL by "/" and get the last two parts
    parts = url.split("/")
    
    if len(parts) < 2:
        print("Error: Invalid GitHub URL.")
        sys.exit(1)
    
    owner = parts[-2]
    repo = parts[-1]
    return owner, repo

def main():
    # Set up the CLI argument parser
    parser = argparse.ArgumentParser(
        description="Generate an onboarding guide for any GitHub repository."
    )
    
    parser.add_argument(
        "url",
        help="The full GitHub repository URL (e.g. https://github.com/owner/repo)"
    )
    
    args = parser.parse_args()
    
    # Step 1: Parse the URL to get owner and repo name
    owner, repo = parse_github_url(args.url)
    print(f"\nGenerating onboarding guide for: {owner}/{repo}\n")
    
    # Step 2: Fetch all the repo data from GitHub
    repo_data = collect_repo_data(owner, repo)
    
    # Step 3: Send the data to Claude and get the guide back
    guide = generate_onboarding_guide(repo_data)
    
    # Step 4: Save the guide to a markdown file
    filename = save_guide(guide, repo)
    
    print(f"\nDone! Open {filename} to read your onboarding guide.")

if __name__ == "__main__":
    main()