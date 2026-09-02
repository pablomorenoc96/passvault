---
name: improve-codebase-architecture
description: |
  Audit and refactor codebase architecture with disciplined software engineering standards.
  Surfaces shallow modules, identifies decoupling opportunities, documents Architecture
  Decision Records (ADRs), and enforces clean separation of concerns. Based on mattpocock/skills.
license: MIT
metadata:
  version: "1.0.0"
  source: "https://skills.sh/mattpocock/skills/improve-codebase-architecture"
---

# Improve Codebase Architecture

Audit and elevate code quality by identifying architectural shortcomings rather than writing ad-hoc code.

## Core Directives

1. **Deep vs. Shallow Modules:** Prefer deep modules (simple interfaces hiding complex logic) over shallow modules (complex interfaces doing little work).
2. **Strict Layer Decoupling:** Keep presentation, business logic, cryptography, and storage in distinct, isolated layers.
3. **Explicit Data Flow:** Ensure data flows in a single direction. Avoid circular dependencies and hidden global state.
4. **Architecture Decision Records (ADRs):** When taking significant technical decisions (e.g. choosing Argon2id over PBKDF2, choosing AES-GCM over CBC), document the context, trade-offs, and consequences in `ARCHITECTURE.md`.
5. **Threat Modeling:** For security-critical applications, always define in-scope vs out-of-scope security boundaries.
