"""Generador de contraseñas aleatorias criptográficamente seguras.

Usa ``secrets`` (CSPRNG del sistema operativo), nunca ``random``.
"""
from __future__ import annotations

import math
import secrets

MAYUSCULAS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
MINUSCULAS = "abcdefghijklmnopqrstuvwxyz"
NUMEROS = "0123456789"
SIMBOLOS = "!@#$%^&*()-_=+[]{};:,.?/"

# Caracteres que se confunden entre si al leerlos o dictarlos.
AMBIGUOS = "Il1|O0o`'\";:,.5S2Z8B"

LONGITUD_MINIMA = 4
LONGITUD_MAXIMA = 64


class ErrorGenerador(ValueError):
    """No se puede generar con las opciones dadas."""


def _conjuntos(mayusculas: bool, minusculas: bool, numeros: bool,
               simbolos: bool, sin_ambiguos: bool) -> list[str]:
    crudos = []
    if mayusculas:
        crudos.append(MAYUSCULAS)
    if minusculas:
        crudos.append(MINUSCULAS)
    if numeros:
        crudos.append(NUMEROS)
    if simbolos:
        crudos.append(SIMBOLOS)

    if sin_ambiguos:
        crudos = ["".join(c for c in grupo if c not in AMBIGUOS) for grupo in crudos]

    return [grupo for grupo in crudos if grupo]


def generar(longitud: int = 20, mayusculas: bool = True, minusculas: bool = True,
            numeros: bool = True, simbolos: bool = True,
            sin_ambiguos: bool = False) -> str:
    """Genera una contraseña con al menos un caracter de cada tipo elegido."""
    grupos = _conjuntos(mayusculas, minusculas, numeros, simbolos, sin_ambiguos)

    if not grupos:
        raise ErrorGenerador("Selecciona al menos un tipo de caracter.")
    if int(longitud) < len(grupos):
        raise ErrorGenerador(
            f"La longitud debe ser de al menos {len(grupos)} para incluir todos "
            "los tipos seleccionados."
        )
    longitud = max(LONGITUD_MINIMA, min(LONGITUD_MAXIMA, int(longitud)))

    total = "".join(grupos)
    # Un caracter obligatorio de cada grupo y el resto libre.
    caracteres = [secrets.choice(grupo) for grupo in grupos]
    caracteres += [secrets.choice(total) for _ in range(longitud - len(grupos))]

    # Barajado Fisher-Yates con el CSPRNG para no filtrar el orden de los grupos.
    for i in range(len(caracteres) - 1, 0, -1):
        j = secrets.randbelow(i + 1)
        caracteres[i], caracteres[j] = caracteres[j], caracteres[i]

    return "".join(caracteres)


def tamano_alfabeto(mayusculas: bool, minusculas: bool, numeros: bool,
                    simbolos: bool, sin_ambiguos: bool) -> int:
    return sum(len(g) for g in _conjuntos(mayusculas, minusculas, numeros,
                                          simbolos, sin_ambiguos))


def entropia_generada(longitud: int, alfabeto: int) -> float:
    """Bits de entropía reales de una contraseña aleatoria de este generador."""
    if alfabeto <= 1 or longitud <= 0:
        return 0.0
    return longitud * math.log2(alfabeto)


def generar_pin(digitos: int = 6) -> str:
    digitos = max(3, min(16, int(digitos)))
    return "".join(secrets.choice(NUMEROS) for _ in range(digitos))
