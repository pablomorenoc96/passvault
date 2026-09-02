# PassVault Technical Architecture & Cryptographic Specification

This document details the architectural design, security model, and cryptographic specifications of **PassVault**.

---

## 1. System Architecture

PassVault is structured into decoupled modules with a strict unidirectional dependency hierarchy:

```
┌─────────────────────────────────────────────────────────────┐
│                    Presentation Layer                       │
│  gestorpass/ui_principal.py · ui_entrada.py · ui_acceso.py   │
└──────────────────────────────┬──────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────┐
│                    Application Controller                   │
│                     gestorpass/app.py                       │
└──────────────┬───────────────────────────────┬──────────────┘
               │                               │
┌──────────────▼─────────────┐   ┌─────────────▼──────────────┐
│        Data Model          │   │      Security Engines      │
│    gestorpass/boveda.py    │   │  crypto.py · fortaleza.py  │
│   (CRUD, Import, Export)   │   │    · generador.py (CSPRNG) │
└──────────────┬─────────────┘   └─────────────┬──────────────┘
               │                               │
               └───────────────┬───────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────┐
│                    Storage & OS Subsystem                   │
│   Atomic File I/O · Win32 DPI API · Secrets OS CSPRNG       │
└─────────────────────────────────────────────────────────────┘
```

### Module Responsibilities

| Module | Responsibility | External Dependencies |
|:---|:---|:---|
| `crypto.py` | Key derivation, AEAD encryption/decryption, AAD verification | `cryptography`, `argon2-cffi` |
| `boveda.py` | Data structure (`Entrada`), UUID tracking, CSV/Excel parsing | `openpyxl` |
| `generador.py` | CSPRNG password generation, Shannon entropy calculation | Python `secrets` |
| `fortaleza.py` | Brute-force crack time modeling and dictionary penalty checks | Python standard library |
| `i18n.py` | Bilingual translation catalog and OS locale detection | `ctypes` (Win32) |
| `config.py` | Path resolution (`%APPDATA%` vs portable USB) and preferences | Standard library |

---

## 2. Threat Model

In security engineering, defining what an application defends against—and what it explicitly cannot defend against—is essential.

### In-Scope (Defended Threats)

1. **Physical Laptop Theft or Stolen Storage Media:**
   An adversary who gains physical access to the machine's drive finds only `vault.dat`. The file contains zero plaintext metadata, site names, usernames, or passwords.
2. **Offline Brute-Force & Dictionary Attacks:**
   An attacker attempting to crack the master password offline faces memory-hard Argon2id derivation (256 MiB RAM per attempt), rendering GPU and ASIC cracking rigs cost-prohibitive.
3. **Database Downgrade & Parameter Tampering:**
   An attacker cannot modify the file header to reduce Argon2 iterations or memory cost. All header metadata is cryptographically bound into the AES-GCM cipher via Authenticated Additional Data (AAD). Any byte modification invalidates the authentication tag.
4. **Sudden Power Loss / Crash during File Save:**
   Write operations are atomic. A power failure never leaves a half-written or corrupted vault.

### Out-of-Scope (Host-Compromised Threats)

Like all desktop password managers (including Bitwarden, KeePassXC, and 1Password), PassVault cannot defend against an attacker who has already compromised the host operating system:

1. **Kernel-level keyloggers or memory scrapers:** An adversary with root/SYSTEM privileges or malware active in the user session can read decrypted passwords from process memory or capture keystrokes.
2. **Compromised clipboard monitors:** While PassVault auto-clears the clipboard after 30 seconds, third-party clipboard history managers (if running on the host) may log copied text.
3. **Master password loss:** There is no back-door, telemetry, or remote recovery mechanism. If the user forgets their master password, the data is unrecoverable.

---

## 3. Cryptographic Specification

### A. Key Derivation Function (KDF)

The master key is derived from the user's master password using **Argon2id** (the winner of the Password Hashing Competition):

| Parameter | Value | Rationale |
|:---|:---|:---|
| Algorithm | `Argon2id` (v1.3) | Hybrid defense against side-channel and GPU/ASIC attacks |
| Memory Cost | **256 MiB** (`262,144 KiB`) | Well above OWASP minimum (19 MiB); forces ~0.25s compute per try |
| Time Cost | **4 iterations** | Multi-pass memory hashing |
| Parallelism | **4 lanes / threads** | Optimal utilization of modern multi-core CPUs |
| Salt Length | **16 bytes (128 bits)** | Generated per-vault using `secrets.token_bytes(16)` |
| Derived Key Length | **32 bytes (256 bits)** | Matches AES-256 key size |

*Fallback:* If `argon2-cffi` is unavailable in the host environment, the system automatically falls back to standard `hashlib.scrypt` with parameters `N=65536, r=8, p=1`.

### B. Authenticated Encryption (AEAD)

Vault payload encryption is performed using **AES-256-GCM**:

- **Cipher:** AES-256 in Galois/Counter Mode (GCM).
- **Nonce:** 12 bytes (96 bits), freshly generated via `secrets.token_bytes(12)` on every write operation. Nonces are never reused.
- **Authentication Tag:** 16 bytes (128 bits) appended to the ciphertext.
- **Authenticated Additional Data (AAD):**
  The canonical JSON representation of the file header (`version`, `kdf` settings, and `sal`) is passed as AAD into the cipher:
  ```python
  aad = json.dumps(cabecera, sort_keys=True).encode("utf-8")
  ```
  If any field in the header is tampered with, `AESGCM.decrypt` raises an `InvalidTag` exception and aborts without decrypting.

---

## 4. Storage & File Format

The database is stored as an encoded JSON envelope with the following schema:

```json
{
  "version": 1,
  "kdf": {
    "algo": "argon2id",
    "memoria_kib": 262144,
    "iteraciones": 4,
    "paralelismo": 4
  },
  "sal": "<base64 encoded 16-byte salt>",
  "nonce": "<base64 encoded 12-byte nonce>",
  "datos": "<base64 encoded ciphertext + 16-byte GCM authentication tag>"
}
```

### Atomic File Write Flow

To ensure ACID-like durability on the local filesystem:

1. Data is serialized and encrypted in memory.
2. The payload is written to a temporary sibling file: `vault.dat.tmp`.
3. Flushed to disk via `flush()` and `os.replace`.
4. If an existing `vault.dat` exists, it is rotated to `vault.dat.bak`.
5. The temporary file replaces `vault.dat` in an atomic filesystem operation.

---

## 5. Security Audit & Entropy Model

PassVault evaluates password security using Shannon entropy combined with dictionary penalties:

$$\text{Entropy} = L \times \log_2(N)$$

Where $L$ is password length and $N$ is the effective character set size (e.g., $N = 26 + 26 + 10 + 32 = 94$).

- **Crack Time Estimation:** Modeled against an attacker capable of testing $10^{10}$ hashes per second.
- **Dictionary Penalty:** Passwords matching common word lists or low-diversity patterns (e.g., `123456`, `qwerty`, pure digits) are penalized to 0 bits of effective entropy.
- **Vault Audit:** Identifies identical password hashes across distinct accounts, alerting users to credential stuffing vulnerabilities.
