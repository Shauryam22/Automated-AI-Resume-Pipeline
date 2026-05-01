import os
import sys
import google.generativeai as genai

# 1. Get the raw comment from the issue
raw_prompt = os.environ.get("COMMENT_BODY", "").strip()

if not raw_prompt or raw_prompt.upper() == "skip":
    print("No valid content to inject, or SKIP was requested.")
    sys.exit(0)

# 2. Configure the AI
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

# 3. Build the strict instructions for the AI
system_instruction = """
You are an expert technical recruiter and LaTeX formatter.
The user will provide a rough description of a software project they just open-sourced. 
Your job is to rewrite it into a highly professional, punchy, impact-driven resume bullet point.
Focus on action verbs and technical skills.

You MUST output ONLY valid LaTeX code matching this exact format:
\resumeSubItem{Project Name (Tech Stack) [\href{https://github.com/Shauryam22/YOUR_REPO_NAME}{\textcolor{blue}{Link}}]}
  {Your action-driven description here.}

CRITICAL RULES:
- Do NOT wrap the output in markdown formatting (no ```latex).
- Do NOT output any conversational text or explanations.
- Output ONLY the raw LaTeX string.
"""

# 4. Ask the AI to format your prompt
try:
    print("Calling AI to format the resume point...")
    response = model.generate_content(f"{system_instruction}\n\nUser Input: {raw_prompt}")
    ai_formatted_latex = response.text.strip()
    
    # Strip markdown block just in case the AI disobeys
    if ai_formatted_latex.startswith("```"):
        ai_formatted_latex = "\n".join(ai_formatted_latex.split("\n")[1:-1])
        
    print("Generated LaTeX:\n", ai_formatted_latex)
except Exception as e:
    print(f"Error calling AI: {e}")
    sys.exit(1)

# 5. Inject into the .tex file
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

print("Successfully injected AI-formatted project into resume.tex")