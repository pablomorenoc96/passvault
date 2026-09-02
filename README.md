# PassVault

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Platform: Windows](https://img.shields.io/badge/platform-Windows-lightgrey.svg)](#)
[![Tests](https://img.shields.io/badge/tests-24%20passed-brightgreen.svg)](#unit-testing)
[![Language: Bilingual](https://img.shields.io/badge/language-English%20%7C%20Espa%C3%B1ol-brightgreen.svg)](#)

[🇪🇸 Leer en Español](README.es.md)

A modern, secure, and lightweight desktop password manager for Windows, built with Python and Tkinter.
Features an **AES-256-GCM** encrypted vault, **Argon2id** key derivation, full account management, a CSPRNG-powered password generator with entropy calculation, and native **bilingual support (English / Spanish)**.

---

## Getting Started

### Option A: Running with Python (Recommended for development)

Double-click **`Iniciar Gestor.bat`**. This script automatically detects Python, installs required dependencies on the first run, and launches the application without an extra terminal window.

Or manually via terminal:

```bash
pip install -r requirements.txt
python gestor_passwords.py
```

> **Desktop Shortcut:**
> Right-click `Iniciar Gestor.bat` → *Show more options* → *Send to* → *Desktop (create shortcut)*.
> You can change the shortcut's icon using `assets\gestor.ico`.

### Option B: Standalone Executable (.exe)

You can compile a standalone executable or download the latest precompiled release from the **Releases** tab. No Python installation required.

On the first launch, you will be prompted to create a **master password**. You can also import existing accounts from CSV or Excel files (see sample template in `ejemplo_cuentas.csv`).

---

## Features

### Security & Cryptography
- **AES-256-GCM Authenticated Encryption:** The stored database contains zero plaintext data: sites, usernames, URLs, categories, notes, and passwords are all fully encrypted.
- **Argon2id Key Derivation:** Master key derived using Argon2id (256 MiB memory cost, 4 iterations, 4 parallelism threads), exceeding OWASP recommendations. Brute-force attacks require prohibitive computational memory. Includes `scrypt` fallback.
- **Zero Knowledge Architecture:** The master password is never stored anywhere on disk or in memory. Decryption authenticates via GCM tag; incorrect passwords immediately fail authentication.
- **Authenticated Additional Data (AAD):** Prevents tampering with header metadata or downgrading encryption parameters.
- **Automatic Inactivity Lock:** Configurable auto-lock (5 minutes default).
- **Clipboard Auto-Clear:** Clears copied passwords from the system clipboard after 30 seconds (configurable).
- **Atomic File Saving with Backup:** Writes to `.tmp`, rotates the previous vault to `.bak`, and atomically replaces the file. Power outages during write operations will not corrupt the database.

### Bilingual Support (English / Spanish)
- Full UI translation in **English and Spanish**.
- Automatically detects system locale on startup.
- Dynamic language switcher in the **Settings** dialog with instant preference persistence.

### Account Management
- Create, edit, and delete individual account fields: site, username, password, URL, category, notes, and favorite status.
- Unique UUID identification prevents collisions between multiple accounts sharing the same site or username.
- Previous password history tracking (stores last 10 passwords per account).
- Instant search filter across all fields, category grouping, favorites, and sortable columns.
- Duplicate account, open web URL in default browser, and quick copy actions.
- Bulk import/export via Excel (.xlsx), CSV, and raw text.

### Cryptographic Password Generator
- Length slider from 4 to 64 characters.
- Toggles for Uppercase, Lowercase, Numbers, and Symbols.
- Option to exclude ambiguous characters (`l 1 I O 0 S 5`).
- Guaranteed inclusion of at least one character from each selected set.
- Real-time entropy calculation (in bits) and brute-force crack time estimates.
- Built strictly using `secrets` (operating system CSPRNG), never pseudorandom `random`.

### Security Audit
Scans your entire vault to detect security risks:
- Weak passwords.
- **Reused passwords across different accounts** (the highest credential stuffing risk).
- Empty password entries.
- Overall vault health score (0-100).

---

## Data Storage

| Resource | Path |
|---|---|
| Encrypted Vault | `%APPDATA%\GestorPasswords\vault.dat` |
| Vault Backup | `%APPDATA%\GestorPasswords\vault.dat.bak` |
| User Preferences | `%APPDATA%\GestorPasswords\preferencias.json` |

**Portable Mode:** If a `vault.dat` file exists in the same folder as the executable/script (e.g., on a USB drive), PassVault uses it instead of `%APPDATA%`.

> **Notice:** There is no master password recovery mechanism. Passwords are never sent to any server. If you lose your master password, your encrypted data cannot be recovered.

---

## Keyboard Shortcuts

| Shortcut | Action |
|---|---|
| `Ctrl + N` | New account |
| `Ctrl + E` | Edit selected account |
| `Ctrl + C` | Copy password |
| `Ctrl + U` | Copy username |
| `Ctrl + F` | Focus search bar |
| `Ctrl + G` | Open password generator |
| `Ctrl + L` | Lock vault |
| `Del` | Delete selected account |
| Double-click | Edit account |
| Right-click | Context action menu |

---

## Unit Testing

PassVault includes a complete automated test suite covering cryptography (AES-256-GCM, Argon2id, scrypt, tampering detection), the CSPRNG generator, password entropy, and vault data models:

```bash
pip install pytest
pytest -v
```

All tests run continuously via **GitHub Actions** across Windows and Linux (`.github/workflows/ci.yml`).

---

## Building the Executable

```bash
pip install pyinstaller
pyinstaller gestor_passwords.spec
```

The optimized standalone binary will be created in `dist\PassVault.exe`.

---

## Project Structure

```
.github/workflows/         Continuous Integration (GitHub Actions)
assets/                    Application icons and graphics
gestorpass/                Core application package
  config.py                Application paths and user preferences
  escala.py                High-DPI display awareness (Windows)
  i18n.py                  Internationalization engine (English / Spanish)
  crypto.py                Argon2id / scrypt + AES-256-GCM encryption
  boveda.py                Data model, CRUD, bulk import/export
  generador.py             CSPRNG generator & entropy calculation
  fortaleza.py             Password strength analyzer & crack time estimation
  tema.py                  Visual color themes (Dark & Light)
  widgets.py               Reusable UI components and custom widgets
  ui_acceso.py             Authentication, vault creation, and unlock screens
  ui_principal.py          Main window, treeview table, and details panel
  ui_entrada.py            Account creation and edit form
  ui_generador.py          Interactive generator dialog
  ui_dialogos.py           Settings (language/theme), security audit, mass import
  app.py                   Application orchestration and lifecycle
herramientas/              Utilities
  crear_icono.py           Icon generator script
  organizar_excel.py       Script to structure unformatted password spreadsheets
tests/                     Automated test suite with pytest
ejemplo_cuentas.csv        Sample dummy dataset for import testing
gestor_passwords.py        Application entry point
gestor_passwords.spec      PyInstaller build configuration
Iniciar Gestor.bat         Windows launcher script
requirements.txt           Project dependencies
LICENSE                    MIT License
```

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
