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
    repo.add(NOMBRE_ARCHIVO)
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
    repo.add(NOMBRE_ARCHIVO)
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

