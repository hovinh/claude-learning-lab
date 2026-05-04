# claude-learning-lab

A collection of Claude Code best-practice examples. Each folder is a self-contained project with its own environment and a `notes.md` explaining the concepts and Claude Code workflow behind it.

## Examples

| Project | Stack | Demonstrates |
|---|---|---|
| [api-monitor](api-monitor/) | Click · Requests · smtplib · pytest | Python CLI package, YAML config, email alerts, rolling stats |

## How each example is structured

```
<example>/
├── <package>/        source code
├── tests/            pytest suite
├── config.yaml       example configuration
├── pyproject.toml    package + entry point + dev deps
├── notes.md          concepts demonstrated + Claude Code workflow
├── prompt.md         original prompt used to generate the example
└── .venv/            local virtual environment (gitignored)
```

## Running an example

```bash
cd <example>
py -3.11 -m venv .venv
source .venv/Scripts/activate   # Windows Git Bash
# or: .venv\Scripts\Activate.ps1  (PowerShell)
pip install -e ".[dev]"
pytest
```