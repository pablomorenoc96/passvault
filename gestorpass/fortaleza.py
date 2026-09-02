"""Evaluacion de la fortaleza de una contraseña y estimacion de tiempo de crackeo."""
from __future__ import annotations

import math
import re

# Ataque offline contra un hash rápido con GPU de gama alta.
# Es el escenario pesimista realista; el número se muestra en la interfaz.
INTENTOS_POR_SEGUNDO = 1e11

NIVELES = [
    # (entropía minima, etiqueta, color)
    (0, "Muy débil", "#e5484d"),
    (36, "Débil", "#f76b15"),
    (60, "Aceptable", "#f5d90a"),
    (80, "Fuerte", "#46a758"),
    (110, "Muy fuerte", "#12a594"),
]

# Lista corta de contraseñas y patrones muy usados (incluye variantes en español).
COMUNES = {
    "123456", "123456789", "12345678", "1234567", "12345", "1234567890",
    "password", "contrasena", "contrasena1", "contraseña", "contraseña1",
    "qwerty", "qwertyuiop", "abc123",
    "111111", "123123", "000000", "iloveyou", "admin", "administrador",
    "welcome", "monkey", "dragon", "letmein", "football", "shadow", "master",
    "sunshine", "princess", "azerty", "trustno1", "hola", "holahola",
    "mexico", "america", "chivas", "cruzazul", "pumas", "barcelona", "madrid",
    "usuario", "invitado", "secreto", "amor", "familia", "teamo", "tequiero",
    "hola123", "password1", "passw0rd", "p@ssw0rd", "qwerty123", "1q2w3e4r",
    "zxcvbnm", "asdfgh", "asdfghjk", "michael", "jordan", "superman", "batman",
}

SECUENCIAS = [
    "abcdefghijklmnopqrstuvwxyz",
    "qwertyuiop", "asdfghjkl", "zxcvbnm",
    "01234567890",
]


def _alfabeto_efectivo(contrasena: str) -> int:
    tamano = 0
    if re.search(r"[a-z]", contrasena):
        tamano += 26
    if re.search(r"[A-Z]", contrasena):
        tamano += 26
    if re.search(r"[0-9]", contrasena):
        tamano += 10
    simbolos = set(re.findall(r"[^a-zA-Z0-9]", contrasena))
    if simbolos:
        # Se cuenta el conjunto habitual de símbolos ASCII imprimibles.
        tamano += 32
    return tamano


def _tiene_secuencia(minuscula: str, largo: int = 4) -> bool:
    for base in SECUENCIAS:
        invertida = base[::-1]
        for i in range(len(base) - largo + 1):
            if base[i:i + largo] in minuscula or invertida[i:i + largo] in minuscula:
                return True
    return False


def _repeticiones(contrasena: str) -> bool:
    if re.search(r"(.)\1{2,}", contrasena):       # aaa, 111
        return True
    if re.search(r"(.{2,4})\1{1,}", contrasena):  # abab, xyzxyz
        return True
    return False


from . import i18n

CLAVES_NIVELES = [
    (0, "strength_very_weak", "#e5484d"),
    (36, "strength_weak", "#f76b15"),
    (60, "strength_fair", "#f5d90a"),
    (80, "strength_strong", "#46a758"),
    (110, "strength_very_strong", "#12a594"),
]


def nivel_por_entropia(entropia: float) -> tuple[str, str, int]:
    """Devuelve (etiqueta, color, puntaje 0-4) para una entropía conocida."""
    clave, color, puntaje = CLAVES_NIVELES[0][1], CLAVES_NIVELES[0][2], 0
    for indice, (minimo, c_nombre, tono) in enumerate(CLAVES_NIVELES):
        if entropia >= minimo:
            clave, color, puntaje = c_nombre, tono, indice
    return i18n.t(clave), color, puntaje


def _segundos_para_romper(entropia: float) -> float:
    """Segundos promedio para adivinarla por fuerza bruta (mitad del espacio)."""
    if entropia <= 0:
        return 0.0
    # Se trabaja en logaritmos para no desbordar el float con entropías altas.
    exponente = entropia - 1 - math.log2(INTENTOS_POR_SEGUNDO)
    if exponente > 1000:
        return float("inf")
    return 2 ** exponente


def evaluar(contrasena: str) -> dict:
    """Devuelve entropía estimada, etiqueta, color, puntaje 0-4 y avisos."""
    contrasena = contrasena or ""
    largo = len(contrasena)
    avisos: list[str] = []

    if largo == 0:
        return {"entropia": 0.0, "etiqueta": i18n.t("strength_empty"), "color": "#7d7d7d",
                "puntaje": 0, "avisos": [i18n.t("warn_empty")], "segundos": 0.0}

    alfabeto = _alfabeto_efectivo(contrasena)
    entropia = largo * math.log2(alfabeto) if alfabeto > 1 else 0.0

    minuscula = contrasena.lower()
    base_comun = re.sub(r"[^a-z]", "", minuscula)

    # Penalizaciones: la entropía bruta sobreestima las contraseñas humanas.
    if minuscula in COMUNES or base_comun in COMUNES:
        entropia = min(entropia, 12.0)
        avisos.append("Aparece en las listas de contraseñas más usadas")
    if _tiene_secuencia(minuscula):
        entropia *= 0.55
        avisos.append("Contiene una secuencia predecible (abcd, qwerty, 1234...)")
    if _repeticiones(contrasena):
        entropia *= 0.65
        avisos.append("Contiene caracteres o patrones repetidos")
    if re.fullmatch(r"\d+", contrasena):
        entropia *= 0.7
        avisos.append("Solo números")
    elif re.fullmatch(r"[a-z]+", contrasena):
        entropia *= 0.75
        avisos.append("Solo letras minúsculas")
    if re.search(r"(19|20)\d{2}", contrasena):
        entropia *= 0.85
        avisos.append("Contiene algo que parece un año")

    if largo < 8:
        entropia *= 0.6
        avisos.append("Demasiado corta (menos de 8 caracteres)")
    elif largo < 12:
        avisos.append("Menos de 12 caracteres: se recomienda alargarla")

    clave, color, puntaje = CLAVES_NIVELES[0][1], CLAVES_NIVELES[0][2], 0
    for indice, (minimo, c_nombre, tono) in enumerate(CLAVES_NIVELES):
        if entropia >= minimo:
            clave, color, puntaje = c_nombre, tono, indice

    segundos = _segundos_para_romper(entropia)

    return {"entropia": entropia, "etiqueta": i18n.t(clave), "color": color,
            "puntaje": puntaje, "avisos": avisos, "segundos": segundos}


def formatear_tiempo(segundos: float) -> str:
    """Convierte segundos en un texto legible ('3 días' o '3 days')."""
    if segundos == float("inf"):
        return i18n.t("time_eternal")
    if segundos < 1:
        return i18n.t("time_instant")
    unidades = [
        (60, "time_minutes"), (60, "time_hours"), (24, "time_days"), (365.25, "time_years"),
    ]
    valor = segundos
    clave = "time_seconds"
    for factor, siguiente in unidades:
        if valor < factor:
            break
        valor /= factor
        clave = siguiente
    else:
        clave = "time_years"

    if clave == "time_years":
        if valor >= 1e15:
            return i18n.t("time_eternal")
        if valor >= 1e12:
            return f"{_miles(valor / 1e12)} {i18n.t('time_trillion_years')}"
        if valor >= 1e9:
            return f"{_miles(valor / 1e9)} {i18n.t('time_billion_years')}"
        if valor >= 1e6:
            return f"{_miles(valor / 1e6)} {i18n.t('time_million_years')}"
        if valor >= 1e3:
            return f"{_miles(valor / 1e3)} {i18n.t('time_thousand_years')}"
    return f"{_miles(valor)} {i18n.t(clave)}"


def _miles(valor: float) -> str:
    """Entero con punto como separador de miles, al estilo del español."""
    return f"{valor:,.0f}".replace(",", ".")
