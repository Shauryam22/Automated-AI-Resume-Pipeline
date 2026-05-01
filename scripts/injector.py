import os
import sys
import re
from google import genai # NEW SDK IMPORT

# 1. Get the raw comment and the original issue body
raw_prompt = os.environ.get("COMMENT_BODY", "").strip()
issue_body = os.environ.get("ISSUE_BODY", "")

if not raw_prompt or raw_prompt.upper() == "SKIP":
    print("No valid content to inject, or SKIP was requested.")
    sys.exit(0)

# 2. Extract the GitHub URL from the original issue text
url_match = re.search(r"(https://github\.com/\S+)", issue_body)
repo_url = url_match.group(1) if url_match else "https://github.com/Shauryam22/YOUR_REPO"

# 3. Configure the AI Client (NEW SYNTAX)
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# 4. Build the dynamic instructions with the extracted URL
system_instruction = f"""
You are an expert technical recruiter and LaTeX formatter.
The user will provide a rough description of a software project they just open-sourced. 
Your job is to rewrite it into a highly professional, punchy, impact-driven resume bullet point.
Focus on action verbs and technical skills.

You MUST output ONLY valid LaTeX code matching this exact format.
You MUST use this exact URL for the hyperlink: {repo_url}

\\resumeSubItem{{Project Name (Tech Stack) [\\href{{{repo_url}}}{{\\textcolor{{blue}}{{Link}}}}]}}
  {{Your action-driven description here.}}

CRITICAL RULES:
- Do NOT wrap the output in markdown formatting (no ```latex).
- Do NOT output any conversational text or explanations.
- Output ONLY the raw LaTeX string.
"""

# 5. Ask the AI to format your prompt (NEW SYNTAX)
try:
    print("Calling AI to format the resume point...")
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=f"{system_instruction}\n\nUser Input: {raw_prompt}"
    )
    ai_formatted_latex = response.text.strip()
    
    if ai_formatted_latex.startswith("```"):
        ai_formatted_latex = "\n".join(ai_formatted_latex.split("\n")[1:-1])
        
    print("Generated LaTeX:\n", ai_formatted_latex)
except Exception as e:
    print(f"Error calling AI: {e}")
    sys.exit(1)

# 6. Inject into the .tex file
resume_file = "resume.tex"
anchor = "% AUTO-INSERT-PROJECTS-HERE"

try:
    with open(resume_file, "r") as f:
        lines = f.readlines()
except FileNotFoundError:
    print(f"Error: {resume_file} not found.")
    sys.exit(1)

with open(resume_file, "w") as f:
    for line in lines:
        f.write(line)
        if anchor in line:
            f.write(f"\n{ai_formatted_latex}\n")

print(f"Successfully injected project with URL: {repo_url}")