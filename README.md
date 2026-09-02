<p align="center">
  <img src="assets/banner.png" alt="PassVault Banner" width="100%">
</p>

<p align="center">
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-3.10+-blue.svg" alt="Python 3.10+"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT"></a>
  <a href="#"><img src="https://img.shields.io/badge/platform-Windows-lightgrey.svg" alt="Platform: Windows"></a>
  <a href="#unit-testing"><img src="https://img.shields.io/badge/tests-24%20passed-brightgreen.svg" alt="Tests: 24 passed"></a>
  <a href="#"><img src="https://img.shields.io/badge/language-English%20%7C%20Espa%C3%B1ol-brightgreen.svg" alt="Bilingual"></a>
  <a href="https://github.com/pablomorenoc96/passvault/releases"><img src="https://img.shields.io/badge/download-.exe%20standalone-blueviolet.svg" alt="Download Executable"></a>
</p>

<p align="center">
  <a href="README.es.md"><b>🇪🇸 Leer esta página en Español</b></a>
</p>

---

**PassVault** is a modern, secure, and lightweight desktop password manager for Windows, built with Python and Tkinter.
Features an **AES-256-GCM** encrypted vault, **Argon2id** key derivation, full account management, a CSPRNG-powered password generator with entropy calculation, and native **bilingual support (English / Spanish)**.

---

## ⚡ Why PassVault?

| Feature | PassVault | Cloud Managers (Bitwarden, 1Password) | Electron Apps |
|:---|:---:|:---:|:---:|
| **100% Offline (Zero Cloud)** | ✅ Yes | ❌ Stored on cloud servers | ⚠️ Depends on app |
| **Memory Footprint** | ✅ **~25 MB RAM** | ⚠️ Varies | ❌ 300–600 MB RAM |
| **Startup Speed** | ✅ **Instant (<0.5s)** | ⚠️ Web latency | ❌ Slow boot |
| **Key Derivation** | ✅ **Argon2id (256 MiB)** | ⚠️ PBKDF2 / Argon2 | ⚠️ Varies |
| **Portability** | ✅ **Run from USB drive** | ❌ Requires internet / install | ❌ Heavy binary |
| **No Account / Subscription** | ✅ **Completely free & private** | ❌ Account required | ⚠️ Freemium models |

---

## Getting Started

### Option A: Standalone Executable (.exe) — Recommended for users

Download the latest precompiled **`PassVault.exe`** directly from the **[Releases](https://github.com/pablomorenoc96/passvault/releases)** page. No Python installation required!

### Option B: Running from Source (Recommended for developers)

Double-click **`Iniciar Gestor.bat`**. This script automatically detects Python, installs required dependencies on the first run, and launches the application without an extra terminal window.

Or manually via terminal:

```bash
pip install -r requirements.txt
python gestor_passwords.py
```

> **Desktop Shortcut:**
> Right-click `Iniciar Gestor.bat` → *Show more options* → *Send to* → *Desktop (create shortcut)*.
> You can change the shortcut's icon using `assets\gestor.ico`.

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

## ⭐ Support the Project

If you find PassVault useful, please consider giving it a **star on GitHub**! It helps more people discover the project and motivates further development.

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
