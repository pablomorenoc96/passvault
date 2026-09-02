<p align="center">
  <img src="assets/banner.png" alt="PassVault Banner" width="100%">
</p>

<p align="center">
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-3.10+-blue.svg" alt="Python 3.10+"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT"></a>
  <a href="#"><img src="https://img.shields.io/badge/platform-Windows-lightgrey.svg" alt="Platform: Windows"></a>
  <a href="#pruebas-unitarias-testing"><img src="https://img.shields.io/badge/tests-24%20passed-brightgreen.svg" alt="Tests: 24 passed"></a>
  <a href="#"><img src="https://img.shields.io/badge/language-English%20%7C%20Espa%C3%B1ol-brightgreen.svg" alt="Bilingüe"></a>
  <a href="https://github.com/pablomorenoc96/passvault/releases"><img src="https://img.shields.io/badge/descargar-.exe%20standalone-blueviolet.svg" alt="Descargar Ejecutable"></a>
</p>

<p align="center">
  <a href="README.md"><b>🇺🇸 Read this page in English</b></a>
</p>

---

**PassVault** es un gestor de contraseñas de escritorio moderno, seguro y ultraligero para Windows, desarrollado en Python y Tkinter.
Cuenta con una bóveda cifrada con **AES-256-GCM**, derivación de clave con **Argon2id**, generador de contraseñas mediante CSPRNG con cálculo de entropía y **soporte bilingüe nativo (Español / Inglés)**.

---

## ⚡ ¿Por qué PassVault?

| Característica | PassVault | Gestores en la Nube (Bitwarden, 1Password) | Aplicaciones en Electron |
|:---|:---:|:---:|:---:|
| **100% Offline (Sin nube)** | ✅ Sí | ❌ Guardado en servidores externos | ⚠️ Depende de la app |
| **Consumo de Memoria** | ✅ **~25 MB RAM** | ⚠️ Variable | ❌ 300–600 MB RAM |
| **Velocidad de Arranque** | ✅ **Instantáneo (<0.5s)** | ⚠️ Latencia de red | ❌ Carga lenta |
| **Derivación de Clave** | ✅ **Argon2id (256 MiB)** | ⚠️ PBKDF2 / Argon2 | ⚠️ Variable |
| **Portabilidad** | ✅ **Usar desde memoria USB** | ❌ Requiere internet / instalación | ❌ Binarios pesados |
| **Sin Cuenta ni Suscripción** | ✅ **100% gratis y privado** | ❌ Requiere cuenta | ⚠️ Modelos freemium |

---

## Empezar

### Opción A: Ejecutable listo para usar (.exe) — Recomendado

Descarga el ejecutable **`PassVault.exe`** directamente desde la pestaña **[Releases](https://github.com/pablomorenoc96/passvault/releases)**. ¡No requiere tener Python instalado!

### Opción B: Ejecutar desde el código fuente

Doble clic en **`Iniciar Gestor.bat`**. Ese archivo busca Python en tu sistema, instala las
librerías que falten la primera vez y abre el programa sin ventana de consola.

O a mano desde una terminal:

```bash
pip install -r requirements.txt
python gestor_passwords.py
```

> **Acceso directo en el Escritorio:**
> Clic derecho sobre `Iniciar Gestor.bat` → *Mostrar más opciones* → *Enviar a* → *Escritorio (crear acceso directo)*.
> Al acceso directo le puedes cambiar el icono por `assets\gestor.ico`.

---

## Qué hace

### Seguridad
- **Bóveda cifrada con AES-256-GCM:** El archivo en disco no contiene ni un solo dato en claro: ni los sitios, ni los usuarios, ni las contraseñas.
- **Llave derivada con Argon2id** (256 MiB, 4 iteraciones) a partir de la contraseña maestra. Cada intento de adivinarla le cuesta al atacante ~0.25 s y 256 MiB de RAM, lo que hace inviable la fuerza bruta. Si falta `argon2-cffi`, usa `scrypt` como respaldo.
- **La maestra no se guarda en ningún lado:** Se comprueba porque el descifrado autentica: si es incorrecta, GCM falla y la rechaza.
- **Cabecera autenticada (AAD):** Si alguien edita el archivo para bajar los parámetros del cifrado, deja de abrir.
- **Bloqueo automático** por inactividad (5 min por defecto, configurable).
- **El portapapeles se limpia solo** 30 segundos después de copiar (configurable).
- **Guardado atómico con respaldo:** Se escribe a `.tmp`, se rota el anterior a `.bak` y se reemplaza. Un corte de luz a media escritura no corrompe la base de datos.

### Soporte Bilingüe (Español / Inglés)
- Interfaz completamente traducida en **Español e Inglés**.
- Detección automática del idioma del sistema operativo.
- Selector de idioma dinámico en la ventana de **Ajustes** (guarda la preferencia).

### Gestión de cuentas
- Alta, **edición** y borrado de cada campo por separado: sitio, usuario, contraseña, URL, categoría, notas y favorito.
- Cada cuenta tiene un identificador único (UUID), así que **dos cuentas del mismo sitio con el mismo usuario no se pisan** al editar o borrar.
- Historial de las últimas 10 contraseñas de cada cuenta.
- Buscador instantáneo, categorías, favoritos y orden por cualquier columna.
- Duplicar una cuenta, abrir su web en el navegador, copiar usuario o contraseña.
- Importar desde Excel, CSV o pegando texto; exportar a Excel o CSV.

### Generador de contraseñas
Al estilo del generador de Avast:
- Longitud de 4 a 64 con deslizador.
- Mayúsculas, minúsculas, números y símbolos, activables por separado.
- Opción de evitar caracteres ambiguos (`l 1 I O 0 S 5`).
- Garantiza al menos un carácter de cada tipo elegido.
- Medidor en vivo: nivel, **bits de entropía** y tiempo estimado para descifrarla.
- Usa `secrets`, el generador criptográfico del sistema operativo (CSPRNG). Nunca `random`.

### Análisis de seguridad
Revisa toda la bóveda y lista lo que hay que arreglar: contraseñas débiles, **contraseñas repetidas en varios sitios** (el riesgo más grave), entradas sin contraseña, y una nota de salud general.

---

## Dónde se guardan los datos

| Recurso | Ubicación |
|---|---|
| Bóveda | `%APPDATA%\GestorPasswords\vault.dat` |
| Respaldo | `%APPDATA%\GestorPasswords\vault.dat.bak` |
| Preferencias | `%APPDATA%\GestorPasswords\preferencias.json` |

**Modo portable:** si colocas un `vault.dat` en la misma carpeta que el programa (por ejemplo en una memoria USB), se usa ese en lugar del de `%APPDATA%`.

Para hacer una copia de seguridad basta con copiar `vault.dat`: va cifrado con AES-256-GCM, así que se puede guardar en la nube sin riesgo mientras la contraseña maestra sea robusta.

> **No hay forma de recuperar la contraseña maestra.** No se guarda en el programa ni en ningún servidor. Si se te olvida, los datos se pierden.

---

## Atajos de teclado

| Atajo | Acción |
|---|---|
| `Ctrl + N` | Nueva cuenta |
| `Ctrl + E` | Editar la seleccionada |
| `Ctrl + C` | Copiar contraseña |
| `Ctrl + U` | Copiar usuario |
| `Ctrl + F` | Ir al buscador |
| `Ctrl + G` | Generador de contraseñas |
| `Ctrl + L` | Bloquear bóveda |
| `Supr` | Eliminar cuenta seleccionada |
| Doble clic | Editar cuenta |
| Clic derecho | Menú contextual de acciones |

---

## Pruebas unitarias (Testing)

El proyecto cuenta con una suite completa de pruebas unitarias que verifican la seguridad criptográfica (Argon2id, scrypt, AES-GCM, manipulación de cabeceras), el generador, i18n y el modelo de datos:

```bash
pip install pytest
pytest -v
```

El repositorio también incluye integración continua (CI) mediante **GitHub Actions** en `.github/workflows/ci.yml`.

---

## Compilar el .exe

```bash
pip install pyinstaller
pyinstaller gestor_passwords.spec
```

Queda en `dist\PassVault.exe`, sin consola y con icono propio.

---

## ⭐ Apoya el proyecto

Si encuentras útil **PassVault**, ¡por favor considera dejar una **estrella (star) en GitHub**! Ayuda a que más personas descubran el proyecto y motiva su desarrollo continuo.

---

## Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo [LICENSE](LICENSE) para más detalles.
