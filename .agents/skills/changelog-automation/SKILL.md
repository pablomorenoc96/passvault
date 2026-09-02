---
name: changelog-automation
description: |
  Maintain and update project CHANGELOG.md adhering strictly to Keep a Changelog
  (https://keepachangelog.com) and Semantic Versioning (SemVer 2.0.0).
license: MIT
metadata:
  version: "1.0.0"
---

# Changelog Automation Skill

Standardizes release notes and version history across commits and releases.

## Core Rules

1. **Guiding Principles:** Changelogs are for humans, not machines. Every change must be explained clearly without Git log dumps.
2. **Standard Sections:** Use standard categories under each version:
   - `Added`: for new features.
   - `Changed`: for changes in existing functionality.
   - `Deprecated`: for soon-to-be removed features.
   - `Removed`: for now removed features.
   - `Fixed`: for any bug fixes.
   - `Security`: in case of vulnerabilities or security hardening.
3. **Semantic Versioning (SemVer):**
   - MAJOR version when you make incompatible API/database changes.
   - MINOR version when you add functionality in a backward-compatible manner.
   - PATCH version when you make backward-compatible bug fixes.
