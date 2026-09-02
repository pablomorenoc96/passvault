"""Pruebas unitarias para el generador de contraseñas (gestorpass/generador.py)."""
import pytest
from gestorpass import generador
from gestorpass.generador import (
    AMBIGUOS,
    MAYUSCULAS,
    MINUSCULAS,
    NUMEROS,
    SIMBOLOS,
    ErrorGenerador,
)


def test_generar_longitud_correcta():
    for longitud in (8, 16, 32, 64):
        pwd = generador.generar(longitud=longitud)
        assert len(pwd) == longitud


def test_generar_todos_los_tipos():
    pwd = generador.generar(longitud=24, mayusculas=True, minusculas=True, numeros=True, simbolos=True)
    assert any(c in MAYUSCULAS for c in pwd)
    assert any(c in MINUSCULAS for c in pwd)
    assert any(c in NUMEROS for c in pwd)
    assert any(c in SIMBOLOS for c in pwd)


def test_generar_sin_ambiguos():
    for _ in range(10):
        pwd = generador.generar(longitud=40, sin_ambiguos=True)
        for char in AMBIGUOS:
            assert char not in pwd


def test_generar_sin_conjuntos_lanza_error():
    with pytest.raises(ErrorGenerador):
        generador.generar(mayusculas=False, minusculas=False, numeros=False, simbolos=False)


def test_generar_longitud_menor_que_grupos():
    with pytest.raises(ErrorGenerador):
        # 4 grupos activados pero longitud 2
        generador.generar(longitud=2, mayusculas=True, minusculas=True, numeros=True, simbolos=True)


def test_generar_pin():
    pin = generador.generar_pin(digitos=6)
    assert len(pin) == 6
    assert pin.isdigit()

    pin_largo = generador.generar_pin(digitos=12)
    assert len(pin_largo) == 12
    assert pin_largo.isdigit()


def test_tamano_alfabeto_y_entropia():
    alfabeto = generador.tamano_alfabeto(
        mayusculas=True, minusculas=True, numeros=True, simbolos=True, sin_ambiguos=False
    )
    assert alfabeto == len(MAYUSCULAS) + len(MINUSCULAS) + len(NUMEROS) + len(SIMBOLOS)

    entropia = generador.entropia_generada(longitud=20, alfabeto=alfabeto)
    assert entropia > 100.0  # 20 caracteres sobre un alfabeto de ~94 símbolos da >130 bits


def test_generar_desde_palabra():
    palabra = "guitarra"
    # Con sufijo y leet
    pwd = generador.generar_desde_palabra(palabra, leet=True, capitalizar=True, con_sufijo=True)
    assert len(pwd) > len(palabra)
    assert any(c in NUMEROS for c in pwd)

    # Sin sufijo ni leet ni capitalizar
    pwd_simple = generador.generar_desde_palabra(palabra, leet=False, capitalizar=False, con_sufijo=False)
    assert pwd_simple == palabra


def test_generar_desde_palabra_vacia():
    with pytest.raises(ErrorGenerador):
        generador.generar_desde_palabra("   ")
