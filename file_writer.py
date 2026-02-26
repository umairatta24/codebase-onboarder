import os

def save_guide(guide_text, repo_name, output_path=None):
    """Save the generated onboarding guide to a markdown file."""

    if output_path:
        # Use the custom path the user provided
        filename = output_path
        # Create any directories in the path if they don't exist
        os.makedirs(os.path.dirname(filename), exist_ok=True) if os.path.dirname(filename) else None
    else:
        # Default: save in current directory
        filename = f"{repo_name}-onboarding.md"

    with open(filename, "w") as f:
        f.write(guide_text)

    print(f"Onboarding guide saved to: {filename}")
    return filename