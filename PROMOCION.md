# Kit de Promoción y Lanzamiento para PassVault 🚀

Utiliza estas plantillas optimizadas para dar a conocer **PassVault** en las principales comunidades de desarrolladores y seguridad. Están redactadas en un tono auténtico, técnico y sin parecer spam publicitario.

---

## 1. Configuración del Repositorio en GitHub

En la página principal de tu repositorio ([github.com/pablomorenoc96/passvault](https://github.com/pablomorenoc96/passvault)):
Haz clic en el engranaje ⚙️ junto a **About** en la columna derecha.

### Description:
```text
Modern, lightweight, and 100% offline desktop password manager for Windows built with Python & Tkinter (AES-256-GCM + Argon2id).
```

### Website:
```text
https://github.com/pablomorenoc96/passvault/releases
```

### Topics (Etiquetas clave):
Copia y pega estas etiquetas en el campo de Topics:
```text
python, tkinter, password-manager, cybersecurity, aes-gcm, argon2id, encryption, desktop-app, open-source, security-tools, windows, offline-first
```

---

## 2. Publicación para Reddit

### Opción A: Subreddit `r/Python`
> **Consejo:** Elige la etiqueta (**Flair**) `Showcase` o `Project`. Publica en horario de mañana o mediodía (horario de EE. UU. / Europa). Si puedes, adjunta un vídeo de 15 segundos o una captura.

**Título:**
> I built an offline, open-source desktop password manager in Python with Argon2id and AES-256-GCM (PassVault)

**Contenido:**
```markdown
Hey everyone!

I wanted to share **PassVault**, a lightweight, 100% offline desktop password manager for Windows built purely with Python and Tkinter.

### Why did I build this?
Many popular password managers are moving entirely to cloud subscriptions, and existing desktop alternatives are often built on Electron (which easily eats 400MB+ of RAM) or have complicated legacy setups. I wanted something modern, ultra-fast, completely offline, and with battle-tested cryptography.

### Key Features:
- **Military-grade Encryption:** AES-256-GCM with authenticated headers (AAD) to prevent parameter tampering.
- **Argon2id Key Derivation:** Uses 256 MiB memory cost and 4 iterations (well above OWASP minimums) to make brute-force attacks computationally unfeasible. Includes `scrypt` fallback.
- **100% Offline & Zero Cloud:** No telemetry, no cloud sync, and zero internet requests. Your vault never leaves your machine.
- **CSPRNG Password Generator:** Uses Python's `secrets` module (never `random`) with real-time entropy calculation and crack time estimation.
- **Native Bilingual Support:** Full dynamic switching between English and Spanish.
- **Built-in Security Audit:** Flags reused passwords across sites (the biggest credential stuffing threat), weak entries, and empty accounts.
- **Automated CI/CD:** 24 unit tests running on Windows and Linux via GitHub Actions.

The project is completely open source under the MIT license:
🔗 GitHub: https://github.com/pablomorenoc96/passvault

Precompiled standalone executables (.exe) are also available in the Releases tab if you just want to try it without setting up Python:
📦 Releases: https://github.com/pablomorenoc96/passvault/releases

I'd love to hear your feedback, thoughts on the cryptographic design, or suggestions for new features!
```

---

### Opción B: Subreddit `r/coolgithubprojects`

**Título:**
> PassVault – A secure, lightweight & offline desktop password manager in Python (AES-256-GCM + Argon2id)

**Contenido:**
```markdown
**GitHub:** https://github.com/pablomorenoc96/passvault

PassVault is an offline-first Windows password manager built with Python and Tkinter.

**Highlights:**
- AES-256-GCM authenticated encryption + Argon2id key derivation
- Password generator with live entropy calculation
- Security audit tool (detects reused & weak passwords)
- Full English & Spanish support
- Standalone executable available (.exe)
- MIT License
```

---

## 3. Publicación para Twitter / X

```text
Excited to share PassVault: a lightweight, 100% offline desktop password manager built with #Python and Tkinter 🛡️

✨ Features:
🔒 AES-256-GCM + Argon2id encryption
⚡ Zero cloud, ultra-lightweight
🎲 CSPRNG generator with live entropy
🌎 English & Spanish support

Check out the code on #GitHub 👇
https://github.com/pablomorenoc96/passvault

#OpenSource #Cybersecurity #DevCommunity #Coding
```

---

## 4. Publicación para LinkedIn

```text
¡Hola a todos! 👋

Quiero compartir un proyecto en el que estuve trabajando: **PassVault**, un gestor de contraseñas de escritorio seguro, moderno y 100% offline desarrollado en Python y Tkinter.

En un momento donde la mayoría de soluciones dependen de la nube o consumen cientos de megabytes de RAM con Electron, quise construir una herramienta nativa, rápida y con estándares criptográficos de primer nivel:

🔹 Cifrado autenticado AES-256-GCM con cabecera AAD antimanipulación.
🔹 Derivación de clave maestra con Argon2id (256 MiB de memoria y 4 iteraciones) para neutralizar ataques de fuerza bruta por GPU.
🔹 Generador criptográfico con cálculo de entropía en tiempo real.
🔹 Auditoría de seguridad interna (detección de contraseñas reutilizadas y débiles).
🔹 Soporte bilingüe completo (Español e Inglés).
🔹 Pipeline de CI/CD automatizado con GitHub Actions y suite de pruebas unitarias.

El proyecto es totalmente open-source bajo licencia MIT:
🔗 Repositorio: https://github.com/pablomorenoc96/passvault

¡Cualquier feedback, sugerencia o estrella ⭐ en GitHub es más que bienvenida!

#Python #Cybersecurity #OpenSource #SoftwareDevelopment #GitHub #Programming
```
