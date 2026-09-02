# Changelog

All notable changes to **PassVault** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2.0.0] - 2026-09-02

### Added
- **Full Bilingual Localization:** Complete English and Spanish interface with automatic Windows system locale detection and a runtime language switch in Settings.
- **Formula Injection Mitigation:** Protection against CSV/Excel Formula Injection (CWE-1236) by neutralizing active cell prefixes (`=`, `+`, `-`, `@`, `\t`, `\r`) during export and restoring original values on import.
- **Constant-Time Master Password Verification:** Implemented `secrets.compare_digest` in `verificar_maestra` to eliminate timing side-channel attacks.
- **Comprehensive Edge-Case Test Suite:** Added `tests/test_edge_cases.py` covering Unicode credentials, emojis, very long passwords (10,000+ characters), truncated payload error handling, and formula sanitization. Total automated test count increased to 29 tests.
- **Architectural Documentation:** Added `ARCHITECTURE.md` documenting the threat model, cryptographic specifications (Argon2id, AES-256-GCM, AAD), binary file structure, and atomic write durability.
- **Automated CI/CD Workflows:** Configured GitHub Actions matrix testing across Windows and Linux on Python 3.10 through 3.13, and automated binary compilation on tag release.
- **Pixel-Perfect Banner & Visuals:** Uniform 32px pill badges, regular typography, and exact coordinate alignment for project branding.

### Changed
- Refactored project name and binary artifact to **PassVault**.
- Reorganized codebase into clean modular package structure under `gestorpass/`.
- Streamlined documentation to adopt an authentic, honest open-source tone, clearly specifying project scope and limitations.

---

## [1.0.0] - 2026-08-15

### Added
- Initial release of the desktop password manager.
- Local AES-256-GCM authenticated encryption.
- Argon2id key derivation with 256 MiB memory cost and scrypt fallback.
- CSPRNG password generator with Shannon entropy calculation.
- Vault audit tool for weak and reused passwords.
- Desktop UI built on native Python Tkinter.
