"""Pruebas unitarias del módulo criptográfico (gestorpass/crypto.py)."""
import json
import pytest
from gestorpass import crypto
from gestorpass.crypto import BovedaCorrupta, ContrasenaIncorrecta

# KDF ligero para ejecutar pruebas unitarias rápidamente
KDF_TEST_SCRYPT = {"algo": "scrypt", "n": 1024, "r": 8, "p": 1}
KDF_TEST_ARGON2 = {
    "algo": "argon2id",
    "memoria_kib": 1024,
    "iteraciones": 1,
    "paralelismo": 1,
}


def test_cifrar_y_descifrar_con_scrypt():
    datos = {"usuario": "admin", "cuentas": [{"sitio": "test.com", "pass": "1234"}]}
    password = "clave_maestra_segura"

    cifrado = crypto.cifrar(datos, password, kdf=KDF_TEST_SCRYPT)
    assert isinstance(cifrado, bytes)

    recuperados, kdf_usado = crypto.descifrar(cifrado, password)
    assert recuperados == datos
    assert kdf_usado["algo"] == "scrypt"


def test_cifrar_y_descifrar_con_argon2id():
    if not crypto.HAY_ARGON2:
        pytest.skip("argon2-cffi no está disponible en este entorno")

    datos = {"entradas": [{"id": "uuid-1", "sitio": "ejemplo.org"}]}
    password = "otra_clave_super_secreta"

    cifrado = crypto.cifrar(datos, password, kdf=KDF_TEST_ARGON2)
    recuperados, kdf_usado = crypto.descifrar(cifrado, password)
    assert recuperados == datos
    assert kdf_usado["algo"] == "argon2id"


def test_contrasena_incorrecta_falla():
    datos = {"secreto": "información confidencial"}
    cifrado = crypto.cifrar(datos, "password_correcto", kdf=KDF_TEST_SCRYPT)

    with pytest.raises(ContrasenaIncorrecta):
        crypto.descifrar(cifrado, "password_incorrecto")


def test_boveda_corrupta_formato_invalido():
    with pytest.raises(BovedaCorrupta):
        crypto.descifrar(b"esto no es json ni una boveda valida", "password")


def test_boveda_tampered_aad():
    """Si un atacante modifica la cabecera en claro, el AAD de AES-GCM debe rechazarlo."""
    datos = {"secreto": "42"}
    cifrado = crypto.cifrar(datos, "password", kdf=KDF_TEST_SCRYPT)

    archivo = json.loads(cifrado.decode("utf-8"))
    # Manipular el salt o nonce
    archivo["sal"] = crypto._b64e(b"\x00" * crypto.LONGITUD_SAL)
    manipulado = json.dumps(archivo).encode("utf-8")

    with pytest.raises((ContrasenaIncorrecta, BovedaCorrupta)):
        crypto.descifrar(manipulado, "password")


def test_boveda_tampered_datos():
    """Si se modifica el payload cifrado, GCM debe fallar con InvalidTag -> ContrasenaIncorrecta."""
    datos = {"secreto": "42"}
    cifrado = crypto.cifrar(datos, "password", kdf=KDF_TEST_SCRYPT)

    archivo = json.loads(cifrado.decode("utf-8"))
    payload = bytearray(crypto._b64d(archivo["datos"]))
    payload[0] ^= 0xFF  # Voltear bits
    archivo["datos"] = crypto._b64e(bytes(payload))
    manipulado = json.dumps(archivo).encode("utf-8")

    with pytest.raises(ContrasenaIncorrecta):
        crypto.descifrar(manipulado, "password")
