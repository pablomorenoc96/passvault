"""Rutas, constantes y preferencias de la aplicación."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

APP_NAME = "PassVault"
APP_VERSION = "2.0"
VAULT_FILENAME = "vault.dat"
PREFS_FILENAME = "preferencias.json"

# Valores por defecto de las preferencias del usuario.
DEFAULTS = {
    "idioma": "auto",              # "auto" | "en" | "es"
    "tema": "oscuro",              # "oscuro" | "claro"
    "minutos_autobloqueo": 5,      # 0 = desactivado
    "segundos_portapapeles": 30,   # 0 = no limpiar
    "gen_longitud": 20,
    "gen_mayusculas": True,
    "gen_minusculas": True,
    "gen_numeros": True,
    "gen_simbolos": True,
    "gen_sin_ambiguos": False,
    "ancho_ventana": 1180,
    "alto_ventana": 720,
    "geometria_escalada": False,
}


def directorio_app() -> Path:
    """Carpeta donde vive el script o el .exe."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


def ruta_recurso(nombre: str) -> Path | None:
    """Localiza un archivo de ``assets``, funcione como script o como .exe."""
    candidatos = []
    if getattr(sys, "frozen", False):
        # PyInstaller descomprime los datos en una carpeta temporal.
        base = getattr(sys, "_MEIPASS", None)
        if base:
            candidatos.append(Path(base) / "assets" / nombre)
    candidatos.append(Path(__file__).resolve().parent.parent / "assets" / nombre)
    candidatos.append(directorio_app() / "assets" / nombre)

    for ruta in candidatos:
        if ruta.exists():
            return ruta
    return None


def directorio_datos() -> Path:
    """Carpeta de datos.

    Modo portable: si ya existe un ``vault.dat`` junto al programa (por ejemplo
    en una USB), se usa esa carpeta. Si no, se usa %APPDATA%\\GestorPasswords,
    que sobrevive a recompilaciones y no se pierde al borrar ``dist``.
    """
    local = directorio_app()
    if (local / VAULT_FILENAME).exists():
        return local

    base = os.environ.get("APPDATA") or os.environ.get("XDG_DATA_HOME")
    if base:
        destino = Path(base) / "GestorPasswords"
    else:
        destino = Path.home() / ".gestor_passwords"
    destino.mkdir(parents=True, exist_ok=True)
    return destino


def ruta_vault() -> Path:
    return directorio_datos() / VAULT_FILENAME


def ruta_preferencias() -> Path:
    return directorio_datos() / PREFS_FILENAME


def cargar_preferencias() -> dict:
    prefs = dict(DEFAULTS)
    try:
        with open(ruta_preferencias(), "r", encoding="utf-8") as fh:
            guardadas = json.load(fh)
        if isinstance(guardadas, dict):
            for clave, valor in guardadas.items():
                if clave in DEFAULTS:
                    prefs[clave] = valor
    except (OSError, ValueError):
        pass
    return prefs


def guardar_preferencias(prefs: dict) -> None:
    try:
        limpio = {k: v for k, v in prefs.items() if k in DEFAULTS}
        with open(ruta_preferencias(), "w", encoding="utf-8") as fh:
            json.dump(limpio, fh, indent=2, ensure_ascii=False)
    except OSError:
        pass  # Las preferencias no son criticas: si fallan, se usan las default.
