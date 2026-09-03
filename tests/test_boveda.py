"""Pruebas unitarias para el modelo de bóveda y entradas (gestorpass/boveda.py)."""
import pytest
from gestorpass.boveda import Boveda, ContrasenaIncorrecta, Entrada, ErrorBoveda


def test_crear_y_abrir_boveda(tmp_path):
    archivo = tmp_path / "test_vault.dat"
    password = "clave_maestra_123"

    boveda = Boveda.crear(archivo, password)
    assert archivo.exists()
    assert len(boveda.entradas) == 0

    # No se puede crear si ya existe
    with pytest.raises(ErrorBoveda):
        Boveda.crear(archivo, password)

    # Abrir con clave correcta
    abierta = Boveda.abrir(archivo, password)
    assert len(abierta.entradas) == 0

    # Fallo al abrir con clave incorrecta
    with pytest.raises(ContrasenaIncorrecta):
        Boveda.abrir(archivo, "clave_falsa")


def test_crud_entradas(tmp_path):
    archivo = tmp_path / "test_crud.dat"
    boveda = Boveda.crear(archivo, "pass")

    # 1. Agregar entrada
    e1 = Entrada(sitio="GitHub", usuario="octocat", contrasena="gh_pass", categoria="Trabajo")
    boveda.agregar(e1)
    assert len(boveda.entradas) == 1
    assert e1.id is not None

    # 2. Obtener entrada
    encontrada = boveda.obtener(e1.id)
    assert encontrada is not None
    assert encontrada.sitio == "GitHub"

    # 3. Actualizar y verificar historial
    boveda.actualizar(e1.id, contrasena="gh_pass_nueva")
    actualizada = boveda.obtener(e1.id)
    assert actualizada.contrasena == "gh_pass_nueva"
    assert len(actualizada.historial) == 1
    assert actualizada.historial[0]["contrasena"] == "gh_pass"

    # 4. Duplicar
    duplicada = boveda.duplicar(e1.id)
    assert duplicada is not None
    assert duplicada.id != e1.id
    assert "(copia)" in duplicada.sitio
    assert len(boveda.entradas) == 2

    # 5. Eliminar
    borradas = boveda.eliminar([e1.id])
    assert borradas == 1
    assert len(boveda.entradas) == 1
    assert boveda.obtener(e1.id) is None


def test_filtrar_y_buscar(tmp_path):
    archivo = tmp_path / "test_filter.dat"
    boveda = Boveda.crear(archivo, "pass")

    boveda.agregar(Entrada(sitio="Gmail", usuario="pablo@gmail.com", favorito=True, categoria="Personal"))
    boveda.agregar(Entrada(sitio="Outlook", usuario="pablo@empresa.com", favorito=False, categoria="Trabajo"))
    boveda.agregar(Entrada(sitio="Spotify", usuario="pablo@gmail.com", favorito=False, categoria="Ocio"))

    # Filtrar solo favoritos
    favs = boveda.filtrar(solo_favoritos=True)
    assert len(favs) == 1
    assert favs[0].sitio == "Gmail"

    # Filtrar por texto
    mails = boveda.filtrar(texto="gmail")
    assert len(mails) == 2

    # Filtrar por categoria
    trabajo = boveda.filtrar(categoria="Trabajo")
    assert len(trabajo) == 1
    assert trabajo[0].sitio == "Outlook"


def test_contrasenas_repetidas(tmp_path):
    archivo = tmp_path / "test_repetidas.dat"
    boveda = Boveda.crear(archivo, "pass")

    boveda.agregar(Entrada(sitio="Sitio1", usuario="user1", contrasena="misma_clave"))
    boveda.agregar(Entrada(sitio="Sitio2", usuario="user2", contrasena="misma_clave"))
    boveda.agregar(Entrada(sitio="Sitio3", usuario="user3", contrasena="clave_unica"))

    repetidas = boveda.contrasenas_repetidas()
    assert "misma_clave" in repetidas
    assert len(repetidas["misma_clave"]) == 2
    assert "clave_unica" not in repetidas


def test_importar_texto(tmp_path):
    archivo = tmp_path / "test_import.dat"
    boveda = Boveda.crear(archivo, "pass")

    csv_data = (
        "Google, user1, pass1, https://google.com, Web\n"
        "Twitter, user2, pass2, https://x.com, Redes\n"
    )

    agregadas, omitidas = boveda.importar_texto(csv_data, separador=",")
    assert agregadas == 2
    assert omitidas == 0
    assert len(boveda.entradas) == 2


def test_boveda_con_fixtures(boveda_con_datos: Boveda):
    """Prueba el uso de fixtures compartidos de conftest.py (python-testing-patterns)."""
    assert len(boveda_con_datos.entradas) == 3
    sitios = [e.sitio for e in boveda_con_datos.entradas]
    assert "GitHub" in sitios
    assert "ProtonMail" in sitios
    assert "Servidor Local" in sitios
