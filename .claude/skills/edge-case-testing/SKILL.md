---
name: edge-case-testing
description: |
  Design and execute aggressive boundary tests, fuzzing checks, Unicode edge cases,
  and failure-mode tests to ensure software resilience under extreme conditions.
license: MIT
metadata:
  version: "1.0.0"
---

# Edge-Case Testing Skill

Ensures the software handles malformed, extreme, and international inputs without unexpected crashes.

## Testing Matrix

1. **International Character Sets:** Full Unicode support, emojis, RTL characters, and diacritics in passwords and usernames.
2. **Extreme Input Lengths:** Passwords exceeding 4,000+ characters, massive vaults, empty fields.
3. **Corrupted Stream Handling:** Truncated byte payloads, modified bitflips, invalid JSON envelopes.
4. **File Format Interoperability:** Malformed CSV delimiters, mismatched quotes, empty files.
