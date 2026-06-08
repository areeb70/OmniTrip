# Activate the virtual machine
run ".venv\Scripts\activate" command in the terminal

# Run The Arize Phoenix Platform

run "python -m phoenix.server.main serve" command in another terminal

OR

run "phoenix serve" command

Then open:

```text
http://localhost:6006/v1/traces
```

# Run The App Very Simply

Double-click:

```text
run_app.bat
```
OR

run "uvicorn src.app:app --reload" command in the terminal

Then open:

```text
http://127.0.0.1:8000
```

<!-- If you prefer PowerShell, run:

```powershell
cd C:\Users\muaaz\Documents\Codex\2026-06-02\about-arize-arize-is-the-single\work\arize-gemini-agent-starter
.\run_app.bat
``` -->
<!-- pip install -r requirements.txt -->

Keep the black window open while using the app.

