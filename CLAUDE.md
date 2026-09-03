# Claude Code Configuration — PassVault

This file provides project-specific instructions and guidelines for Claude Code.

---

## 1. Project Overview & Boundaries

- **Name:** PassVault
- **Type:** Lightweight, offline desktop password manager for Windows.
- **Tech Stack:** Python 3.10+, Tkinter, `cryptography` (PyCA), `argon2-cffi`, `openpyxl`.
- **Absolute Invariants:**
  - **Zero Network / 100% Offline:** Zero sockets, zero HTTP requests, zero telemetry, zero analytics.
  - **CSPRNG Only:** Never use `random`. Always use `secrets` for passwords, salts, nonces, and tokens.
  - **Ciphers:** AES-256-GCM with 96-bit random nonces and Authenticated Additional Data (AAD).
  - **KDF:** Argon2id (256 MiB memory, 4 iterations, 4 parallelism) with `scrypt` fallback.
  - **Storage:** Atomic file writes with `.tmp` and `.bak` rotation.

---

## 2. Common Developer Commands

- **Run Application:**
  ```bash
  python gestor_passwords.py
  ```
- **Run Unit Tests:**
  ```bash
  pytest -v
  ```
- **Build Standalone Executable (Windows):**
  ```bash
  pyinstaller gestor_passwords.spec
  ```

---

## 3. Engineering & Writing Tone

- **Voice:** Direct, technical, humble, and authentic. Write like a senior open-source maintainer, not a marketing brochure.
- **Prohibited Clichés:** Do not use AI tropes (*delve*, *testament*, *pivotal*, *crucial*, *tapestry*, *military-grade*, *battle-tested*, *seamless*).
- **No Emoji Spam:** Avoid decorating every bullet point with emojis. Use clean markdown hyphens.
- **Honest Trade-offs:** Always acknowledge what PassVault does NOT do (no cloud sync, no browser autofill).

---

## 4. Skills Available in `.claude/skills/`

- `humanizer`: Eradicates AI writing patterns and marketing fluff.
- `improve-codebase-architecture`: Enforces deep modules and clean separation of concerns.
- `security-audit`: Checks for cryptographic hygiene, timing side-channels, and formula injection (CWE-1236).
- `edge-case-testing`: Boundary testing for Unicode, emojis, truncated streams, and extreme inputs.
- `changelog-automation`: Maintains `CHANGELOG.md` according to Keep a Changelog and SemVer.
- `python-testing-patterns`: Comprehensive testing strategies with pytest.
