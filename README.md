# GitPilot

> Automate GitHub organization management at scale.

GitPilot is an open-source Python CLI built for DevSecOps, Platform Engineering, and Release Engineering teams to automate repetitive GitHub administration tasks across multiple repositories.

Instead of manually performing the same operation across tens or hundreds of repositories, GitPilot enables safe, repeatable, and auditable bulk operations.

---

## 🚀 Why GitPilot?

Managing GitHub organizations often involves repetitive administrative tasks such as:

- Creating release branches
- Updating repository secrets
- Managing branch protection
- Bulk repository operations

GitPilot aims to simplify these workflows through an intuitive command-line interface.

---

## 🎯 Target Users

- DevSecOps Engineers
- Platform Engineers
- Release Engineers
- DevOps Engineers
- GitHub Organization Administrators

---

## 📦 Current Status

🚧 **Project is under active development.**

### Version 0.1 (In Progress)

- [ ] Bulk branch creation
- [ ] Bulk secret updates
- [ ] CSV repository input
- [ ] Dry-run mode
- [ ] Execution summary

---

## 🛠 Planned Features

### 🌿 Branch Management

- Create branches
- Delete branches
- Merge branches
- Protect branches
- Unprotect branches
- Bulk branch operations

### 🔐 Secret Management

- Create repository secrets
- Update repository secrets
- Delete repository secrets
- Validate secret availability
- Environment secrets support

### 📂 Repository Management

- Repository Variables
- Branch Protection Rules
- Labels
- Repository Settings
- GitHub Actions Variables

### 🚀 Release Management

- Release Branch Creation
- Pull Request Automation
- Release Validation
- Release Notes Support

---

## 💻 Planned CLI Examples

Create a release branch across multiple repositories:

```bash
gitpilot branch create \
    --repos repos.csv \
    --source main \
    --branch release/1.0
```

Update a repository secret:

```bash
gitpilot secret update \
    --repos repos.csv \
    --secret API_KEY \
    --value ********
```

---

## 🏗 Design Principles

- Simple CLI
- Developer First
- Safe by Default
- Dry Run Support
- Idempotent Operations
- Enterprise Ready
- Extensible Architecture

---

## 🗺 Roadmap

### v0.1

- Bulk Branch Creation
- Bulk Secret Updates
- CSV Repository Input
- Dry Run Support
- Execution Summary

### v0.2

- Branch Protection
- Secret Validation
- Repository Variables
- Improved Logging

### v0.3

- Release Management
- Pull Request Automation
- Repository Settings

### v1.0

GitPilot becomes a complete GitHub organization administration toolkit.

---

## 🧰 Tech Stack

- Python 3.12+
- Typer
- GitHub REST API
- PyGithub
- Pytest

---

## 🤝 Contributing

Contributions, feature requests, ideas, and bug reports are welcome.

If you'd like to contribute, feel free to open an issue or submit a pull request.

---

## 📄 License

This project is licensed under the MIT License.

---

## ⭐ Vision

GitPilot aims to become the go-to open-source toolkit for GitHub administrators by making large-scale GitHub organization management fast, reliable, and effortless.
