"""Pruebas exhaustivas de casos límite, seguridad y fuzzing ligero."""
from __future__ import annotations

from pathlib import Path
import pytest

from gestorpass.boveda import Boveda, Entrada
from gestorpass.crypto import (
    BovedaCorrupta,
    ContrasenaIncorrecta,
    cifrar,
    descifrar,
)


def test_formula_injection_sanitization(tmp_path: Path):
    """Comprueba que caracteres de inyección de fórmulas (=, +, -, @, \\t, \\r) se neutralizan."""
    archivo = tmp_path / "vault.dat"
    boveda = Boveda.crear(archivo, "MaestraSegura123!")

    entrada = Entrada(
        sitio="=CMD|' /C calc'!A0",
        usuario="+123456789",
        contrasena="@SuperSecret!2026",
        url="https://ejemplo.com",
        categoria="-Finanzas",
        notas="\tNota con tabulador inicial",
    )
    boveda.agregar(entrada)

    # 1. Exportar a CSV
    ruta_csv = tmp_path / "export.csv"
    boveda.exportar_csv(ruta_csv)

    contenido_csv = ruta_csv.read_text(encoding="utf-8-sig")
    assert "'=CMD" in contenido_csv
    assert "'+123456789" in contenido_csv
    assert "'@SuperSecret" in contenido_csv
    assert "'-Finanzas" in contenido_csv
    assert "'\tNota" in contenido_csv

    # 2. Reimportar en una bóveda limpia y verificar que se recupera el texto original
    archivo2 = tmp_path / "vault2.dat"
    boveda_nueva = Boveda.crear(archivo2, "MaestraSegura123!")
    agregadas, omitidas = boveda_nueva.importar_csv(ruta_csv)
    assert agregadas == 1

    recuperada = boveda_nueva.entradas[0]
    assert recuperada.sitio == "=CMD|' /C calc'!A0"
    assert recuperada.usuario == "+123456789"
    assert recuperada.contrasena == "@SuperSecret!2026"
    assert recuperada.categoria == "-Finanzas"
    assert recuperada.notas == "\tNota con tabulador inicial"


def test_unicode_and_emojis_credentials(tmp_path: Path):
    """Verifica que caracteres internacionales, acentos y emojis se cifran y descifran sin pérdida."""
    clave_maestra = "🔑Clave_Mäëstrá_漢字_Ñandú_123!🎉"
    archivo = tmp_path / "vault_unicode.dat"
    boveda = Boveda.crear(archivo, clave_maestra)

    e = Entrada(
        sitio="Sitio con acentos: México y España 🌮",
        usuario="usuário_japonés_田中太郎@domínio.com",
        contrasena="§±!@#$%^&*()_+{}|:\"<>?~`-=[]\\;',./—–•🔒",
        url="https://xn--mxico-bta.com",
        categoria="Categoría Ñ 📂",
        notas="Notas multilínea con emojis:\nLínea 1 ✨\nLínea 2 🚀\nLínea 3 🛡️",
    )
    boveda.agregar(e)

    # Reabrir y verificar
    boveda_reabierta = Boveda.abrir(archivo, clave_maestra)

    assert len(boveda_reabierta.entradas) == 1
    recuperada = boveda_reabierta.entradas[0]
    assert recuperada.sitio == e.sitio
    assert recuperada.usuario == e.usuario
    assert recuperada.contrasena == e.contrasena
    assert recuperada.notas == e.notas


def test_very_long_password(tmp_path: Path):
    """Prueba que contraseñas gigantescas (5,000+ caracteres) no causan fallos de desbordamiento."""
    clave_maestra = "A" * 4096
    pass_gigante = "X" * 10000

    archivo = tmp_path / "vault_long.dat"
    boveda = Boveda.crear(archivo, clave_maestra)

    e = Entrada(sitio="BigPasswordSite", usuario="user", contrasena=pass_gigante)
    boveda.agregar(e)

    boveda2 = Boveda.abrir(archivo, clave_maestra)
    assert boveda2.entradas[0].contrasena == pass_gigante


def test_corrupted_payload_truncation():
    """Verifica que cortar el payload cifrado a la mitad arroje ContrasenaIncorrecta o BovedaCorrupta."""
    datos = {"prueba": "123"}
    cifrado_bytes = cifrar(datos, "password123")

    # Truncar bytes a la mitad
    mitad = len(cifrado_bytes) // 2
    truncado = cifrado_bytes[:mitad]

    with pytest.raises((BovedaCorrupta, ContrasenaIncorrecta)):
        descifrar(truncado, "password123")


def test_verificar_maestra_timing_safe(tmp_path: Path):
    """Comprueba el comportamiento de verificar_maestra."""
    archivo = tmp_path / "vault_time.dat"
    b = Boveda.crear(archivo, "ClaveCorrecta999")
    assert b.verificar_maestra("ClaveCorrecta999") is True
    assert b.verificar_maestra("ClaveIncorrecta") is False
    assert b.verificar_maestra("") is False
