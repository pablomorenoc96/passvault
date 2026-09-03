"""Configuración global y fixtures compartidas de pytest (python-testing-patterns)."""
from __future__ import annotations

from pathlib import Path
import pytest

from gestorpass.boveda import Boveda, Entrada


@pytest.fixture
def clave_maestra() -> str:
    """Contraseña maestra estándar para pruebas."""
    return "MaestraSegura123!*Test"


@pytest.fixture
def ruta_boveda_temp(tmp_path: Path) -> Path:
    """Ruta temporal aislada para un archivo de bóveda."""
    return tmp_path / "vault_test.dat"


@pytest.fixture
def boveda_vacia(ruta_boveda_temp: Path, clave_maestra: str) -> Boveda:
    """Bóveda nueva y vacía lista para pruebas."""
    return Boveda.crear(ruta_boveda_temp, clave_maestra)


@pytest.fixture
def entradas_muestra() -> list[Entrada]:
    """Conjunto de entradas de prueba con diferentes características."""
    return [
        Entrada(
            sitio="GitHub",
            usuario="octocat",
            contrasena="ghp_SecretToken123!",
            url="https://github.com",
            categoria="Desarrollo",
            notas="Cuenta principal de trabajo",
            favorito=True,
        ),
        Entrada(
            sitio="ProtonMail",
            usuario="seguro@proton.me",
            contrasena="Pr0t0n_M@il_2026",
            url="https://mail.proton.me",
            categoria="Personal",
            notas="Correo cifrado",
            favorito=False,
        ),
        Entrada(
            sitio="Servidor Local",
            usuario="admin",
            contrasena="123456",  # Contraseña débil a propósito para pruebas
            url="http://192.168.1.1",
            categoria="Redes",
            notas="",
            favorito=False,
        ),
    ]


@pytest.fixture
def boveda_con_datos(boveda_vacia: Boveda, entradas_muestra: list[Entrada]) -> Boveda:
    """Bóveda poblada con entradas de prueba guardadas en disco."""
    for e in entradas_muestra:
        boveda_vacia.agregar(e)
    return boveda_vacia
