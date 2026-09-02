# PassVault 2.0 (Gestor de Contraseñas)

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Platform: Windows](https://img.shields.io/badge/platform-Windows-lightgrey.svg)](#)
[![Tests](https://img.shields.io/badge/tests-24%20passed-brightgreen.svg)](#pruebas-unitarias-testing)
[![Language: Bilingual](https://img.shields.io/badge/language-English%20%7C%20Espa%C3%B1ol-brightgreen.svg)](#)

[🇺🇸 Read in English](README.md)

Gestor de contraseñas de escritorio para Windows, desarrollado en Python + Tkinter.
Bóveda cifrada, soporte bilingüe (Español / English), edición completa de cuentas y generador de contraseñas aleatorias con medidor de fortaleza y cálculo de entropía.

---

## Empezar

### Opción A: Con Python (recomendada para desarrollo)

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

### Opción B: Ejecutable listo para usar (.exe)

Puedes compilar tu propio ejecutable independiente o descargarlo directamente desde la pestaña **Releases** de este repositorio de GitHub. No requiere tener Python instalado.

La primera vez te pedirá crear una **contraseña maestra**. Si deseas importar cuentas existentes, puedes utilizar el menú de importación con archivos Excel o CSV (ver plantilla de prueba en `ejemplo_cuentas.csv`).

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

El proyecto cuenta con una suite completa de pruebas unitarias que verifican la seguridad criptográfica (Argon2id, scrypt, AES-GCM, manipulación de cabeceras), el generador, i18n y el modelo de datos.

Para ejecutar los tests localmente:

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

## Estructura del proyecto

```
.github/workflows/         integración continua (GitHub Actions)
assets/                    iconos e imágenes de la aplicación
gestorpass/                paquete principal de la aplicación
  config.py                rutas y preferencias del usuario
  escala.py                soporte de pantallas con escalado DPI (Windows)
  i18n.py                  catálogo bilingüe (Español / Inglés)
  crypto.py                Argon2id / scrypt + AES-256-GCM autenticado
  boveda.py                modelo de datos, CRUD, importar/exportar
  generador.py             generador seguro con secrets y cálculo de entropía
  fortaleza.py             evaluador de fortaleza y tiempo de descifrado
  tema.py                  paletas y estilos (modo oscuro y claro)
  widgets.py               componentes y controles visuales reutilizables
  ui_acceso.py             pantallas de inicio, creación y desbloqueo
  ui_principal.py          ventana principal y tabla de cuentas
  ui_entrada.py            formulario de alta y edición de cuentas
  ui_generador.py          diálogo interactivo del generador
  ui_dialogos.py           importación masiva, auditoría y ajustes con selector de idioma
  app.py                   coordinador de sesión y ciclo de vida
herramientas/              utilidades auxiliares
  crear_icono.py           genera assets/gestor.ico con Pillow
  organizar_excel.py       utilidad para ordenar listas desorganizadas de Excel
tests/                     pruebas unitarias automatizadas con pytest
ejemplo_cuentas.csv        plantilla de datos ficticios para pruebas de importación
gestor_passwords.py        punto de entrada de la aplicación
gestor_passwords.spec      receta optimizada para PyInstaller
Iniciar Gestor.bat         lanzador automático para Windows
requirements.txt           dependencias del proyecto
LICENSE                    licencia de código abierto MIT
```

---

## Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo [LICENSE](LICENSE) para más detalles.
