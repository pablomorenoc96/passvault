# AGENTS.md — Universal Agent Instructions for PassVault

This document guides AI coding agents (OpenAI Codex, Antigravity, Claude Code, Cursor) working on the **PassVault** codebase.

---

## 1. Project Context

PassVault is an offline, local-first Windows desktop password manager built with native Python (Tkinter). It prioritizes simplicity, minimal memory footprint (~25 MB RAM), and auditable cryptography without cloud dependencies or subscription accounts.

---

## 2. Cryptographic & Architectural Invariants

Agents must strictly uphold these engineering invariants:

1. **Offline Isolation:** Never add networking libraries (`requests`, `urllib.request`, `httpx`, `socket`). Zero cloud telemetry.
2. **CSPRNG Integrity:** Never use `random` for any security-sensitive value. Always use `secrets` (OS CSPRNG).
3. **Key Derivation:** Argon2id with 256 MiB memory cost, 4 iterations, 4 parallel threads. Fallback to `scrypt`.
4. **AEAD Encryption:** AES-256 in GCM mode. Generate a fresh 96-bit nonce on every write. Always bind header metadata via Authenticated Additional Data (AAD).
5. **Constant-Time Verification:** Compare secrets and master passwords with `secrets.compare_digest`.
6. **Formula Injection Sanitization (CWE-1236):** Prefix any cell starting with `=`, `+`, `-`, `@`, `\t`, `\r` with `'` on export to prevent DDE execution in Excel.
7. **Atomic Writes:** Always flush to disk (`flush()`, `os.fsync()`) and replace files atomically via `.tmp` and `.bak`.

---

## 3. Tooling & Verification

Before proposing or committing changes, run the automated test suite:

```bash
# Run test suite
pytest -v

# Run application locally
python gestor_passwords.py

# Build release executable
pyinstaller gestor_passwords.spec
```

---

## 4. Voice and Writing Style

- Follow humanized engineer standards: direct, technical, honest, and humble.
- Reject marketing tropes (*military-grade*, *battle-tested*, *groundbreaking*, *tapestry*, *delve*).
- Never spam emojis in lists.
- Document limitations and trade-offs explicitly.

---

## 5. Skills Directory (`.agents/skills/`)

- `humanizer`: Strips AI cliches and chatbot patterns from text.
- `improve-codebase-architecture`: Architecture review and modular decoupling.
- `security-audit`: Security vulnerability and timing-safe audit.
- `edge-case-testing`: Extreme boundary and fuzzing checks.
- `changelog-automation`: Standardized release notes in `CHANGELOG.md`.
- `python-testing-patterns`: Comprehensive pytest design and fixture patterns.
