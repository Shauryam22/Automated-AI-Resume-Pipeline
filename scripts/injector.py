import os
import sys
import requests
from google import genai

print("--- 🌍 GLOBAL RADAR SCRIPT STARTED ---")

# 1. Parse Current Resume (To check what projects are already in there)
resume_file = "resume.tex"
try:
    with open(resume_file, "r") as f:
        resume_text = f.read()
except FileNotFoundError:
    print(f"🚨 ERROR: {resume_file} not found.")
    sys.exit(1)

# Find the injection boundaries
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

# 2. Fetch all public repos for the user
print("🔍 Scanning GitHub for all public repositories...")
api_url = "https://api.github.com/users/Shauryam22/repos?type=public&per_page=100"
response = requests.get(api_url)

if response.status_code != 200:
    print(f"🚨 ERROR: Failed to fetch repos. Status: {response.status_code}")
    sys.exit(1)

repos = response.json()
MAGIC_STRING = "<!-- RESUME: ADD -->"
project_added = False

# 3. Loop through all repos and check READMEs
for repo in repos:
    repo_name = repo['name']
    repo_url = repo['html_url']
    
    # DEDUPLICATION CHECK: Is this repo already in the resume?
    if repo_url in current_projects:
        continue # Skip this repo, it's already on the resume!

    # Fetch README
    raw_urls = [
        f"https://raw.githubusercontent.com/Shauryam22/{repo_name}/main/README.md",
        f"https://raw.githubusercontent.com/Shauryam22/{repo_name}/master/README.md"
    ]
    
    readme_text = ""
    for url in raw_urls:
        res = requests.get(url)
        if res.status_code == 200:
            readme_text = res.text
            break
            
    # Check for the secret tag
    if MAGIC_STRING in readme_text:
        print(f"🎯 Secret tag found in NEW repo: {repo_name}! Preparing AI...")
        
        # 4. Call AI
        client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
        system_instruction = f"""
        You are an expert technical recruiter and LaTeX editor.
        The user has a project. Read the README context and write 2-3 ATS-optimized resume bullet points.
        
        Format EXACTLY like this:
        \\resumeSubItem{{{repo_name} (Tech Stack) [\\href{{{repo_url}}}{{\\textcolor{{blue}}{{Link}}}}]}}
          {{\\vspace{{-8pt}}
          \\begin{{itemize}}\\itemsep0em \\parskip0em
            \\item Impact and what was built.
            \\item Tech stack and architecture.
            \\item MLOps, deployment, or metrics.
          \\end{{itemize}}}}\\vspace{{-0.5em}}
          
        Here are the CURRENT projects:
        {current_projects}
        
        CRITICAL RULES:
        - Output ONLY the raw LaTeX string for the updated section (combining the new project with the existing ones).
        - Do NOT include the % AUTO-INSERT-PROJECTS-HERE anchor or the % RESUME-PROJECT-END marker.
        - Do NOT wrap the output in markdown formatting.
        """
        
        ai_prompt = f"Project README Context:\n{readme_text[:4000]}" 
        
        try:
            ai_response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=f"{system_instruction}\n\n{ai_prompt}"
            )
            ai_formatted_latex = ai_response.text.strip()
            if ai_formatted_latex.startswith("```"):
                ai_formatted_latex = "\n".join(ai_formatted_latex.split("\n")[1:-1])
            
            # Write back to file
            new_lines = lines[:start_idx + 1] + [ai_formatted_latex + "\n"] + lines[end_idx:]
            with open(resume_file, "w") as f:
                f.writelines(new_lines)
                
            print(f"✅ Successfully injected {repo_name} into resume.tex!")
            project_added = True
            
            # Break after adding one project to be safe. 
            # If you have multiple new ones, it will get the next one on the next run.
            break 
            
        except Exception as e:
            print(f"🚨 ERROR calling AI for {repo_name}: {e}")

if not project_added:
    print("✅ Scan complete. No new projects with the secret tag were found.")
    sys.exit(0)