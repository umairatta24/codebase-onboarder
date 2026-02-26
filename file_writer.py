def save_guide(guide_text, repo_name):
    """Save the generated onboarding guide to a markdown file."""
    filename = f"{repo_name}-onboarding.md"

    with open(filename, "w") as f:
        f.write(guide_text)

    print(f"Onboarding guide saved to: {filename}")
    return filename