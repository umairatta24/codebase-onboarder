import anthropic
import os
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def generate_onboarding_guide(repo_data):
    """Send repo data to Claude and get back an onboarding guide."""

    # Build a summary of the source files to include in the prompt
    files_text = ""
    for filename, content in repo_data["source_files"].items():
        # Limit each file to 300 lines so we don't send too much
        lines = content.split("\n")[:300]
        truncated = "\n".join(lines)
        files_text += f"\n\n--- {filename} ---\n{truncated}"

    prompt = f"""You are a senior software engineer writing an onboarding guide for a new engineer joining a project.

Here is the information about the repository:

Repository Name: {repo_data['name']}
Description: {repo_data['description']}
Primary Language: {repo_data['language']}
GitHub Stars: {repo_data['stars']}

README:
{repo_data['readme'][:3000]}

Source Files:
{files_text}

Please write a clear, friendly, and thorough onboarding guide in Markdown format. Include these sections:

1. **What This Project Does** - explain the purpose in plain English
2. **Tech Stack** - list the languages, frameworks, and tools used
3. **Project Structure** - explain what the key files and folders do
4. **How To Get Started** - setup and run instructions based on what you see
5. **Key Concepts** - explain the most important patterns or concepts a new engineer needs to understand
6. **Things To Watch Out For** - any gotchas, quirks, or important notes

Write it as if you're a friendly senior engineer helping a new teammate on their first day.
"""

    print("Sending to Claude, generating onboarding guide...")

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=2048,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return message.content[0].text