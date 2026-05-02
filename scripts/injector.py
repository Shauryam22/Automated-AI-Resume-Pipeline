import os
import sys
import re
from google import genai

print("--- 🚀 INJECTOR SCRIPT STARTED ---")

# 1. Get the prompt
comment_body = os.environ.get("COMMENT_BODY", "").strip()
issue_body = os.environ.get("ISSUE_BODY", "").strip()

print(f"DEBUG: Found COMMENT_BODY (Length: {len(comment_body)})")
print(f"DEBUG: Found ISSUE_BODY (Length: {len(issue_body)})")

raw_prompt = comment_body if comment_body else issue_body

# If prompt is empty or just says "add it" with no details
if not raw_prompt or raw_prompt.upper() == "SKIP" or raw_prompt.lower() == "add it":
    print("🚨 ERROR: No valid prompt detected! Provide the project details in your comment.")
    sys.exit(1) # Force a red X!

print("✅ Prompt accepted. Parsing resume...")

# Extract Repo URL from Issue Body automatically
repo_url = "[https://github.com/Shauryam22](https://github.com/Shauryam22)"
url_match = re.search(r"https://github\.com/[^\s]+", issue_body)
if url_match:
    repo_url = url_match.group(0)
    print(f"✅ Extracted Repo URL: {repo_url}")

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
    print("🚨 ERROR: Could not find % AUTO-INSERT-PROJECTS-HERE or % RESUME-PROJECT-END in resume.tex")
    sys.exit(1)

current_projects = "".join(lines[start_idx + 1 : end_idx])
print(f"✅ Found project section (Lines {start_idx} to {end_idx}). Calling AI...")

# 3. Call AI
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

system_instruction = f"""
You are an expert technical recruiter and LaTeX editor.
The user wants to update their resume's Projects section. They will give you instructions, which might involve ADDING a new project, REMOVING an old project, or REPLACING one.

When a person gives prompt of the project details you modify it according to below rules, your writing MUST be:
- Impactful, punchy, and point-wise.
- Highly tailored to impress recruiters specifically for Data Science and Machine Learning Engineer internship roles.
- Focused on metrics, algorithms, data pipelines, and measurable outcomes.

Format the new project heading EXACTLY like this:
\\resumeSubItem{{Project Name (Tech Stack) [\\href{{{repo_url}}}{{\\textcolor{{blue}}{{Link}}}}]}}
  {{Your punchy,pointwise, impact-driven description here.}}

Here is their CURRENT LaTeX Projects section:
```latex
{current_projects}
```

Your job is to read their request, modify the LaTeX block accordingly, and return the ENTIRE updated Projects section. 

CRITICAL RULES:
- Output ONLY the raw LaTeX string for the updated section.
- Do NOT include the % AUTO-INSERT-PROJECTS-HERE anchor or the % RESUME-PROJECT-END marker.
- Do NOT wrap the output in markdown formatting (no ```latex).
"""

try:
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=f"{system_instruction}\n\nUser Request: {raw_prompt}"
    )
    ai_formatted_latex = response.text.strip()
    
    # Clean up markdown formatting if the AI accidentally adds it
    if ai_formatted_latex.startswith("```"):
        ai_formatted_latex = "\n".join(ai_formatted_latex.split("\n")[1:-1])
        
    print("✅ AI generated new LaTeX successfully.")
except Exception as e:
    print(f"🚨 ERROR calling AI: {e}")
    sys.exit(1)

# 4. Write back to file
new_lines = lines[:start_idx + 1] + [ai_formatted_latex + "\n"] + lines[end_idx:]

try:
    with open(resume_file, "w") as f:
        f.writelines(new_lines)
    print("✅ Successfully overwrote resume.tex with new projects!")
except Exception as e:
    print(f"🚨 Failed to write file: {e}")
    sys.exit(1)