---
name: security-audit
description: |
  Audit codebase for security vulnerabilities, cryptographic integrity, timing side-channels,
  and input sanitization (OWASP, CWE-1236, Constant-Time operations).
license: MIT
metadata:
  version: "1.0.0"
---

# Security Audit Skill

Audits and enforces security hygiene across Python applications, with an emphasis on cryptography and data handling.

## Security Checklist

1. **CSPRNG vs Pseudo-random:** Verify that all tokens, nonces, and passwords use `secrets`, never `random`.
2. **Timing Attack Protection:** Master password comparisons and secret verification must use `secrets.compare_digest` or `hmac.compare_digest`.
3. **Formula Injection (CWE-1236):** All data exported to CSV or Excel must sanitize active prefixes (`=`, `+`, `-`, `@`, `\t`, `\r`) to prevent DDE code execution in spreadsheet applications.
4. **AAD Verification:** File headers and metadata must be authenticated alongside the payload (e.g. via AES-GCM Authenticated Additional Data).
5. **Atomic Storage:** Saves must flush buffers (`flush()`, `os.fsync()`) and replace files atomically to prevent data corruption.
