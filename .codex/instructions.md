# OpenAI Codex Project Instructions — PassVault

This project is configured to follow the universal guidelines defined in `AGENTS.md`.

## Key Directives for Codex:
- **Language & Runtime:** Python 3.10+ on Windows / Tkinter.
- **Crypto Rules:** AES-256-GCM + Argon2id (256 MiB RAM). Always use `secrets`, never `random`.
- **Offline Invariant:** Zero network sockets, zero external API calls.
- **Test Command:** `pytest -v`
- **Reference Docs:** See `ARCHITECTURE.md` for cryptographic details and `AGENTS.md` for the cross-agent specification.
