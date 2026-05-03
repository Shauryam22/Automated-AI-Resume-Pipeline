
# 🚀 AI-Driven Resume CI/CD Pipeline
<!-- RESUME: ADD -->
[![GitHub Actions Status](https://img.shields.io/badge/CI%2FCD-Active-success?logo=github-actions)](https://github.com/features/actions)
[![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python)](https://www.python.org/)
[![Gemini API](https://img.shields.io/badge/AI-Gemini%202.0-orange?logo=google)](https://deepmind.google/technologies/gemini/)
[![LaTeX](https://img.shields.io/badge/LaTeX-Compiled-008080?logo=latex)](https://www.latex-project.org/)

An automated, serverless pipeline that uses **GitHub Actions** and **Google's Gemini AI** to keep my LaTeX resume perfectly synchronized with my latest coding projects. 

No more manual formatting. When I ship a new project, this pipeline automatically writes ATS-optimized bullet points and rebuilds my master PDF.

**You can change the pipeline according to your needs, like your own personalised prompts in  scipts/injector.py, or using a different LLM API by making changes in the YAML file, or changing the schedule of updates in the CI/CD pipeline.**

---

## 🎥 Pipeline Demo
*

https://github.com/user-attachments/assets/464856e7-3753-4cf8-a383-26f3405d77ed


I have used my private automate_resume repo; you use the Automated_AI_Resume_Pipeline.
*

---

## 🧠 The Architecture

This project solves the "stale resume" problem using an event-driven automation loop:

1. **The Trigger:** I push code to any of my public repositories and add a hidden webhook tag (`<!-- RESUME: ADD -->`) to the `README.md`.
2. **The Scanner:** A scheduled (or manually triggered) GitHub Action fires up a Python script that scans my GitHub profile for these active tags via the GitHub REST API.
3. **The AI Injection:** The script extracts the README context and feeds it to the **Gemini 2.0 Flash API**. The LLM is prompted to act as a state synchronizer, generating 2-3 high-impact, ATS-friendly bullet points formatted strictly in LaTeX.
4. **The Compilation:** The generated LaTeX is injected into a master `resume.tex` file using anchor tags.
5. **The Delivery:** The workflow compiles the `.tex` file into a clean, 1-page PDF using a TeX Live environment and pushes the updated code back to the repository.


**CAUTION**: If a project is not in the GitHub repo with a proper ADD tag, then it will be removed from your resume by the pipeline.
So if you don't want a project in your resume, then remove the Resume ADD tag from its README.
---

## 🛠️ Tech Stack

* **Automation Engine:** GitHub Actions (Ubuntu Runners, Cron Scheduling)
* **Scripting & Data Fetching:** Python 3, `requests`
* **AI & LLM:** Google Gemini 2.0 API (`google-genai`)
* **Document Generation:** LaTeX, `pdflatex`

---

## 🚀 How It Works (The Magic)

I never touch the `resume.tex` file directly when adding projects. Instead, I rely on two invisible HTML comments that the Python script looks for:

**To add a new project:**
I place this inside the project's README:
```html
<!-- RESUME: ADD -->

To update an existing project:
If I rewrite a README and want the AI to generate fresh bullet points, I change the tag to:
HTML

<!-- RESUME: UPDATE -->

The Python injector isolates the injection zone in the LaTeX file using these specific anchor tags:
Code snippet

% AUTO-INSERT-PROJECTS-HERE
% ... AI dynamically writes blocks here ...
% RESUME-PROJECT-END

⚙️ Setup & Installation (Forking this project)

If you want to use this pipeline for your own resume, you can fork this repository and configure your environment.
1. Repository Secrets(Github)

Go to Settings > Secrets and variables > Actions and add the following:

    GEMINI_API_KEY: Your API key from Google AI Studio.

    EMAIL_USERNAME: Write your email ID here

    EMAIL_PASSWORD: Paste your app passwords generated in G-Account

    RECEIVER_MAIL: Write your mail ID here also

    GITHUB_TOKEN(don't create it as secrets): Ensure your workflow has Read/Write permissions to push the compiled resume back to the repo.
    
    To get better clarity of these variables, refer to injector_resume.yaml and check the required variables.

2. Environment Variables

Replace USERNAME with your GitHub username in both tracker.py and injector.py:


3. Customize the LaTeX Template

Modify the resume.tex file with your personal information, education, and hardcoded legacy projects. Leave the % AUTO-INSERT-PROJECTS-HERE tags and % RESUME-PROJECT-END exactly where they are in the Projects section in the resume.tex demo file.
📂 File Structure
Plaintext

├── .github/workflows/
│   └── main.yml           # The CI/CD pipeline instructions
├── scripts/
│   └── injector.py        # The core Python script bridging GitHub API and Gemini
├── resume.tex             # The base LaTeX template
└── README.md              # You are here
