from pathlib import Path
from sbac.repositorio import Repositorio
from sbac.manejador_archivos import ManejadorArchivos

NOMBRE_ARCHIVO = "test.txt"
MENSAJE_GENERICO = "Hello, World!"
MENSAJE_MODIFICADO = "Bye, World!"


def test_integracion_init_persiste_estructura(tmp_path: Path) -> None:
    """Init persiste la estructura y un manejador independiente la lee."""
    repo = Repositorio(tmp_path)
    repo.init()

    manejador = ManejadorArchivos(tmp_path)

    assert manejador.existe_repositorio()
    assert (tmp_path / ".sbac/versions").is_dir()
    assert (tmp_path / ".sbac/baselines").is_dir()
    assert (tmp_path / ".sbac/config.json").exists()
    assert manejador.leer_tracked_files() == []
    assert manejador.leer_current_version() == ""


def test_integracion_add_rm_persiste_tracking(tmp_path: Path) -> None:
    """Add y rm persisten el seguimiento en tracked-files."""
    repo = Repositorio(tmp_path)
    repo.init()

    (tmp_path / "a.txt").write_text("A")
    (tmp_path / "b.txt").write_text("B")
    repo.add("a.txt")
    repo.add("b.txt")

    manejador = ManejadorArchivos(tmp_path)
    assert sorted(manejador.leer_tracked_files()) == ["a.txt", "b.txt"]

    contenido = (tmp_path / ".sbac/tracked-files").read_text(encoding="utf-8")
    assert "a.txt" in contenido
    assert "b.txt" in contenido

    repo.rm("a.txt")
    assert ManejadorArchivos(tmp_path).leer_tracked_files() == ["b.txt"]


def test_integracion_commit_persiste_version_y_metadata(tmp_path: Path) -> None:
    """Commit persiste archivos (incl. subdirectorios), metadata y puntero."""
    repo = Repositorio(tmp_path)
    repo.init()

    (tmp_path / "a.txt").write_text("contenido A")
    directorio = tmp_path / "docs"
    directorio.mkdir()
    (directorio / "b.txt").write_text("contenido B")

    repo.add("a.txt")
    repo.add("docs")
    repo.commit("Primer commit")

    manejador = ManejadorArchivos(tmp_path)

    assert "v1" in manejador.listar_versiones()

    metadata = manejador.leer_metadata("v1")
    assert metadata["id"] == "v1"
    assert metadata["parent_id"] == ""
    assert sorted(metadata["archivos"]) == ["a.txt", "docs/b.txt"]

    assert manejador.leer_archivo_de_version("v1", "a.txt") == "contenido A"
    assert manejador.leer_archivo_de_version("v1", "docs/b.txt") == "contenido B"
    assert manejador.leer_current_version() == "v1"

    assert (tmp_path / ".sbac/versions/v1/files/a.txt").exists()
    assert (tmp_path / ".sbac/versions/v1/files/docs/b.txt").exists()


def test_integracion_checkout_restaura_desde_disco(tmp_path: Path) -> None:
    """Checkout restaura el contenido desde disco y actualiza el puntero."""
    repo = Repositorio(tmp_path)
    repo.init()

    archivo_prueba = tmp_path / NOMBRE_ARCHIVO
    archivo_prueba.write_text(MENSAJE_GENERICO)
    repo.add(NOMBRE_ARCHIVO)
    repo.commit("Primer commit")

    archivo_prueba.write_text(MENSAJE_MODIFICADO)
    repo.commit("Segundo commit")
    assert archivo_prueba.read_text(encoding="utf-8") == MENSAJE_MODIFICADO

    mensaje = repo.checkout("v1")

    assert mensaje == "Repositorio restaurado a la versión v1"
    assert archivo_prueba.read_text(encoding="utf-8") == MENSAJE_GENERICO
    assert ManejadorArchivos(tmp_path).leer_current_version() == "v1"


def test_integracion_persistencia_entre_instancias(tmp_path: Path) -> None:
    """Una segunda instancia lee el estado persistido por la primera."""
    repo_uno = Repositorio(tmp_path)
    repo_uno.init()

    archivo_prueba = tmp_path / NOMBRE_ARCHIVO
    archivo_prueba.write_text(MENSAJE_GENERICO)
    repo_uno.add(NOMBRE_ARCHIVO)
    repo_uno.commit("Primer commit")

    repo_dos = Repositorio(tmp_path)

    historial = repo_dos.history()
    assert "v1" in historial
    assert "Primer commit" in historial

    assert repo_dos.status() == repo_dos._formatear_status(
        [NOMBRE_ARCHIVO], [], [], [], "v1")
    assert repo_dos.manejador.leer_tracked_files() == [NOMBRE_ARCHIVO]


def test_integracion_baseline_persiste_y_list_baselines_lee(tmp_path: Path) -> None:
    """Baseline persiste la línea base y list-baselines la lee."""
    repo = Repositorio(tmp_path)
    repo.init()

    archivo_prueba = tmp_path / NOMBRE_ARCHIVO
    archivo_prueba.write_text(MENSAJE_GENERICO)
    repo.add(NOMBRE_ARCHIVO)
    repo.commit("Primer commit")

    repo.baseline("entrega-1")

    ruta_baseline = tmp_path / ".sbac/baselines/entrega-1.txt"
    assert ruta_baseline.exists()
    assert ManejadorArchivos(tmp_path).leer_archivo(ruta_baseline).strip() == "v1"

    repo_dos = Repositorio(tmp_path)
    salida = repo_dos.list_baselines()
    assert "entrega-1 -> v1" in salida


def test_integracion_diff_lee_versiones_de_disco(tmp_path: Path) -> None:
    """Diff lee dos versiones desde disco y reporta sus diferencias."""
    repo = Repositorio(tmp_path)
    repo.init()

    archivo_prueba = tmp_path / NOMBRE_ARCHIVO
    archivo_prueba.write_text("linea1\nlinea2")
    repo.add(NOMBRE_ARCHIVO)
    repo.commit("Primer commit")

    archivo_prueba.write_text("linea1\nMODIFICADA")
    repo.commit("Segundo commit")

    salida = repo.diff("v1", "v2")

    assert "[test.txt] Línea 2" in salida
    assert "- v1: linea2" in salida
    assert "+ v2: MODIFICADA" in salida