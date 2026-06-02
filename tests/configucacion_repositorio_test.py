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

def test_init_configuracion_default(tmp_path: Path) -> None:
    """
    Verifica que init() genere el archivo config.json con la configuración correcta.
    """
    repo = Repositorio(tmp_path)

    repo.init()

    config_path = tmp_path / ".sbac" / "config.json"

    assert config_path.exists()

    with open(config_path, encoding="utf-8") as archivo:
        config = json.load(archivo)

    assert "autor" in config
    assert "algoritmo_hash" in config

def test_autor_config(tmp_path: Path) -> None:
    """
    Verifica que commit  almacene el autor de config.json en metadata.json.
    """
    repo = Repositorio(tmp_path)
    repo.init()

    config_path = tmp_path / ".sbac" / "config.json"

    with open(config_path, encoding="utf-8") as archivo:
        config = json.load(archivo)

    autor = config["autor"]

    archivo_prueba = tmp_path / NOMBRE_ARCHIVO 
    archivo_prueba.write_text(MENSAJE_GENERICO)

    repo.add("test.txt")
    repo.commit("commit de test")

    metadata_path = (
        tmp_path /
        ".sbac" /
        "versions" /
        "v1" /
        "metadata.json"
    )

    with open(metadata_path, encoding="utf-8") as archivo:
        metadata = json.load(archivo)

    assert metadata["autor"] == autor

def test_cambios_config(tmp_path: Path) -> None:
    """
    Verifica que un cambio manual en config.json se refleje en nuevos commits.
    """
    repo = Repositorio(tmp_path)
    repo.init()

    config_path = tmp_path / ".sbac" / "config.json"

    with open(config_path, encoding="utf-8") as archivo:
        config = json.load(archivo)

    config["autor"] = "UsuarioPrueba"

    with open(config_path, "w", encoding="utf-8") as archivo:
        json.dump(config, archivo)

    archivo_prueba = tmp_path / NOMBRE_ARCHIVO 
    archivo_prueba.write_text(MENSAJE_GENERICO)

    repo.add("test.txt")
    repo.commit("commit test")

    metadata_path = (
        tmp_path /
        ".sbac" /
        "versions" /
        "v1" /
        "metadata.json"
    )

    with open(metadata_path, encoding="utf-8") as archivo:
        metadata = json.load(archivo)

    assert metadata["autor"] == "UsuarioPrueba"


def test_commit_metadata(
    tmp_path: Path
) -> None:
    """
    Verifica que config.json y metadata.json sean consistentes internamente.
    """
    repo = Repositorio(tmp_path)
    repo.init()

    archivo_prueba = tmp_path / NOMBRE_ARCHIVO 
    archivo_prueba.write_text(MENSAJE_GENERICO)

    repo.add("archivo.txt")
    repo.commit("commit")

    with open(
        tmp_path / ".sbac" / "config.json",
        encoding="utf-8"
    ) as archivo_config:
        config = json.load(archivo_config)

    with open(
        tmp_path /
        ".sbac" /
        "versions" /
        "v1" /
        "metadata.json",
        encoding="utf-8"
    ) as archivo_meta:
        metadata = json.load(archivo_meta)

    assert metadata["autor"] == config["autor"]
