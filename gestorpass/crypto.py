"""Cifrado de la bóveda: Argon2id (o scrypt) + AES-256-GCM.

La contraseña maestra nunca se guarda en ningún lado. De ella se deriva una
llave de 32 bytes con un KDF lento y con sal aleatoria; esa llave cifra el JSON
completo de la bóveda. Si la contraseña es incorrecta, el tag de autenticación
de GCM no válida y se levanta ``ContrasenaIncorrecta``.
"""
from __future__ import annotations

import base64
import json
import os
import secrets

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt

try:  # argon2-cffi es la opción preferida (más resistente a GPU/ASIC).
    from argon2.low_level import Type as _Argon2Type
    from argon2.low_level import hash_secret_raw as _argon2_raw

    HAY_ARGON2 = True
except ImportError:  # pragma: no cover - depende del entorno
    HAY_ARGON2 = False

FORMATO_VERSION = 1
LONGITUD_LLAVE = 32   # AES-256
LONGITUD_SAL = 16
LONGITUD_NONCE = 12   # recomendado para GCM

# Parámetros Argon2id muy por encima del mínimo recomendado por OWASP.
# Cuesta ~0.25 s por intento en un equipo moderno: imperceptible al abrir la
# bóveda, carísimo para quien intente millones de contraseñas por fuerza bruta.
ARGON2_MEMORIA_KIB = 262144   # 256 MiB
ARGON2_ITERACIONES = 4
ARGON2_PARALELISMO = 4

# Parámetros scrypt para el respaldo si no hay argon2-cffi.
SCRYPT_N = 2 ** 16
SCRYPT_R = 8
SCRYPT_P = 1


class ErrorBoveda(Exception):
    """Error genérico al leer o escribir la bóveda."""


class ContrasenaIncorrecta(ErrorBoveda):
    """La contraseña maestra no descifra la bóveda."""


class BovedaCorrupta(ErrorBoveda):
    """El archivo existe pero no tiene un formato válido."""


def _b64e(datos: bytes) -> str:
    return base64.b64encode(datos).decode("ascii")


def _b64d(texto: str) -> bytes:
    return base64.b64decode(texto.encode("ascii"))


def _derivar_llave(contrasena: str, sal: bytes, kdf: dict) -> bytes:
    algoritmo = kdf.get("algo", "argon2id")
    secreto = contrasena.encode("utf-8")

    if algoritmo == "argon2id":
        if not HAY_ARGON2:
            raise ErrorBoveda(
                "Esta bóveda usa Argon2id pero falta el paquete 'argon2-cffi'.\n"
                "Instálalo con:  pip install argon2-cffi"
            )
        return _argon2_raw(
            secret=secreto,
            salt=sal,
            time_cost=int(kdf.get("iteraciones", ARGON2_ITERACIONES)),
            memory_cost=int(kdf.get("memoria_kib", ARGON2_MEMORIA_KIB)),
            parallelism=int(kdf.get("paralelismo", ARGON2_PARALELISMO)),
            hash_len=LONGITUD_LLAVE,
            type=_Argon2Type.ID,
        )

    if algoritmo == "scrypt":
        return Scrypt(
            salt=sal,
            length=LONGITUD_LLAVE,
            n=int(kdf.get("n", SCRYPT_N)),
            r=int(kdf.get("r", SCRYPT_R)),
            p=int(kdf.get("p", SCRYPT_P)),
        ).derive(secreto)

    raise BovedaCorrupta(f"KDF desconocido: {algoritmo!r}")


def parametros_kdf() -> dict:
    """Parámetros del KDF que se usaran para una bóveda nueva."""
    if HAY_ARGON2:
        return {
            "algo": "argon2id",
            "memoria_kib": ARGON2_MEMORIA_KIB,
            "iteraciones": ARGON2_ITERACIONES,
            "paralelismo": ARGON2_PARALELISMO,
        }
    return {"algo": "scrypt", "n": SCRYPT_N, "r": SCRYPT_R, "p": SCRYPT_P}


def cifrar(datos: dict, contrasena: str, kdf: dict | None = None) -> bytes:
    """Serializa ``datos`` a JSON y devuelve el archivo de bóveda completo."""
    kdf = kdf or parametros_kdf()
    sal = secrets.token_bytes(LONGITUD_SAL)
    nonce = secrets.token_bytes(LONGITUD_NONCE)

    llave = _derivar_llave(contrasena, sal, kdf)
    payload = json.dumps(datos, ensure_ascii=False, separators=(",", ":")).encode("utf-8")

    # La cabecera va como "additional authenticated data": si alguien la
    # manipula (por ejemplo para bajar los parámetros del KDF), GCM lo detecta.
    cabecera = {
        "formato": FORMATO_VERSION,
        "cifrado": "AES-256-GCM",
        "kdf": kdf,
        "sal": _b64e(sal),
        "nonce": _b64e(nonce),
    }
    aad = json.dumps(cabecera, sort_keys=True, separators=(",", ":")).encode("utf-8")
    cifrado = AESGCM(llave).encrypt(nonce, payload, aad)

    archivo = dict(cabecera)
    archivo["datos"] = _b64e(cifrado)
    return json.dumps(archivo, indent=1).encode("utf-8")


def descifrar(contenido: bytes, contrasena: str) -> tuple[dict, dict]:
    """Devuelve ``(datos, kdf)`` a partir del contenido del archivo de bóveda."""
    try:
        archivo = json.loads(contenido.decode("utf-8"))
        kdf = archivo["kdf"]
        sal = _b64d(archivo["sal"])
        nonce = _b64d(archivo["nonce"])
        cifrado = _b64d(archivo["datos"])
        cabecera = {k: archivo[k] for k in ("formato", "cifrado", "kdf", "sal", "nonce")}
    except (ValueError, KeyError, TypeError) as exc:
        raise BovedaCorrupta(f"El archivo de bóveda no es válido: {exc}") from exc

    llave = _derivar_llave(contrasena, sal, kdf)
    aad = json.dumps(cabecera, sort_keys=True, separators=(",", ":")).encode("utf-8")
    try:
        payload = AESGCM(llave).decrypt(nonce, cifrado, aad)
    except InvalidTag as exc:
        raise ContrasenaIncorrecta("Contraseña maestra incorrecta.") from exc

    try:
        return json.loads(payload.decode("utf-8")), kdf
    except ValueError as exc:  # pragma: no cover - solo si el JSON interno se dana
        raise BovedaCorrupta(f"Contenido descifrado ilegible: {exc}") from exc


def escribir_atomico(ruta, contenido: bytes) -> None:
    """Escribe reemplazando de forma atómica, conservando un respaldo .bak."""
    ruta = str(ruta)
    temporal = ruta + ".tmp"
    with open(temporal, "wb") as fh:
        fh.write(contenido)
        fh.flush()
        os.fsync(fh.fileno())

    if os.path.exists(ruta):
        respaldo = ruta + ".bak"
        try:
            if os.path.exists(respaldo):
                os.remove(respaldo)
            os.replace(ruta, respaldo)
        except OSError:
            pass  # Si el respaldo falla, igual seguimos con el reemplazo.

    os.replace(temporal, ruta)
