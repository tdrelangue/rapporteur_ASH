<div id="top">

<!-- HEADER STYLE: CLASSIC -->
<div align="center">

<img src="assets/ASH.png" width="70%" style="position: relative; top: 0; right: 0;" alt="Project Logo"/>

# `Rapporteur ASH`

**Automated quarterly report & email sender for ASH / MJPM workflows**

</div>

<em></em>

<!-- BADGES -->
<!-- local repository, no metadata badges. -->

<em>Built with the tools and technologies:</em>

<img src="https://img.shields.io/badge/Python-3776AB.svg?style=flat-square&logo=Python&logoColor=white" alt="Python">
<img src="https://img.shields.io/badge/GitHub%20Actions-2088FF.svg?style=flat-square&logo=GitHub-Actions&logoColor=white" alt="GitHub%20Actions">
<img src="https://img.shields.io/badge/bat-31369E.svg?style=flat-square&logo=bat&logoColor=white" alt="bat">

</div>
<br>

---

## 🌈 Table of Contents

<details>
<summary>Table of Contents</summary>

- [🌈 Table of Contents](#-table-of-contents)
- [🔴 Overview](#-overview)
- [🟠 Features](#-features)
- [🟡 Project Structure](#-project-structure)
    - [🟢 Project Index](#-project-index)
- [🔵 Getting Started](#-getting-started)
    - [🟣 Prerequisites](#-prerequisites)
    - [⚫ Installation](#-installation)
    - [⚪ Usage](#-usage)
    - [🟤 Testing](#-testing)
- [🌟 Roadmap](#-roadmap)
- [🤝 Contributing](#-contributing)
- [📜 License](#-license)
- [✨ Acknowledgments](#-acknowledgments)

</details>

---

## 🔴 Overview

`Rapporteur ASH` is a small desktop tool written in Python to automate a repetitive task in the ASH / MJPM context:

> Generate quarterly reports for protected persons and send them by email with the correct documents attached, using a single interface.

The application is designed for real-world usage in guardianship / social work workflows:

- One click to process a batch of protégés.
- Automatic attachment of the right PDF(s) per person based on folder structure.
- Centralized logging to trace what was sent, when, and to whom.
- Packaged as a Windows executable for non-technical users, while remaining easy to hack and extend in Python.

---

## 🟠 Features

- **Automated email sending**
  - Sends emails via configurable SMTP (host, port, SSL, DSN / MDN options).
  - Supports authenticated accounts (user/password stored via `.env`).
  - Can request read receipts / delivery notifications depending on provider.

- **Quarterly report handling**
  - Designed around trimestrial reports (“rapports trimestriels”) for protected persons.
  - Attaches PDF reports from a structured directory (per protégé).
  - Uses HTML and text templates for email subject and body.

- **Configurable templates**
  - Email subject template: `templates/ASH_subject.txt`
  - Email body template (HTML): `templates/ASH_body.html`
  - Can be customized to match local requirements (institution name, signature, etc.).

- **Batch processing & logging**
  - Processes multiple protégés in a single run.
  - Writes detailed logs under `logs/` (timestamped folders per run).
  - Keeps copies of sent documents in dedicated subfolders for traceability.

- **Windows-friendly**
  - Packaged with PyInstaller into:
    - `Rapporteur ASH.exe` (standalone executable)
    - `rapporteur_ash_setup.exe` (installer)
  - Icons and assets included for a more polished experience.

---

## 🟡 Project Structure

This repository is the *source + build artifacts* for the application.

```text
.
├── ASH_Email.py            # High-level orchestration / UI for ASH emailing
├── Email.py                # Core email composition & sending logic
├── email_utils.py          # Utility functions (attachments, formatting, etc.)
├── Rapports_trimestriel.py # Logic related to quarterly reports
├── config.py               # Configuration layer (SMTP/IMAP, helpers)
├── imap_handler.py         # IMAP utilities (reading mailboxes, flags, etc.)
├── requirements.txt        # Python dependencies
├── templates/
│   ├── ASH_body.html       # HTML template for email body
│   └── ASH_subject.txt     # Template for email subject
├── assets/
│   ├── ASH.png             # Logo
│   ├── icon.ico            # Main app icon
│   └── ...                 # Other icon sizes
├── logs/                   # Execution logs & copies of sent documents
│   └── YYYY-MM-DD_HH-MM-SS/
│       ├── log.txt
│       └── sent/...
├── Protégés/               # Example directory with documents per protégé
├── build/                  # PyInstaller build artifacts
├── dist/                   # Final packaged application (exe, setup, .env used in prod)
├── Rapporteur ASH.spec     # PyInstaller spec file
├── Rapporteur ASH.iss      # Inno Setup script for the installer
├── LICENSE.txt
└── README.md
````

---

## 🔵 Getting Started

### 🟣 Prerequisites

For development:

* **OS:** Windows (target platform), Linux/Mac possible for dev only.
* **Python:** 3.11 (recommended, same as used in this repo).
* **Tools:**

  * `git` (optional, for cloning)
  * `pip` for dependency management

For end-users, only the packaged `.exe` / installer is required.

### ⚫ Installation (development)

Clone the repository and install the dependencies:

```sh
git clone https://github.com/tdrelangue/rapporteur_ASH.git
cd rapporteur_ASH

# (optional but recommended)
python -m venv .venv
.\.venv\Scripts\activate  # sous Windows

pip install -r requirements.txt
```

### ⚪ Configuration

The app expects email configuration and some runtime settings via environment variables (typically stored in a `.env` file loaded by `python-dotenv`).

Typical variables (adapt to your provider):

```env
MAIL_USERNAME=your.email@example.com
MAIL_PASSWORD=your-password-or-app-password

SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USE_SSL=false

IMAP_HOST=imap.example.com
IMAP_MAILBOX=Inbox
IMAP_SENTBOX=Sent
```

You can either:

* Put a `.env` file at the project root for development, or
* Use the `.env` that is shipped inside `dist/` for the packaged application and edit it there.

### ⚪ Usage

#### 1. Run from source (developer mode)

From the project root:

```sh
python ASH_Email.py
```

Typical workflow:

1. Configure `.env` with your email credentials and server details.
2. Configure / verify templates in `templates/`.
3. Organize protégés’ documents in the appropriate directories (e.g. `Protégés/<Nom Prénom>/...pdf`).
4. Launch `ASH_Email.py` and follow the interface / prompts to send the quarterly reports.

Depending on how you use the project, you can also directly call the lower-level scripts:

```sh
# Generate or handle trimestrial report data
python Rapports_trimestriel.py

# Run the core sending logic (if you want finer control)
python send_email.py
```

#### 2. Use the packaged executable (end users)

If you are using the distributed version:

1. Install or unzip from `rapporteur_ash_setup.exe` or `Rapporteur ASH.exe` in `dist/`.
2. Edit the `.env` file next to the executable with the correct SMTP/IMAP settings.
3. Double-click `Rapporteur ASH.exe` and use the interface to send reports.

---

### 🟤 Logs

Every run writes a timestamped folder under `logs/`, for example:

```text
logs/
├── 2025-11-28_15-53-20/
│   ├── log.txt               # Detailed run log
│   └── sent/
│       └── TEST test/
│           └── COS Drelangue.pdf
└── ...
```

These logs are intended to:

* Track which email and attachments were sent.
* Help debug connection / authentication issues.
* Provide a minimal audit trail.

---

## 🌟 Roadmap

Planned or possible evolutions:

* [x] Automate trimestrial report sending with attachments.
* [x] Add detailed logging per batch and per protégé.
* [ ] Add a configuration UI (setup of SMTP/IMAP and templates without editing `.env`).
* [ ] Multi-account support (different sender identities).
* [ ] Better error feedback in the UI (per-email status, retry options).
* [ ] Internationalization (FR/EN templates, labels).

---

## 🤝 Contributing

This project started as an internal automation tool. Contributions, suggestions, and bug reports are welcome if you find it useful in a similar context.

* 🐛 **Issues:**
  Open an issue on GitHub with:

  * Steps to reproduce
  * Logs (redacted of any personal data)
  * Environment (Windows version, Python version, mail provider)

* 💡 **Pull Requests:**

  1. Fork the repository.
  2. Create a feature branch:

     ```sh
     git checkout -b feature/my-improvement
     ```
  3. Commit your changes with a clear message.
  4. Push and open a PR against `main`.

Please avoid committing real personal / patient data (use dummy PDFs in `Protégés/`).

---

## 📜 License

This project is distributed under the terms described in [`LICENSE.txt`](LICENSE.txt).
Check that file for the exact license used.

---

## ✨ Acknowledgments

* Real-world feedback from ASH / MJPM users that inspired and shaped the tool.
* The Python ecosystem: `customtkinter`, `imap_tools`, `Pillow`, `python-dotenv`, and others.
* Internal OrigAI tooling efforts around legal and administrative automation.

---

<div align="right">

[![][back-to-top]](#top)

</div>

[back-to-top]: https://img.shields.io/badge/-BACK_TO_TOP-151515?style=flat-square

