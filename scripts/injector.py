import os
import sys
import re
import requests
from google import genai

print("--- 🌍 SMART SYNC RADAR STARTED ---")

# ─────────────────────────────────────────
# 1. Parse Current Resume
# ─────────────────────────────────────────
resume_file = "resume.tex"

try:
    with open(resume_file, "r") as f:
        resume_text = f.read()
except FileNotFoundError:
    print(f"🚨 ERROR: {resume_file} not found.")
    sys.exit(1)

lines = resume_text.splitlines(True)
start_idx, end_idx = -1, -1

for i, line in enumerate(lines):
    if "% AUTO-INSERT-PROJECTS-HERE" in line:
        start_idx = i
    elif "% RESUME-PROJECT-END" in line:
        end_idx = i

if start_idx == -1 or end_idx == -1:
    print("🚨 ERROR: Could not find LaTeX anchor tags.")
    sys.exit(1)

current_projects = "".join(lines[start_idx + 1 : end_idx])

# Extract all GitHub URLs currently in the resume
current_urls_raw = re.findall(r'href\{(https://github\.com/[^}]+)\}', current_projects)
current_urls = set([url.strip().rstrip('/') for url in current_urls_raw])

# ─────────────────────────────────────────
# 2. Fetch All Public Repos
# ─────────────────────────────────────────
print("🔍 Scanning GitHub for active tags...")

api_url = "https://api.github.com/users/Shauryam22/repos?type=public&per_page=100"
response = requests.get(api_url)

if response.status_code != 200:
    print("🚨 ERROR: Failed to fetch repos.")
    sys.exit(1)

repos = response.json()

MAGIC_ADD    = "<!-- RESUME: ADD -->"
MAGIC_UPDATE = "<!-- RESUME: UPDATE -->"

desired_repos = []

for repo in repos:
    repo_name = repo['name']
    repo_url  = repo['html_url'].rstrip('/')

    raw_urls = [
        f"https://raw.githubusercontent.com/Shauryam22/{repo_name}/main/README.md",
        f"https://raw.githubusercontent.com/Shauryam22/{repo_name}/master/README.md",
        f"https://raw.githubusercontent.com/Shauryam22/{repo_name}/main/readme.md",
    ]

    readme_text = ""
    for url in raw_urls:
        res = requests.get(url)
        if res.status_code == 200:
            readme_text = res.text
            break

    if MAGIC_UPDATE in readme_text:
        desired_repos.append({
            "name":   repo_name,
            "url":    repo_url,
            "readme": readme_text,
            "action": "UPDATE",
        })
    elif MAGIC_ADD in readme_text:
        desired_repos.append({
            "name":   repo_name,
            "url":    repo_url,
            "readme": readme_text,
            "action": "ADD/KEEP",
        })

desired_urls = set([r['url'] for r in desired_repos])

# ─────────────────────────────────────────
# 3. Calculate the Diff
# ─────────────────────────────────────────
urls_to_delete   = current_urls - desired_urls
urls_to_add      = desired_urls - current_urls
repos_needing_ai = [
    r for r in desired_repos
    if r['action'] == "UPDATE" or r['url'] in urls_to_add
]

if not urls_to_delete and not repos_needing_ai:
    print("✅ Resume is perfectly in sync with GitHub! No changes needed.")
    sys.exit(0)

n_updates = len([r for r in repos_needing_ai if r['action'] == 'UPDATE'])
print(f"🔄 Sync required! Adding: {len(urls_to_add)}, Deleting: {len(urls_to_delete)}, Updating: {n_updates}")

# ─────────────────────────────────────────
# 4. Build AI Prompt
# ─────────────────────────────────────────
ai_instructions = f"""
You are a state synchronizer for a LaTeX resume.
Below is the CURRENT LaTeX Projects section. I will also give you a list of actions to perform (Delete, Add, Update).

CURRENT LATEX:
```latex
{current_projects}
```

--- ACTIONS REQUIRED ---
"""

if urls_to_delete:
    ai_instructions += "\n1. DELETIONS:\n"
    ai_instructions += "Remove the entire \\resumeSubItem block for the following URLs:\n"
    for url in urls_to_delete:
        ai_instructions += f"- {url}\n"

if repos_needing_ai:
    ai_instructions += "\n2. GENERATION (ADD/UPDATE):\n"
    ai_instructions += "Write or rewrite the \\resumeSubItem blocks for these projects using their README context:\n"
    for repo in repos_needing_ai:
        ai_instructions += (
            f"\nProject: {repo['name']} | URL: {repo['url']}\n"
            f"README Context: {repo['readme'][:3000]}\n"
        )

ai_instructions += r"""
CRITICAL RULES:
1. Output ONLY the final, modified raw LaTeX string for the Projects section.
2. For projects that are in the CURRENT LATEX and NOT in the Deletion or Generation list, KEEP their LaTeX exactly as it is.
3. Format new/updated projects EXACTLY like this (note the negative vspace spacing):

\resumeSubItem{Project Name (Tech Stack) [\href{URL}{\textcolor{blue}{Link}}]}
{\vspace{-8pt}
\begin{itemize}\itemsep0em \parskip0em
  \item Impact and what was built.
  \item Tech stack and architecture.
  \item Deployment or metrics.
\end{itemize}}\vspace{-1em}

4. Do NOT wrap output in markdown ticks.
5. Do NOT include the % AUTO-INSERT-PROJECTS-HERE anchor or the % RESUME-PROJECT-END marker.
"""

# ─────────────────────────────────────────
# 5. Call AI to Rebuild Section
# ─────────────────────────────────────────
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

try:
    print("🧠 Calling AI to reconcile state...")
    ai_response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=ai_instructions,
    )
    ai_formatted_latex = ai_response.text.strip()

    # Strip accidental markdown fences
    if ai_formatted_latex.startswith("```"):
        ai_formatted_latex = "\n".join(ai_formatted_latex.split("\n")[1:-1])

    # Write back to file
    new_lines = (
        lines[:start_idx + 1]
        + [ai_formatted_latex + "\n"]
        + lines[end_idx:]
    )
    with open(resume_file, "w") as f:
        f.writelines(new_lines)

    print("✅ Successfully synced resume.tex!")

except Exception as e:
    print(f"🚨 ERROR calling AI: {e}")
    sys.exit(1)