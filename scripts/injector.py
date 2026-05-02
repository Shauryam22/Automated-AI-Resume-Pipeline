import os
import sys
import re
import requests
from google import genai

print("--- 🚀 ZERO-TOUCH INJECTOR SCRIPT STARTED ---")

# 1. Get the issue body
issue_body = os.environ.get("ISSUE_BODY", "").strip()

# 2. Extract Repo URL and Name
repo_url = "https://github.com/Shauryam22"
repo_name = ""
url_match = re.search(r"https://github\.com/[^\s]+", issue_body)

if url_match:
    repo_url = url_match.group(0)
    print(f"✅ Extracted Repo URL: {repo_url}")
    
    # Extract just the repository name
    name_match = re.search(r"github\.com/[^/]+/([^/\s]+)", repo_url)
    if name_match:
        repo_name = name_match.group(1)
else:
    print("🚨 ERROR: Could not find a repository URL in the issue.")
    sys.exit(1)

# 3. Automatically Fetch the README
readme_text = ""
if repo_name:
    print(f"🔍 Searching for README.md in repository: {repo_name}...")
    raw_urls = [
        f"https://raw.githubusercontent.com/Shauryam22/{repo_name}/main/README.md",
        f"https://raw.githubusercontent.com/Shauryam22/{repo_name}/master/README.md",
        f"https://raw.githubusercontent.com/Shauryam22/{repo_name}/main/readme.md"
    ]
    
    for url in raw_urls:
        response = requests.get(url)
        if response.status_code == 200:
            readme_text = response.text
            print("✅ Successfully downloaded README.md!")
            break

# 4. THE SECRET CODE CHECK (Zero-Touch Logic)
MAGIC_STRING = "<!-- RESUME: ADD -->"

if not readme_text:
    print("⚠️ No README found in the repository. Skipping resume injection.")
    sys.exit(0) # Exit cleanly with a green checkmark

if MAGIC_STRING not in readme_text:
    print(f"🛑 Secret tag '{MAGIC_STRING}' NOT found in README. Skipping injection.")
    sys.exit(0) # Exit cleanly with a green checkmark

print(f"🎯 Secret tag found! Preparing AI prompt...")

# 5. Parse Resume
resume_file = "resume.tex"
try:
    with open(resume_file, "r") as f:
        lines = f.readlines()
except FileNotFoundError:
    print(f"🚨 ERROR: {resume_file} not found.")
    sys.exit(1)

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
print(f"✅ Found project section. Calling AI...")

# 6. Build Smart Prompt for AI
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

system_instruction = f"""
You are an expert technical recruiter and LaTeX editor.
The user has created a new project. Below is the raw text of their project's README.md file.
Your job is to read the README, understand the tech stack, the architecture, and the business/technical impact, and turn it into 2-3 highly professional, ATS-optimized resume bullet points.

Format the new project heading EXACTLY like this:
\\resumeSubItem{{Project Name (Tech Stack) [\\href{{{repo_url}}}{{\\textcolor{{blue}}{{Link}}}}]}}
  {{\\vspace{{-8pt}}
  \\begin{{itemize}}\\itemsep0em \\parskip0em
    \\item First bullet point highlighting what was built and its impact.
    \\item Second bullet point detailing the tech stack, algorithms, or pipelines.
    \\item Third bullet point focusing on deployment, metrics, or MLOps (if applicable).
  \\end{{itemize}}}}\\vspace{{-0.5em}}

Here is their CURRENT LaTeX Projects section:
{current_projects}

CRITICAL RULES:
- Output ONLY the raw LaTeX string for the updated section (combining the new project with the existing ones).
- Do NOT include the % AUTO-INSERT-PROJECTS-HERE anchor or the % RESUME-PROJECT-END marker.
- Do NOT wrap the output in markdown formatting.
"""

# Limit to first 4000 characters to prevent crashing the AI
ai_prompt = f"Project README Context:\n{readme_text[:4000]}" 

try:
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=f"{system_instruction}\n\n{ai_prompt}"
    )
    ai_formatted_latex = response.text.strip()
    
    if ai_formatted_latex.startswith("```"):
        ai_formatted_latex = "\n".join(ai_formatted_latex.split("\n")[1:-1])
        
    print("✅ AI generated new LaTeX successfully.")
except Exception as e:
    print(f"🚨 ERROR calling AI: {e}")
    sys.exit(1)

# 7. Write back to file
new_lines = lines[:start_idx + 1] + [ai_formatted_latex + "\n"] + lines[end_idx:]

try:
    with open(resume_file, "w") as f:
        f.writelines(new_lines)
    print("✅ Successfully overwrote resume.tex with new projects!")
except Exception as e:
    print(f"🚨 Failed to write file: {e}")
    sys.exit(1)