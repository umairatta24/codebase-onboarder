# codebase-onboarder

Getting dropped into an unfamiliar codebase is one of the most time-consuming parts of software development. Reading through files, piecing together what does what, figuring out how to even run the thing — it can take hours.

This tool does it in seconds and seamlessly.

Point it at any public GitHub repository and it generates a structured onboarding guide: what the project does, how the code is organized, how to get it running, and what to watch out for. Powered by the Claude API.

## Usage
```bash
python3 main.py https://github.com/owner/repo
```

That's it. A markdown file gets saved to your current directory.

Save to a custom location with `--output`:
```bash
python3 main.py https://github.com/owner/repo --output ./docs/guide.md
```

## Example
```bash
$ python3 main.py https://github.com/kennethreitz/records

Generating onboarding guide for: kennethreitz/records
Fetching repo info...
Fetching README...
Fetching file structure...
Reading source files: 100%|██████████| 5/5 [00:00<00:00, 7.76file/s]
Sending to Claude...
Onboarding guide saved to: records-onboarding.md

Done! Open records-onboarding.md to read your onboarding guide.
```

The output covers what the project does, the tech stack, key files, setup instructions, core concepts, and common gotchas — written in plain language.

## Setup

**Requirements:** Python 3.8+, an Anthropic API key, a GitHub personal access token
```bash
git clone https://github.com/umairatta24/codebase-onboarder.git
cd codebase-onboarder
python3 -m venv venv
source venv/bin/activate
pip install anthropic requests python-dotenv tqdm
```

Create a `.env` file in the root directory:
```
ANTHROPIC_API_KEY=your-anthropic-key-here
GITHUB_TOKEN=your-github-token-here
```

- Anthropic API key: [console.anthropic.com](https://console.anthropic.com)
- GitHub token: Settings → Developer Settings → Personal Access Tokens → Tokens (classic) → check `repo`

Then run it against any public repo:
```bash
python3 main.py https://github.com/owner/repo
```

## How it works

1. Parses the repo URL and calls the GitHub REST API to pull the README, file structure, and up to 5 source files
2. Scores and ranks files by relevance — prioritizing entry points and core logic over config files and dotfiles
3. Feeds that context into a structured prompt and sends it to Claude
4. Writes the response to a markdown file

Source files are capped at 5 (300 lines each) to keep API usage minimal — a full run costs fractions of a cent.

## Project structure
```
main.py            # CLI entry point, argument parsing, and orchestration
github_client.py   # GitHub API calls, data collection, and smart file prioritization
ai_client.py       # Claude API integration and prompt engineering
file_writer.py     # Markdown file output with custom path support
```

## Known limitations

- Only scans the root directory of a repo — deeply nested projects get partial coverage
- Public repositories only

## Possible extensions

- Recursive file scanning for nested project structures
- Support for private repos via fine-grained tokens
- HTML or PDF export
- Web interface
