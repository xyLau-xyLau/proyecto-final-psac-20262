import sys

from sbac.repositorio import Repositorio
from sbac.cli import leer_entrada


def test_integracion_init_crea_estructura_completa(tmp_path):
    """
    Verifica que init() cree correctamente toda la estructura
    necesaria para un repositorio SBAC.
    """
    repo = Repositorio(tmp_path)

    resultado = repo.init()

    assert resultado == "Repositorio SBAC inicializado en .sbac/"

    assert (tmp_path / ".sbac").exists()
    assert (tmp_path / ".sbac" / "versions").exists()
    assert (tmp_path / ".sbac" / "baselines").exists()
    assert (tmp_path / ".sbac" / "tracked-files").exists()
    assert (tmp_path / ".sbac" / "config.json").exists()


def test_integracion_add_y_commit_generan_version(tmp_path):
    """
    Verifica que un archivo pueda añadirse al seguimiento
    y registrarse correctamente en una nueva versión.
    """
    archivo = tmp_path / "hola.txt"
    archivo.write_text("hola")

    repo = Repositorio(tmp_path)

    repo.init()
    repo.add("hola.txt")

    mensaje = repo.commit("primer commit")

    assert "Versión v1 registrada" in mensaje


def test_integracion_commit_aparece_en_history(tmp_path):
    """
    Verifica que una versión registrada aparezca correctamente
    en el historial del repositorio.
    """
    archivo = tmp_path / "hola.txt"
    archivo.write_text("hola")

    repo = Repositorio(tmp_path)

    repo.init()
    repo.add("hola.txt")
    repo.commit("primer commit")

    history = repo.history()

    assert "v1" in history
    assert "primer commit" in history


def test_integracion_status_detecta_modificaciones(tmp_path):
    """
    Verifica que status() identifique correctamente archivos
    modificados después del último commit.
    """
    archivo = tmp_path / "test.txt"
    archivo.write_text("v1")

    repo = Repositorio(tmp_path)

    repo.init()
    repo.add("test.txt")
    repo.commit("inicio")

    archivo.write_text("v2")

    status = repo.status()

    assert "Archivos modificados" in status
    assert "test.txt" in status


def test_integracion_baseline_se_lista_correctamente(tmp_path):
    """
    Verifica que una línea base pueda crearse y listarse
    correctamente.
    """
    archivo = tmp_path / "a.txt"
    archivo.write_text("contenido")

    repo = Repositorio(tmp_path)

    repo.init()
    repo.add("a.txt")
    repo.commit("commit inicial")

    repo.baseline("release-1")

    listado = repo.list_baselines()

    assert "release-1 -> v1" in listado


def test_integracion_diff_detecta_cambios(tmp_path):
    """
    Verifica que diff() detecte y muestre diferencias
    entre dos versiones distintas.
    """
    archivo = tmp_path / "main.py"
    archivo.write_text("print('hola')")

    repo = Repositorio(tmp_path)

    repo.init()
    repo.add("main.py")

    repo.commit("v1")

    archivo.write_text("print('chau')")

    repo.commit("v2")

    diff = repo.diff("v1", "v2")

    assert "[main.py]" in diff
    assert "- v1:" in diff
    assert "+ v2:" in diff


def test_integracion_checkout_restaura_archivos(tmp_path):
    """
    Verifica que checkout() restaure correctamente el contenido
    de una versión anterior.
    """
    archivo = tmp_path / "codigo.py"

    archivo.write_text("version1")

    repo = Repositorio(tmp_path)

    repo.init()
    repo.add("codigo.py")

    repo.commit("v1")

    archivo.write_text("version2")

    repo.commit("v2")

    repo.checkout("v1")

    assert archivo.read_text() == "version1"


def test_integracion_add_directorio_rastrea_contenido(tmp_path):
    """
    Verifica que add() sobre un directorio agregue todos
    los archivos contenidos para seguimiento.
    """
    src = tmp_path / "src"
    src.mkdir()

    (src / "a.py").write_text("a")
    (src / "b.py").write_text("b")

    repo = Repositorio(tmp_path)

    repo.init()

    resultado = repo.add("src")

    assert "2 archivo(s)" in resultado

    tracked = repo.manejador.leer_tracked_files()

    assert "src/a.py" in tracked
    assert "src/b.py" in tracked


def test_integracion_history_muestra_versiones_en_orden(tmp_path):
    """
    Verifica que history() muestre todas las versiones
    registradas y sus mensajes asociados.
    """
    archivo = tmp_path / "app.py"
    archivo.write_text("v1")

    repo = Repositorio(tmp_path)

    repo.init()
    repo.add("app.py")

    repo.commit("commit 1")

    archivo.write_text("v2")
    repo.commit("commit 2")

    archivo.write_text("v3")
    repo.commit("commit 3")

    history = repo.history()

    assert "v1" in history
    assert "v2" in history
    assert "v3" in history

    assert "commit 1" in history
    assert "commit 2" in history
    assert "commit 3" in history


def test_integracion_cli_init_crea_repositorio(
    tmp_path,
    monkeypatch,
    capsys
):
    """
    Verifica que el comando init ejecutado desde el CLI
    cree correctamente un repositorio.
    """
    monkeypatch.chdir(tmp_path)

    monkeypatch.setattr(
        sys,
        "argv",
        ["sbac", "init"]
    )

    leer_entrada()

    salida = capsys.readouterr().out

    assert "Repositorio SBAC inicializado" in salida


def test_integracion_cli_commit_crea_version(
    tmp_path,
    monkeypatch,
    capsys
):
    """
    Verifica el flujo completo desde el CLI para inicializar
    un repositorio, añadir un archivo y crear una versión.
    """
    archivo = tmp_path / "archivo.txt"
    archivo.write_text("hola")

    monkeypatch.chdir(tmp_path)

    monkeypatch.setattr(sys, "argv", ["sbac", "init"])
    leer_entrada()

    monkeypatch.setattr(sys, "argv", ["sbac", "add", "archivo.txt"])
    leer_entrada()

    monkeypatch.setattr(
        sys,
        "argv",
        ["sbac", "commit", "primer commit"]
    )
    leer_entrada()

    salida = capsys.readouterr().out

    assert "Versión v1 registrada" in salida


def test_integracion_checkout_actualiza_version_actual(tmp_path):
    """
    Verifica que después de realizar un checkout,
    status() refleje correctamente la versión activa.
    """
    archivo = tmp_path / "archivo.txt"

    archivo.write_text("contenido 1")

    repo = Repositorio(tmp_path)

    repo.init()
    repo.add("archivo.txt")

    repo.commit("v1")

    archivo.write_text("contenido 2")

    repo.commit("v2")

    repo.checkout("v1")

    status = repo.status()

    assert "Versión actual: v1" in status