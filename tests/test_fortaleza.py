"""Pruebas unitarias para el medidor de fortaleza (gestorpass/fortaleza.py)."""
from gestorpass import fortaleza, i18n


def test_evaluar_contrasena_vacia_espanol():
    i18n.set_idioma("es")
    res = fortaleza.evaluar("")
    assert res["puntaje"] == 0
    assert res["etiqueta"] == "Vacía"
    assert "Sin contraseña" in res["avisos"]


def test_evaluar_contrasena_vacia_ingles():
    i18n.set_idioma("en")
    res = fortaleza.evaluar("")
    assert res["puntaje"] == 0
    assert res["etiqueta"] == "Empty"
    assert "No password" in res["avisos"]
    i18n.set_idioma("es")  # restaurar


def test_evaluar_contrasena_comun_penalizada():
    i18n.set_idioma("es")
    res = fortaleza.evaluar("123456")
    assert res["puntaje"] == 0
    assert res["etiqueta"] == "Muy débil"
    assert any("listas de contraseñas más usadas" in a for a in res["avisos"])


def test_evaluar_contrasena_fuerte():
    i18n.set_idioma("es")
    res = fortaleza.evaluar("Kx9#mP!2$vLq8@zR")
    assert res["puntaje"] >= 3
    assert res["etiqueta"] in ("Fuerte", "Muy fuerte")
    assert res["entropia"] > 70

    i18n.set_idioma("en")
    res_en = fortaleza.evaluar("Kx9#mP!2$vLq8@zR")
    assert res_en["etiqueta"] in ("Strong", "Very Strong")
    i18n.set_idioma("es")


def test_formatear_tiempo_es():
    i18n.set_idioma("es")
    assert fortaleza.formatear_tiempo(0.001) == "instantáneo"
    assert "segundos" in fortaleza.formatear_tiempo(30)
    assert "minutos" in fortaleza.formatear_tiempo(180)
    assert "horas" in fortaleza.formatear_tiempo(7200)
    assert "días" in fortaleza.formatear_tiempo(86400 * 5)
    assert "años" in fortaleza.formatear_tiempo(86400 * 400)
    assert fortaleza.formatear_tiempo(float("inf")) == "prácticamente eterno"


def test_formatear_tiempo_en():
    i18n.set_idioma("en")
    assert fortaleza.formatear_tiempo(0.001) == "instant"
    assert "seconds" in fortaleza.formatear_tiempo(30)
    assert "minutes" in fortaleza.formatear_tiempo(180)
    assert "hours" in fortaleza.formatear_tiempo(7200)
    assert "days" in fortaleza.formatear_tiempo(86400 * 5)
    assert "years" in fortaleza.formatear_tiempo(86400 * 400)
    assert fortaleza.formatear_tiempo(float("inf")) == "practically eternal"
    i18n.set_idioma("es")
