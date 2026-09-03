# Contributing to PassVault

Thank you for your interest in contributing to PassVault. This project aims to remain a simple, lightweight, and auditable offline password manager for Windows.

---

## Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/pablomorenoc96/passvault.git
   cd passvault
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   # On Windows (PowerShell):
   .\venv\Scripts\Activate.ps1
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   pip install pytest pyinstaller
   ```

4. **Run the test suite:**
   ```bash
   pytest -v
   ```

5. **Run the application locally:**
   ```bash
   python gestor_passwords.py
   ```

---

## Architectural & Security Invariants

When submitting a pull request, please make sure your changes strictly uphold these invariants:

1. **Zero Network / 100% Offline:** Never introduce network libraries (`requests`, `urllib.request`, `httpx`, `socket`). PassVault must run entirely offline with zero cloud telemetry.
2. **Cryptographic RNG:** Never use Python's pseudo-random `random` module for secrets, nonces, salts, or passwords. Always use the OS CSPRNG (`secrets`).
3. **AEAD Encryption:** Cryptographic operations must use AES-256-GCM with fresh 96-bit random nonces and AAD header binding.
4. **Key Derivation:** Argon2id (256 MiB RAM, 4 iterations, 4 lanes) with `scrypt` fallback.
5. **Constant-Time Operations:** Use `secrets.compare_digest` when verifying master credentials.
6. **Formula Sanitization (CWE-1236):** Neutralize spreadsheet formula prefixes (`=`, `+`, `-`, `@`, `\t`, `\r`) during CSV/Excel export.
7. **Durability:** File writes must remain atomic via temporary files and `.bak` rotation with `flush()` and `os.fsync()`.

---

## Pull Request Checklist

Before submitting your PR:
- [ ] All unit tests pass (`pytest -v`).
- [ ] New features or fixes include automated tests in `tests/`.
- [ ] Code follows standard PEP 8 conventions.
- [ ] No personal credentials or test vault files are committed.
- [ ] Relevant updates are documented in `CHANGELOG.md`.
