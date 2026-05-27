import pytest
from pathlib import Path
import json
import os
from sbac.repositorio import Repositorio
from sbac.errores import (RepositorioYaExisteError, RepositorioCreacionError,
                    RepositorioNoInicializadoError, ArchivoNoEncontradoError,
                    ArchivoYaRastreadoError, MensajeVacioError,
                    SinArchivosRastreadosError, SinCambiosError,
                    ArchivoRastreadoFaltanteError, ArchivoNoRastreadoError)

NOMBRE_ARCHIVO = "test.txt"
MENSAJE_GENERICO = "Hello, World!"

def test_status_sin_repo_activo(tmp_path: Path) -> None:
    """ 
    Prueba para ver que se levante la excepción
    cuando no se ha inicializado el repositorio
    """
    repo = Repositorio(tmp_path)
    with pytest.raises(RepositorioNoInicializadoError):
        repo.status()

def test_status_repo_vacio(tmp_path: Path) -> None:
    """
    Prueba para ver que se refleje el status correcto
    con un repositorio recién inicializado
    """
    repo = Repositorio(tmp_path)
    repo.init()
    print(repo.status())
    assert repo.status() == repo._formatear_status(
        [], [], [], [], None)

def test_status_repo_modificados(tmp_path: Path) -> None:
    """
    Prueba para ver que se reflejen cambios dentro de un directorio
    1. Se crea un archivo y se refleja en modificados
    2. Se borra el archivo y se actualiza el status
    """
    
    repo = Repositorio(tmp_path)
    repo.init()
    archivo_prueba = tmp_path / NOMBRE_ARCHIVO
    archivo_prueba.write_text(MENSAJE_GENERICO)
    assert repo.status() == repo._formatear_status(
        [], [], [], [NOMBRE_ARCHIVO], None)
    archivo_prueba.unlink()
    assert repo.status() == repo._formatear_status(
        [], [], [], [], None)

def test_status_repo_seguimiento(tmp_path: Path) -> None:
    """ 
    Prueba para verificar que se actualice el status
    si se agregan archivos al seguimiento y si se borran
    usando el comando remove
    """
    repo = Repositorio(tmp_path)
    repo.init()
    archivo_prueba = tmp_path / NOMBRE_ARCHIVO
    archivo_prueba.write_text(MENSAJE_GENERICO)
    repo.add(NOMBRE_ARCHIVO)
    assert repo.status() == repo._formatear_status(
        [NOMBRE_ARCHIVO], [], [], [], None)
    repo.rm(NOMBRE_ARCHIVO)
    assert repo.status() == repo._formatear_status(
        [], [], [], [NOMBRE_ARCHIVO], None)
    
def test_status_commit(tmp_path: Path) -> None:
    """
    Prueba para verificar cambios en el status
    entre commits
    """
    repo = Repositorio(tmp_path)
    repo.init()
    archivo_prueba = tmp_path / NOMBRE_ARCHIVO
    archivo_prueba.write_text(MENSAJE_GENERICO)
    repo.add(NOMBRE_ARCHIVO)
    repo.commit("test")
    assert repo.status() == repo._formatear_status(
        [NOMBRE_ARCHIVO], [], [], [], "v1")
    archivo_prueba.write_text("Bye, World!")
    assert repo.status() == repo._formatear_status(
        [], [NOMBRE_ARCHIVO], [], [], "v1")
    repo.commit("test_2")
    assert repo.status() == repo._formatear_status(
        [NOMBRE_ARCHIVO], [], [], [], "v2")
    
def test_commit_sin_init(tmp_path: Path) -> None:
    """ 
    Prueba para verificar que se levante excepción al intentar
    hacer commit cuando no se ha inicializado el repositorio
    """
    repo = Repositorio(tmp_path)
    with pytest.raises(RepositorioNoInicializadoError):
        repo.commit("Prueba")

def test_commit_sin_msj(tmp_path: Path) -> None:
    """
    Prueba para verificar que se levante excepción al intentar
    hacer commit sin mensaje"""
    repo = Repositorio(tmp_path)
    repo.init()
    with pytest.raises(MensajeVacioError):
        repo.commit("")

def test_commit_sin_archivos_en_seguimiento(tmp_path: Path) -> None:
    """
    Prueba para verficiar que se levante excepción al intentar
    hacer commit sin archivos en el seguimiento"""
    repo = Repositorio(tmp_path)
    repo.init()
    with pytest.raises(SinArchivosRastreadosError):
        repo.commit("prueba")

def test_commit_integridad_archivos_seguimiento(tmp_path: Path) -> None:
    """
    Prueba para verificar que los archivos en rastreo existan previo al commit
    """
    repo = Repositorio(tmp_path)
    repo.init()
    archivo_prueba = tmp_path / NOMBRE_ARCHIVO
    archivo_prueba.write_text(MENSAJE_GENERICO)
    repo.add(NOMBRE_ARCHIVO)
    archivo_prueba.unlink()
    with pytest.raises(ArchivoRastreadoFaltanteError):
        repo.commit("test")

def test_commit_sin_cambios(tmp_path: Path) -> None:
    """
    Prueba para verificar que se levante excepción al intentar
    versionar sin cambios desde la última versión
    """
    repo = Repositorio(tmp_path)
    repo.init()
    archivo_prueba = tmp_path / NOMBRE_ARCHIVO
    archivo_prueba.write_text(MENSAJE_GENERICO)
    repo.add(NOMBRE_ARCHIVO)
    repo.commit("test")
    with pytest.raises(SinCambiosError):
        repo.commit("test_2")

def test_commit_metadatos_correctos(tmp_path: Path) -> None:
    """
    Prueba para verificar que se registren metadatos correctamente
    """
    usuario = os.getenv('USER')
    repo = Repositorio(tmp_path)
    repo.init()
    json_data= open(tmp_path / '.sbac/config.json', 'r', encoding='utf-8')
    data_dict = json.load(json_data)
    json_data.close()
    archivo_prueba = tmp_path / NOMBRE_ARCHIVO
    archivo_prueba.write_text(MENSAJE_GENERICO)
    assert usuario == data_dict['autor']
    repo.add(NOMBRE_ARCHIVO)
    commit_msj = "test"
    repo.commit(commit_msj)
    json_data = open(
        tmp_path / '.sbac/versions/v1/metadata.json', 
        'r', encoding='utf-8')
    assert json_data
    data_dict = json.load(json_data)
    assert data_dict['id'] == 'v1'
    assert data_dict['parent_id'] == ''
    assert data_dict['archivos'] == ['test.txt']
    assert data_dict['autor'] == usuario
    json_data.close()
    with pytest.raises(SinCambiosError):
        repo.commit("test_2")
    archivo_prueba.write_text("Bye, World!")
    commit_msj = "test_2"
    repo.commit(commit_msj)
    json_data = open(
        tmp_path / '.sbac/versions/v2/metadata.json', 
        'r', encoding='utf-8')
    assert json_data
    data_dict = json.load(json_data)
    assert data_dict['id'] == 'v2'
    assert data_dict['parent_id'] == 'v1'
    assert data_dict['archivos'] == ['test.txt']
    assert data_dict['autor'] == usuario
    json_data.close()

def test_add_sin_init(tmp_path: Path) -> None:
    """
    Prueba para verificar que se levante excepción
    si se intenta agregar un archivo sin inicializar
    el repositorio
    """
    repo = Repositorio(tmp_path)

    with pytest.raises(RepositorioNoInicializadoError):
        repo.add(NOMBRE_ARCHIVO)


def test_add_archivo_inexistente(tmp_path: Path) -> None:
    """
    Prueba para verificar que se levante excepción
    cuando el archivo no existe
    """
    repo = Repositorio(tmp_path)
    repo.init()

    with pytest.raises(ArchivoNoEncontradoError):
        repo.add(NOMBRE_ARCHIVO)


def test_add_archivo_correctamente(tmp_path: Path) -> None:
    """
    Prueba para verificar que un archivo
    se agregue correctamente al seguimiento
    """
    repo = Repositorio(tmp_path)
    repo.init()

    archivo_prueba = tmp_path / NOMBRE_ARCHIVO
    archivo_prueba.write_text(MENSAJE_GENERICO)

    repo.add(NOMBRE_ARCHIVO)

    assert repo.status() == repo._formatear_status(
        [NOMBRE_ARCHIVO], [], [], [], None
    )


def test_add_archivo_ya_rastreado(tmp_path: Path) -> None:
    """
    Prueba para verificar que se levante excepción
    al intentar agregar un archivo ya rastreado
    """
    repo = Repositorio(tmp_path)
    repo.init()

    archivo_prueba = tmp_path / NOMBRE_ARCHIVO
    archivo_prueba.write_text(MENSAJE_GENERICO)

    repo.add(NOMBRE_ARCHIVO)

    with pytest.raises(ArchivoYaRastreadoError):
        repo.add(NOMBRE_ARCHIVO)


def test_add_archivo_luego_de_rm(tmp_path: Path) -> None:
    """
    Prueba para verificar que un archivo eliminado
    del seguimiento pueda agregarse nuevamente
    """
    repo = Repositorio(tmp_path)
    repo.init()

    archivo_prueba = tmp_path / NOMBRE_ARCHIVO
    archivo_prueba.write_text(MENSAJE_GENERICO)

    repo.add(NOMBRE_ARCHIVO)
    repo.rm(NOMBRE_ARCHIVO)

    repo.add(NOMBRE_ARCHIVO)

    assert repo.status() == repo._formatear_status(
        [NOMBRE_ARCHIVO], [], [], [], None
    )
    
def test_add_directorio_vacio(tmp_path: Path) -> None:
    """
    Prueba para verificar que se retorne un mensaje
    cuando se intenta agregar un directorio vacío
    """
    repo = Repositorio(tmp_path)
    repo.init()

    (tmp_path / "vacio").mkdir()

    mensaje = repo.add("vacio")

    assert mensaje == 'El directorio "vacio" no contiene archivos'
    
def test_add_directorio_con_slash_final(tmp_path: Path) -> None:
    """
    Prueba para verificar que se pueda agregar
    un directorio usando slash final
    """
    repo = Repositorio(tmp_path)
    repo.init()

    directorio = tmp_path / "src"
    directorio.mkdir()

    archivo = directorio / "main.py"
    archivo.write_text("print('hola')")

    repo.add("src/")

    assert repo.status() == repo._formatear_status(
        ["src/main.py"], [], [], [], None
    )
    
    
def test_add_punto_agrega_todos_los_archivos(tmp_path: Path) -> None:
    """
    Prueba para verificar que add(".")
    agregue todos los archivos del workspace
    """
    repo = Repositorio(tmp_path)
    repo.init()

    (tmp_path / "a.txt").write_text("a")
    (tmp_path / "b.txt").write_text("b")

    repo.add(".")

    rastreados = sorted(repo.manejador.leer_tracked_files())

    assert rastreados == ["a.txt", "b.txt"]
    
def test_add_directorio_agrega_archivos_recursivamente(tmp_path: Path) -> None:
    """
    Prueba para verificar que add()
    agregue recursivamente los archivos
    de un directorio
    """
    repo = Repositorio(tmp_path)
    repo.init()

    directorio = tmp_path / "docs"
    directorio.mkdir()

    (directorio / "a.txt").write_text("hola")
    (directorio / "b.txt").write_text("mundo")

    repo.add("docs")

    rastreados = sorted(repo.manejador.leer_tracked_files())

    assert rastreados == [
        "docs/a.txt",
        "docs/b.txt",
    ]
    
def test_add_multiple_sin_nuevos_archivos(tmp_path: Path) -> None:
    """
    Verifica que _add_multiple no agregue archivos cuando todos
    los candidatos ya están previamente rastreados.
    """
    repo = Repositorio(tmp_path)
    repo.init()

    archivo = tmp_path / "a.txt"
    archivo.write_text("contenido")

    repo.manejador.escribir_tracked_files(["a.txt"])

    resultado = repo._add_multiple(["a.txt"])

    assert resultado == "No hay archivos nuevos para añadir al seguimiento"
    assert repo.manejador.leer_tracked_files() == ["a.txt"]
    
def test_add_multiple_mezcla_parcial(tmp_path: Path) -> None:
    """
    Verifica que _add_multiple agregue únicamente los archivos
    no rastreados, ignorando los ya existentes.
    """
    repo = Repositorio(tmp_path)
    repo.init()

    (tmp_path / "a.txt").write_text("A")
    (tmp_path / "b.txt").write_text("B")

    repo.manejador.escribir_tracked_files(["a.txt"])

    resultado = repo._add_multiple(["a.txt", "b.txt"])

    tracked = repo.manejador.leer_tracked_files()
    assert sorted(tracked) == ["a.txt", "b.txt"]

    assert "1 archivo(s) añadido(s) al seguimiento:" in resultado
    assert "b.txt" in resultado

def test_add_todos_workspace_vacio(tmp_path: Path) -> None:
    """
    Verifica el comportamiento de _add_todos cuando el workspace
    no contiene archivos.
    """
    repo = Repositorio(tmp_path)
    repo.init()

    resultado = repo._add_todos()

    assert resultado == "No hay archivos nuevos para añadir al seguimiento"
    assert repo.manejador.leer_tracked_files() == []

def test_add_todos_todo_ya_rastreado(tmp_path: Path) -> None:
    """
    Verifica que _add_todos no vuelva a agregar archivos que
    ya están completamente rastreados en el workspace.
    """
    repo = Repositorio(tmp_path)
    repo.init()

    (tmp_path / "a.txt").write_text("A")
    (tmp_path / "b.txt").write_text("B")

    repo.manejador.escribir_tracked_files(["a.txt", "b.txt"])

    resultado = repo._add_todos()

    assert resultado == "No hay archivos nuevos para añadir al seguimiento"
    assert sorted(repo.manejador.leer_tracked_files()) == ["a.txt", "b.txt"]