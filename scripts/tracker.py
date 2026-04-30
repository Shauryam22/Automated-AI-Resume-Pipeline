import requests
import json
import os

USERNAME ="ShaMal22" # <-- CHANGE THIS
TOKEN = os.getenv("GITHUB_TOKEN")
REPO = os.getenv("GITHUB_REPOSITORY") 

# Fetch current public repos
url = f"https://api.github.com/users/{USERNAME}/repos?type=public"
response = requests.get(url)

if response.status_code == 200:
    public_repos = {repo['name']: repo['html_url'] for repo in response.json()}
else:
    print("Failed to fetch repos")
    exit(1)

# Load previously tracked repos
try:
    with open("tracked_repos.json", "r") as f:
        tracked_repos = json.load(f)
except FileNotFoundError:
    tracked_repos = {}

# Find the difference
new_repos = set(public_repos.keys()) - set(tracked_repos.keys())

# If new repos exist, open an issue
if new_repos:
    headers = {
        "Authorization": f"token {TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    for repo in new_repos:
        issue_url = f"https://api.github.com/repos/{REPO}/issues"
        payload = {
            "title": f"Action Required: Add {repo} to Resume?",
            "body": f"New public repository detected: {public_repos[repo]}\n\nReply to this issue with the exact LaTeX bullet points to inject this. Reply 'SKIP' to ignore."
        }
        requests.post(issue_url, headers=headers, json=payload)
    
    # Update and save the JSON
    with open("tracked_repos.json", "w") as f:
        json.dump(public_repos, f, indent=4)
    print(f"Opened issues for: {', '.join(new_repos)}")
else:
    print("No new public repositories detected.")