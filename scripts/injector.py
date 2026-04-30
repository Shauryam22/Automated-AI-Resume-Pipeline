import os
import sys

# Get the comment from the GitHub Action environment
comment_body = os.environ.get("COMMENT_BODY", "").strip()

if not comment_body or comment_body.upper() == "SKIP":
    print("No valid content to inject, or SKIP was requested.")
    sys.exit(0)

resume_file = "resume.tex"
anchor = "% AUTO-INSERT-PROJECTS-HERE"

# Read the current resume
try:
    with open(resume_file, "r") as f:
        lines = f.readlines()
except FileNotFoundError:
    print(f"Error: {resume_file} not found.")
    sys.exit(1)

# Write it back out, injecting the new text right below the anchor
with open(resume_file, "w") as f:
    for line in lines:
        f.write(line)
        if anchor in line:
            # Add a newline for formatting, then the comment, then another newline
            f.write(f"\n{comment_body}\n")

print("Successfully injected new project into resume.tex")