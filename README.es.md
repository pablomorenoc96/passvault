# PassVault

![PassVault Banner](assets/banner.png)

Gestor de contraseñas de escritorio para Windows, ligero y sin conexión a internet, desarrollado en Python y Tkinter.

PassVault almacena tus credenciales en una base de datos cifrada localmente con AES-256-GCM y derivación de claves Argon2id. Funciona 100% desconectado: sin sockets de red, sin telemetría y sin cuentas ni suscripciones.

[🇺🇸 Read in English](README.md)

---

## Motivación

Construí PassVault como un proyecto personal porque quería una forma sencilla y confiable de guardar credenciales en Windows sin dos problemas habituales en los programas actuales:

1. **Dependencia de la nube:** Muchos gestores modernos te obligan a crear una cuenta remota y sincronizar datos con servidores externos. Si solo buscas una base de datos local que nunca salga de tu máquina, las soluciones en la nube sobran.
2. **Consumo excesivo de memoria:** Casi todas las aplicaciones de escritorio hoy en día están montadas sobre Electron y consumen entre 300 y 600 MB de RAM solo para mostrar una lista de textos. PassVault está hecho con Python nativo y Tkinter; arranca en menos de medio segundo y se mantiene en torno a los 25 MB de RAM.

---

## Detalles Técnicos

- **Cifrado:** AES-256 en modo GCM (Galois/Counter Mode). Cada guardado genera un nonce aleatorio nuevo de 96 bits y un tag de autenticación. Los metadatos de la cabecera (versión, sal, iteraciones) se vinculan al cifrado mediante Datos Adicionales Autenticados (AAD) para impedir cualquier manipulación del archivo.
- **Derivación de clave:** Argon2id a través de `argon2-cffi` configurado con 256 MiB de memoria, 4 iteraciones y 4 hilos en paralelo. Si la librería de CFFI no está disponible, utiliza `hashlib.scrypt` de la librería estándar como respaldo.
- **Escritura atómica:** Los cambios se escriben primero en un archivo temporal, el archivo previo se renombra a `.bak`, y finalmente se reemplaza atómicamente para evitar que un corte de luz o fallo corrompa la base de datos.
- **Generador de contraseñas:** Utiliza el módulo `secrets` de Python (CSPRNG del sistema operativo). Calcula la entropía de Shannon en bits y estima tiempos de descifrado por fuerza bruta.
- **Herramienta de auditoría:** Analiza la bóveda local en busca de contraseñas reutilizadas en varios sitios, credenciales débiles (<60 bits de entropía) y entradas vacías.
- **Localización:** Interfaz bilingüe nativa (Español e Inglés) con autodetección del idioma del sistema y selector manual en Ajustes.

Para conocer la especificación criptográfica detallada, el formato binario y el modelo de amenazas completo, consulta [ARCHITECTURE.md](ARCHITECTURE.md).

---

## Limitaciones (Lo que PassVault NO hace)

Para mantener claras las expectativas sobre el alcance del proyecto:

- **Sin extensión para navegador:** No rellena contraseñas automáticamente en el navegador. Las credenciales se copian con atajos de teclado (`Ctrl+C`, `Ctrl+U`). El portapapeles se limpia solo a los 30 segundos.
- **Sin sincronización entre dispositivos:** PassVault no tiene código de red. Si necesitas sincronizar contraseñas entre tu teléfono móvil y tu computadora, herramientas como Bitwarden o 1Password son mucho más apropiadas.
- **Sin recuperación de contraseña:** La contraseña maestra nunca se almacena en ninguna parte. Si la olvidas, es matemáticamente imposible recuperar los datos.

---

## Instalación y Uso

### Ejecutar desde el código fuente (Recomendado)

Requiere Python 3.10 o superior:

```bash
git clone https://github.com/pablomorenoc96/passvault.git
cd passvault
pip install -r requirements.txt
python gestor_passwords.py
```

O haciendo doble clic en `Iniciar Gestor.bat` en Windows.

### Ejecutable independiente (.exe)

Si no tienes Python instalado, hay binarios precompilados en la pestaña [Releases](https://github.com/pablomorenoc96/passvault/releases).

---

## Almacenamiento de Datos

| Archivo | Ubicación | Descripción |
|:---|:---|:---|
| Bóveda principal | `%APPDATA%\GestorPasswords\vault.dat` | Base de datos cifrada con AES-256-GCM |
| Respaldo | `%APPDATA%\GestorPasswords\vault.dat.bak` | Versión anterior rotada en cada guardado |
| Preferencias | `%APPDATA%\GestorPasswords\preferencias.json` | Ajustes de tema e idioma |

**Modo portable:** Si colocas un archivo `vault.dat` en la misma carpeta que el ejecutable o script (por ejemplo en una memoria USB), PassVault usará esa base de datos local en lugar de la de `%APPDATA%`.

---

## Atajos de Teclado

- `Ctrl + N`: Nueva cuenta
- `Ctrl + E`: Editar cuenta seleccionada
- `Ctrl + C`: Copiar contraseña
- `Ctrl + U`: Copiar usuario
- `Ctrl + F`: Buscar en la lista
- `Ctrl + G`: Generador de contraseñas
- `Ctrl + L`: Bloquear bóveda
- `Supr`: Eliminar cuenta

---

## Pruebas Unitarias

La suite de pruebas cubre derivación de claves, autenticación del cifrado, detección de manipulación en AAD, rechazo de contraseñas erróneas y lógica del generador:

```bash
pip install pytest
pytest -v
```

Las pruebas se ejecutan automáticamente en Windows y Ubuntu en cada commit mediante GitHub Actions.

---

## Licencia

Licencia MIT. Consulta el archivo [LICENSE](LICENSE) para más información.
