"""Pruebas unitarias para el medidor de fortaleza (gestorpass/fortaleza.py)."""
from gestorpass import fortaleza


def test_evaluar_contrasena_vacia():
    res = fortaleza.evaluar("")
    assert res["puntaje"] == 0
    assert res["etiqueta"] == "Vacía"
    assert "Sin contraseña" in res["avisos"]


def test_evaluar_contrasena_comun_penalizada():
    res = fortaleza.evaluar("123456")
    assert res["puntaje"] == 0
    assert res["etiqueta"] == "Muy débil"
    assert any("listas de contraseñas más usadas" in a for a in res["avisos"])


def test_evaluar_contrasena_fuerte():
    # Contraseña larga y variada
    res = fortaleza.evaluar("Kx9#mP!2$vLq8@zR")
    assert res["puntaje"] >= 3
    assert res["etiqueta"] in ("Fuerte", "Muy fuerte")
    assert res["entropia"] > 70


def test_formatear_tiempo():
    assert fortaleza.formatear_tiempo(0.001) == "instantáneo"
    assert "segundos" in fortaleza.formatear_tiempo(30)
    assert "minutos" in fortaleza.formatear_tiempo(180)
    assert "horas" in fortaleza.formatear_tiempo(7200)
    assert "días" in fortaleza.formatear_tiempo(86400 * 5)
    assert "años" in fortaleza.formatear_tiempo(86400 * 400)
    assert fortaleza.formatear_tiempo(float("inf")) == "prácticamente eterno"
