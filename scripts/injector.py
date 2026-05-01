import os
import sys
import re
from google import genai

# 1. Get the raw comment and the original issue body
raw_prompt = os.environ.get("COMMENT_BODY", "").strip()
issue_body = os.environ.get("ISSUE_BODY", "")

if not raw_prompt or raw_prompt.upper() == "SKIP":
    print("No valid content to inject, or SKIP was requested.")
    sys.exit(0)

# Extract the GitHub URL from the original issue text
url_match = re.search(r"(https://github\.com/\S+)", issue_body)
repo_url = url_match.group(1) if url_match else "https://github.com/Shauryam22/YOUR_REPO"

# 2. Read the current resume to find the existing projects
resume_file = "resume.tex"
try:
    with open(resume_file, "r") as f:
        lines = f.readlines()
except FileNotFoundError:
    print(f"Error: {resume_file} not found.")
    sys.exit(1)

# 3. Find the exact bounds of the Projects section
anchor = "% AUTO-INSERT-PROJECTS-HERE"
start_idx = -1
end_idx = -1

for i, line in enumerate(lines):
    if anchor in line:
        start_idx = i
        break

if start_idx != -1:
    # Find the very next \resumeSubHeadingListEnd
    for i in range(start_idx + 1, len(lines)):
        if "% RESUME-PROJECT-END" in lines[i]:
            end_idx = i
            break

if start_idx == -1 or end_idx == -1:
    print("Error: Could not find the anchor or the section end marker in resume.tex.")
    sys.exit(1)

# Extract the current LaTeX sitting in the projects section
current_projects = "".join(lines[start_idx + 1 : end_idx])

# 4. Configure the AI
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# 5. Build the context-aware prompt
system_instruction = f"""
You are an expert technical recruiter and LaTeX editor.
The user wants to update their resume's Projects section. They will give you instructions, which might involve ADDING a new project, REMOVING an old project, or REPLACING one.

Here is their CURRENT LaTeX Projects section:
```latex
{current_projects}"""