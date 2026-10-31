# Contributing to EduGrade AI

🎉 Thank you for your interest in contributing! EduGrade AI is open source and **Hacktoberfest-friendly**. We welcome contributions from developers, designers, educators, and testers — especially first-time open-source contributors.

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How to Contribute](#how-to-contribute)
- [Good First Issues](#good-first-issues)
- [Development Setup](#development-setup)
- [Pull Request Process](#pull-request-process)
- [Commit Conventions](#commit-conventions)
- [Reporting Issues](#reporting-issues)
- [License](#license)

---

## Code of Conduct

By participating, you agree to uphold our [Code of Conduct](CODE_OF_CONDUCT.md). Please be respectful and inclusive to everyone.

---

## How to Contribute

1. **Fork** the repository on GitHub.
2. **Clone** your fork locally:
   ```bash
   git clone https://github.com/<your-username>/edugrade-ai.git
   cd edugrade-ai
   ```
3. **Create a branch** for your change:
   ```bash
   git checkout -b feature/your-feature-name
   ```
4. **Make your changes** and test them.
5. **Commit** using our commit conventions (see below).
6. **Push** to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```
7. **Open a Pull Request** against the `main` branch.

---

## Good First Issues

Great issues for new contributors:

- Add screenshots to `README.md` under `docs/screenshots/`
- Improve docstrings or inline comments in `gemma_helper.py` or `app.py`
- Add input validation (e.g., empty rubric, missing image)
- Add a `CODE_OF_CONDUCT.md`
- Add a `.env.example` template
- Improve error messages in the UI
- Add unit tests for `gemma_helper.py` parsing logic

Label these with `good first issue` or `hacktoberfest`.

---

## Development Setup

```bash
# Clone the repo
git clone https://github.com/<your-username>/edugrade-ai.git
cd edugrade-ai

# Create a virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Add your GEMMA_API_KEY to .env (never commit it)

# Run the app
streamlit run app.py
```

Run linting/format checks before submitting:

```bash
python -m py_compile app.py gemma_helper.py
```

---

## Pull Request Process

1. Ensure your branch is up to date with `main`.
2. Make sure all existing code still compiles:
   ```bash
   python -m py_compile app.py gemma_helper.py
   ```
3. Open the PR with a clear title and description.
4. Link any related issue (e.g., `Closes #12`).
5. A maintainer will review and may request changes.
6. Once approved, a maintainer will merge your PR.

### PR checklist

- [ ] Code compiles without errors
- [ ] `.env` is NOT committed (no secrets)
- [ ] README updated if UI/features changed
- [ ] PR describes what was changed and why

---

## Commit Conventions

We follow [Conventional Commits](https://www.conventionalcommits.org):

| Type | Use when |
|------|----------|
| `feat:` | New feature |
| `fix:` | Bug fix |
| `docs:` | Documentation only |
| `style:` | Formatting, no code change |
| `refactor:` | Code restructure, no behavior change |
| `test:` | Adding or fixing tests |
| `chore:` | Build/CI/tooling changes |

Examples:

```
feat: add extracted-text tab to results dashboard
fix: handle missing GEMMA_API_KEY gracefully
docs: update README setup instructions
```

---

## Reporting Issues

Found a bug or have a feature idea? Open an issue and include:

- A clear title and description
- Steps to reproduce (for bugs)
- Expected vs. actual behavior
- Screenshots (if UI-related)
- Your environment (OS, Python version)

---

## License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE).

---

_Help us reduce teacher burnout — one graded paper at a time. 📝❤️_
