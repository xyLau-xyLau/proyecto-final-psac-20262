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

def test_init_repositorio_correctamente(tmp_path: Path) -> None:
    """
    Prueba para verificar que se inicialice correctamente
    la estructura del repositorio SBAC
    """
    repo = Repositorio(tmp_path)

    mensaje = repo.init()

    assert mensaje == 'Repositorio SBAC inicializado en .sbac/'

    assert (tmp_path / ".sbac").exists()
    assert (tmp_path / ".sbac/versions").exists()
    assert (tmp_path / ".sbac/baselines").exists()
    assert (tmp_path / ".sbac/config.json").exists()
    assert (tmp_path / ".sbac/tracked-files").exists()


def test_init_repo_ya_existente(tmp_path: Path) -> None:
    """
    Prueba para verificar que se levante excepción
    si el repositorio ya fue inicializado
    """
    repo = Repositorio(tmp_path)

    repo.init()

    with pytest.raises(RepositorioYaExisteError):
        repo.init()


def test_init_creacion_error(tmp_path: Path, monkeypatch) -> None:
    """
    Prueba para verificar que se levante excepción
    cuando ocurre un error creando la estructura
    """

    repo = Repositorio(tmp_path)

    def mock_crear_estructura() -> None:
        raise OSError("Error de creación")

    monkeypatch.setattr(
        repo.manejador,
        "crear_estructura",
        mock_crear_estructura
    )

    with pytest.raises(RepositorioCreacionError):
        repo.init()

def test_rm_sin_init(tmp_path: Path) -> None:
    """
    Prueba para verificar que se levante excepción
    si se intenta usar rm sin inicializar el repositorio
    """
    repo = Repositorio(tmp_path)

    with pytest.raises(RepositorioNoInicializadoError):
        repo.rm(NOMBRE_ARCHIVO)


def test_rm_archivo_no_rastreado(tmp_path: Path) -> None:
    """
    Prueba para verificar que se levante excepción
    cuando el archivo no está bajo seguimiento
    """
    repo = Repositorio(tmp_path)
    repo.init()

    archivo = tmp_path / NOMBRE_ARCHIVO
    archivo.write_text(MENSAJE_GENERICO)

    with pytest.raises(ArchivoNoRastreadoError):
        repo.rm(NOMBRE_ARCHIVO)


def test_rm_archivo_correctamente(tmp_path: Path) -> None:
    """
    Prueba para verificar que un archivo
    se elimine correctamente del seguimiento
    """
    repo = Repositorio(tmp_path)
    repo.init()

    archivo = tmp_path / NOMBRE_ARCHIVO
    archivo.write_text(MENSAJE_GENERICO)

    repo.add(NOMBRE_ARCHIVO)

    assert repo.status() == repo._formatear_status(
        [NOMBRE_ARCHIVO], [], [], [], None
    )

    repo.rm(NOMBRE_ARCHIVO)

    assert repo.status() == repo._formatear_status(
        [], [], [], [NOMBRE_ARCHIVO], None
    )


def test_rm_no_elimina_archivo_fisico(tmp_path: Path) -> None:
    """
    Prueba para verificar que rm no elimine
    el archivo del sistema de archivos
    """
    repo = Repositorio(tmp_path)
    repo.init()

    archivo = tmp_path / NOMBRE_ARCHIVO
    archivo.write_text(MENSAJE_GENERICO)

    repo.add(NOMBRE_ARCHIVO)
    repo.rm(NOMBRE_ARCHIVO)

    # El archivo sigue existiendo en el workspace
    assert archivo.exists()


def test_rm_y_readd_funciona(tmp_path: Path) -> None:
    """
    Prueba para verificar que un archivo eliminado
    del seguimiento pueda volver a agregarse
    """
    repo = Repositorio(tmp_path)
    repo.init()

    archivo = tmp_path / NOMBRE_ARCHIVO
    archivo.write_text(MENSAJE_GENERICO)

    repo.add(NOMBRE_ARCHIVO)
    repo.rm(NOMBRE_ARCHIVO)

    repo.add(NOMBRE_ARCHIVO)

    assert repo.status() == repo._formatear_status(
        [NOMBRE_ARCHIVO], [], [], [], None
    )


def test_rm_actualiza_tracked_files(tmp_path: Path) -> None:
    """
    Prueba para verificar que rm actualiza correctamente
    el archivo de tracking interno
    """
    repo = Repositorio(tmp_path)
    repo.init()

    archivo1 = tmp_path / "a.txt"
    archivo2 = tmp_path / "b.txt"
    archivo1.write_text("a")
    archivo2.write_text("b")

    repo.add("a.txt")
    repo.add("b.txt")

    repo.rm("a.txt")

    rastreados = repo.manejador.leer_tracked_files()

    assert rastreados == ["b.txt"]

#----- History tests

def test_history_sin_init(tmp_path: Path) -> None:
    """
    Prueba para verificar que se arroje la excepción:
    RepositorioNoInicializadoError
    cuando el repositorio no ha sido inicializado
    """
    repo = Repositorio(tmp_path)
    with pytest.raises(RepositorioNoInicializadoError):
        repo.history()

def test_history_sin_versiones(tmp_path: Path) -> None:
    """
    Prueba para verificar que history regrese el mensaje:
    'No hay versiones.'
    en caso de que no haya versiones registradas
    """
    repo = Repositorio(tmp_path)
    repo.init()
    mensaje = repo.history()
    assert mensaje == 'No hay versiones.'

def test_history(tmp_path: Path) -> None:
    """
    Prueba para verificar que el mensaje es correcto al
    crear múltiples versiones
    """
    repo = Repositorio(tmp_path)
    repo.init()
    archivo1 = tmp_path / "a.txt"
    archivo2 = tmp_path / "b.txt"
    archivo3 = tmp_path / "c.txt"
    archivo1.write_text("a")
    archivo2.write_text("b")
    archivo3.write_text("c")
    repo.add("a.txt")
    repo.commit("Primer commit")
    repo.add("b.txt")
    repo.commit("Segundo commit")
    repo.add("c.txt")
    repo.commit("Tercer commit")    
    mensaje = repo.history()
    cadenas = mensaje.split("\n")
    assert cadenas[1].startswith("v1")
    assert cadenas[1].endswith("Primer commit")
    assert cadenas[2].startswith("v2")
    assert cadenas[2].endswith("Segundo commit")
    assert cadenas[3].startswith("v3")
    assert cadenas[3].endswith("Tercer commit")

#----- Baseline tests
def test_baseline_error_repositorio_no_inicializado(tmp_path: Path) -> None:
    """Validar que falle si el repositorio no está inicializado."""
    repo = Repositorio(tmp_path)
    with pytest.raises(RepositorioNoInicializadoError):
        repo.baseline("Version_Invalida")

def test_baseline_error_nombre_vacio(tmp_path: Path) -> None:
    """Validar que falle si el nombre enviado es vacío o espacios."""
    repo = Repositorio(tmp_path)
    repo.init()
    with pytest.raises(ValueError, match="El nombre de la línea base no puede estar vacío"):
        repo.baseline("   ")

def test_baseline_error_sin_versiones(tmp_path: Path) -> None:
    """Validar que falle si no hay un historial de commits previos."""
    repo = Repositorio(tmp_path)
    repo.init()
    with pytest.raises(ValueError, match="No se puede crear una línea base si no existen versiones"):
        repo.baseline("Release_1.0")

def test_baseline_creacion_exitosa(tmp_path: Path) -> None:
    """Validar el flujo correcto de registro y persistencia en formato .txt."""
    repo = Repositorio(tmp_path)
    repo.init()
    
    # Simular cambios para poder ejecutar un commit funcional en la rama develop
    archivo = tmp_path / "main.py"
    archivo.write_text("print('Producción v1')")
    
    repo.add("main.py")
    repo.commit("Primer commit estable")
    
    nombre_bl = "Hito_Proyecto_1"
    mensaje_resultado = repo.baseline(nombre_bl)
    
    # Comprobar salida esperada
    assert f'Línea base "{nombre_bl}" creada sobre versión v1' in mensaje_resultado
    
    # Comprobar la creación física del archivo .txt mapeado en esta versión de develop
    archivo_txt_esperado = tmp_path / ".sbac" / "baselines" / f"{nombre_bl}.txt"
    assert archivo_txt_esperado.exists()
    
    # Comprobar que contenga exactamente el ID de la versión apuntada
    contenido = archivo_txt_esperado.read_text().strip()
    assert contenido == "v1"

#----- Checkout tests|
def test_checkout_error_repositorio_no_inicializado(tmp_path: Path) -> None:
    """Validar que falle si el repositorio no está inicializado."""
    repo = Repositorio(tmp_path)
    with pytest.raises(RepositorioNoInicializadoError):
        repo.checkout("v1")


def test_checkout_error_version_no_encontrada(tmp_path: Path) -> None:
    """Validar que se lance ValueError si se solicita una versión inexistente."""
    repo = Repositorio(tmp_path)
    repo.init()
    
    # Crear un commit previo para que el historial no esté completamente vacío
    archivo = tmp_path / "main.py"
    archivo.write_text("print('v1')")
    repo.add("main.py")
    repo.commit("Primer commit")
    
    # Intentar viajar a una versión 'v99' que no existe
    with pytest.raises(ValueError, match='La versión "v99" no se encontró.'):
        repo.checkout("v99")


def test_checkout_restauracion_exitosa(tmp_path: Path) -> None:
    """Validar que el repositorio restaure correctamente el contenido de un archivo anterior."""
    repo = Repositorio(tmp_path)
    repo.init()
    
    archivo_prueba = tmp_path / "codigo.py"
    
    # 1. Crear Versión 1 (v1)
    archivo_prueba.write_text("contenido original v1")
    repo.add("codigo.py")
    repo.commit("Commit inicial v1")
    
    # 2. Modificar el archivo y crear Versión 2 (v2)
    archivo_prueba.write_text("contenido modificado v2")
    repo.commit("Commit secundario v2")
    
    # Verificar que el archivo en el espacio de trabajo actualmente posee el contenido de v2
    assert archivo_prueba.read_text() == "contenido modificado v2"
    
    # 3. Ejecutar Checkout hacia v1
    mensaje_resultado = repo.checkout("v1")
    
    # 4. Aserciones
    assert "Repositorio restaurado a la versión v1" in mensaje_resultado
    
    # Verificar que el contenido del archivo regresó físicamente al estado de v1
    assert archivo_prueba.read_text() == "contenido original v1"
    
    # Verificar que la versión actual registrada en el sistema sea v1
    assert repo.manejador.leer_current_version() == "v1"

#----- Tests de list-baselines
def test_list_baselines_error_repositorio_no_inicializado(tmp_path: Path) -> None:
    """ Validar que falle si se intenta listar líneas base sin inicializar el sistema. """
    repo = Repositorio(tmp_path)
    with pytest.raises(RepositorioNoInicializadoError):
        repo.list_baselines()


def test_list_baselines_vacio(tmp_path: Path) -> None:
    """ Validar el mensaje informativo correcto cuando no se ha creado ninguna línea base. """
    repo = Repositorio(tmp_path)
    repo.init()
    
    resultado = repo.list_baselines()
    assert resultado == "No hay líneas base."


def test_list_baselines_con_elementos(tmp_path: Path) -> None:
    """ Validar que se listen en orden alfabético todas las líneas base registradas en el disco. """
    repo = Repositorio(tmp_path)
    repo.init()
    
    # 1. Crear un escenario base con un archivo y un commit para generar la versión v1
    archivo = tmp_path / "main.py"
    archivo.write_text("print('v1')")
    repo.add("main.py")
    repo.commit("Primer Commit")
    
    # 2. Registrar múltiples líneas base deliberadamente desordenadas cronológicamente
    repo.baseline("Beta_Release")
    repo.baseline("Alpha_Release")
    
    # 3. Invocar el listado bajo prueba
    resultado = repo.list_baselines()
    
    # 4. Aserciones de formato y ordenamiento alfabético esperado (*.txt ordenados)
    lineas = resultado.split("\n")
    assert lineas[0] == "Líneas base:"
    assert lineas[1] == "Alpha_Release -> v1"
    assert lineas[2] == "Beta_Release -> v1"

#----- Tests de Diff
def test_diff_error_repositorio_no_inicializado(tmp_path: Path) -> None:
    """Validar que se bloquee el comando si el repositorio no está inicializado."""
    repo = Repositorio(tmp_path)
    with pytest.raises(RepositorioNoInicializadoError):
        repo.diff("v1", "v2")


def test_diff_error_versiones_inexistentes(tmp_path: Path) -> None:
    """Validar que se lance ValueError si se intenta comparar versiones que no existen."""
    repo = Repositorio(tmp_path)
    repo.init()
    
    # Intentar comparar versiones en un historial vacío
    with pytest.raises(ValueError, match='La versión "v1" no existe en el repositorio.'):
        repo.diff("v1", "v2")


def test_diff_versiones_identicas(tmp_path: Path) -> None:
    """Validar el mensaje esperado cuando se comparan una versión contra sí misma."""
    repo = Repositorio(tmp_path)
    repo.init()
    
    archivo = tmp_path / "main.py"
    archivo.write_text("print('Hola World')")
    repo.add("main.py")
    repo.commit("Commit inicial")  # Genera v1
    
    resultado = repo.diff("v1", "v1")
    assert resultado == "Las versiones son iguales."


def test_diff_deteccion_de_cambios_linea_por_linea(tmp_path: Path) -> None:
    """Validar la estructura del reporte generado cuando existen diferencias entre versiones."""
    repo = Repositorio(tmp_path)
    repo.init()
    
    archivo_objetivo = tmp_path / "archivo.txt"
    
    # 1. Crear versión 1 (v1)
    archivo_objetivo.write_text("Línea 1 invariable\nLínea 2 original")
    repo.add("archivo.txt")
    repo.commit("Primera versión")
    
    # 2. Crear versión 2 (v2) con modificaciones en la segunda línea
    archivo_objetivo.write_text("Línea 1 invariable\nLínea 2 modificada")
    repo.commit("Segunda versión")
    
    # 3. Invocar el comparador de versiones
    reporte_resultado = repo.diff("v1", "v2")
    
    # 4. Aserciones del formato de salida del reporte
    assert "[archivo.txt] Línea 2" in reporte_resultado
    assert "- v1: Línea 2 original" in reporte_resultado
    assert "+ v2: Línea 2 modificada" in reporte_resultado