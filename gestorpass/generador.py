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


TABLA_LEET: dict[str, list[str]] = {
    "a": ["@", "4"],
    "e": ["3"],
    "i": ["1", "!"],
    "o": ["0"],
    "s": ["$", "5"],
    "t": ["7"],
    "b": ["8"],
}


def generar_desde_palabra(
    palabra: str,
    leet: bool = True,
    capitalizar: bool = True,
    con_sufijo: bool = True,
    longitud_sufijo: int = 4,
) -> str:
    """Transforma una palabra o frase base en una contraseña segura y fácil de recordar.

    Aplica sustituciones leet y mayúsculas probabilísticas mediante CSPRNG (secrets)
    y añade un sufijo numérico/simbólico para garantizar alta entropía.
    """
    palabra_limpia = palabra.strip()
    if not palabra_limpia:
        raise ErrorGenerador("Ingresa al menos una palabra base.")

    resultado = []
    for c in palabra_limpia:
        c_lower = c.lower()
        if leet and c_lower in TABLA_LEET and secrets.randbelow(100) < 55:
            resultado.append(secrets.choice(TABLA_LEET[c_lower]))
        elif capitalizar and c.isalpha():
            resultado.append(c.upper() if secrets.randbelow(100) < 45 else c.lower())
        else:
            resultado.append(c)

    base = "".join(resultado)

    if con_sufijo and longitud_sufijo > 0:
        simbolos_sufijo = "!@#$%^&*-=_"
        mitad = max(1, longitud_sufijo // 2)
        resto = longitud_sufijo - mitad
        suf = [secrets.choice(NUMEROS) for _ in range(mitad)]
        suf += [secrets.choice(simbolos_sufijo) for _ in range(resto)]
        for i in range(len(suf) - 1, 0, -1):
            j = secrets.randbelow(i + 1)
            suf[i], suf[j] = suf[j], suf[i]

        sep = "#" if not any(c in base for c in "!@#$%^&*-_") else ""
        return f"{base}{sep}{''.join(suf)}"

    return base
