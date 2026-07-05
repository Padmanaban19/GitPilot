# Contributing to GitPilot

First off, thank you for your interest in contributing to GitPilot!

GitPilot aims to simplify GitHub organization administration by providing a safe, reliable, and developer-friendly CLI for bulk GitHub operations.

Whether you're fixing bugs, improving documentation, or suggesting new features, your contributions are greatly appreciated.

---

## Getting Started

### Prerequisites

- Python 3.12+
- Git
- GitHub Account

Clone the repository:

```bash
git clone https://github.com/<your-github-username>/GitPilot.git
cd GitPilot
```

Install dependencies:

```bash
pip install -e .
```

---

## Development Workflow

1. Fork the repository
2. Create a feature branch

```bash
git checkout -b feature/my-feature
```

3. Make your changes

4. Run tests

```bash
pytest
```

5. Commit your changes

Example:

```text
feat(branch): add bulk branch creation
```

6. Push your branch

7. Open a Pull Request

---

## Commit Message Convention

We follow Conventional Commits.

Examples:

```
feat(branch): add branch creation

fix(secret): handle missing repository

docs: update README

refactor(api): simplify GitHub client

test(branch): add unit tests
```

---

## Code Style

- Keep functions small.
- Write descriptive names.
- Add type hints whenever possible.
- Include docstrings for public APIs.
- Add unit tests for new functionality.

---

## Reporting Bugs

Please include:

- GitPilot version
- Python version
- Operating system
- Steps to reproduce
- Expected behavior
- Actual behavior

---

## Feature Requests

Before opening a feature request, please check existing issues.

Describe:

- Problem
- Proposed solution
- Example usage

---

## Questions

Feel free to open a GitHub Discussion or Issue.

Happy coding!
