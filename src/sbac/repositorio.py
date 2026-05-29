from pathlib import Path
from datetime import datetime, timezone

from .version import Version
from .configuracion import Configuracion
from .manejador_archivos import ManejadorArchivos
from .errores import (RepositorioYaExisteError, RepositorioCreacionError,
                    RepositorioNoInicializadoError, ArchivoNoEncontradoError,
                    ArchivoYaRastreadoError, MensajeVacioError,
                    SinArchivosRastreadosError, SinCambiosError,
                    ArchivoRastreadoFaltanteError, ArchivoNoRastreadoError)


class Repositorio:
    """Orquesta las operaciones sobre un repositorio SBAC."""

    def __init__(self, ruta_workspace: Path) -> None:
        """
        Args:
            ruta_workspace (Path): Directorio raíz del proyecto del usuario
        """
        self.ruta_workspace: Path = ruta_workspace
        self.manejador: ManejadorArchivos = ManejadorArchivos(ruta_workspace)

    def init(self) -> str:
        """
        Inicializa un nuevo repositorio SBAC en el workspace.
        Crea la estructura .sbac/versions/, .sbac/baselines/,
        .sbac/config.json y .sbac/tracked-files.

        Returns:
            str: Mensaje de éxito

        Raises:
            RepositorioYaExisteError: Si .sbac/ ya existe
            RepositorioCreacionError: Si falla la creación de la estructura
        """
        if self.manejador.existe_repositorio():
            raise RepositorioYaExisteError()

        try:
            self.manejador.crear_estructura()
            Configuracion.por_defecto().guardar(self.manejador.ruta_sbac)
            self.manejador.escribir_tracked_files([])
        except OSError as e:
            raise RepositorioCreacionError(detalle=str(e)) from e

        return 'Repositorio SBAC inicializado en .sbac/'


    def add(self, ruta_archivo: str) -> str:
        """
        Añade uno o varios archivos al seguimiento del repositorio.

        Comportamiento según el argumento:
        - '.'          : añade todos los archivos del workspace no rastreados
        - un directorio: añade recursivamente los archivos que contenga
        - un archivo   : añade ese archivo individual

        Args:
            ruta_archivo (str): Ruta de archivo, directorio, o '.'

        Returns:
            str: Mensaje de éxito en español

        Raises:
            RepositorioNoInicializadoError: Si no existe .sbac/
            ArchivoNoEncontradoError: Si la ruta no existe (caso individual)
            ArchivoYaRastreadoError: Si el archivo ya está rastreado (caso individual)
        """
        if not self.manejador.existe_repositorio():
            raise RepositorioNoInicializadoError()

        if ruta_archivo == '.':
            return self._add_multiple(self.manejador.listar_workspace())

        # Normalizar: quitar la barra final si la tiene (a/ -> a)
        ruta_limpia = ruta_archivo.rstrip('/')

        # Caso directorio: expandir recursivamente
        if self.manejador.existe_directorio(ruta_limpia):
            archivos_dir = self.manejador.listar_directorio(ruta_limpia)
            if not archivos_dir:
                return f'El directorio "{ruta_archivo}" no contiene archivos'
            return self._add_multiple(archivos_dir)

        # Caso archivo individual
        if not self.manejador.existe_archivo(ruta_limpia):
            raise ArchivoNoEncontradoError(ruta_archivo)

        rastreados = self.manejador.leer_tracked_files()
        if ruta_limpia in rastreados:
            raise ArchivoYaRastreadoError(ruta_limpia)

        rastreados.append(ruta_limpia)
        self.manejador.escribir_tracked_files(rastreados)
        return f'"{ruta_limpia}" añadido al seguimiento'
    

    def rm(self, ruta_archivo: str) -> str:
        """
        Quita un archivo del seguimiento del repositorio.
        No elimina el archivo del workspace, solo deja de rastrearlo.
        Creada para complementar el comando add.

        Args:
            ruta_archivo (str): Ruta del archivo a dejar de rastrear

        Returns:
            str: Mensaje de éxito en español

        Raises:
            RepositorioNoInicializadoError: Si no existe .sbac/
            ArchivoNoRastreadoError: Si el archivo no estaba bajo seguimiento
        """
        if not self.manejador.existe_repositorio():
            raise RepositorioNoInicializadoError()

        rastreados = self.manejador.leer_tracked_files()
        if ruta_archivo not in rastreados:
            raise ArchivoNoRastreadoError(ruta_archivo)

        rastreados.remove(ruta_archivo)
        self.manejador.escribir_tracked_files(rastreados)
        return f'"{ruta_archivo}" eliminado del seguimiento'
    

    def commit(self, mensaje: str) -> str:
        """
        Registra una nueva versión con los archivos bajo seguimiento.

        Args:
            mensaje (str): Mensaje descriptivo del commit

        Returns:
            str: Mensaje de éxito en español

        Raises:
            RepositorioNoInicializadoError: Si no existe .sbac/
            MensajeVacioError: Si el mensaje está vacío
            SinArchivosRastreadosError: Si no hay archivos bajo seguimiento
            ArchivoRastreadoFaltanteError: Si un archivo rastreado fue borrado
            SinCambiosError: Si no hay cambios respecto a la última versión
        """
        if not self.manejador.existe_repositorio():
            raise RepositorioNoInicializadoError()

        if not mensaje or not mensaje.strip():
            raise MensajeVacioError()

        rastreados = self.manejador.leer_tracked_files()
        if not rastreados:
            raise SinArchivosRastreadosError()

        # Verificar que todos los archivos rastreados existan
        for archivo in rastreados:
            if not self.manejador.existe_archivo(archivo):
                raise ArchivoRastreadoFaltanteError(archivo)

        version_padre = self.manejador.leer_current_version()

        # Si hay versión previa, verificar que haya cambios
        if version_padre and not self._hay_cambios(rastreados, version_padre):
            raise SinCambiosError()

        # Crear la nueva versión
        nuevo_id = self._siguiente_id()
        dir_files = self.manejador.crear_dir_version(nuevo_id)

        for archivo in rastreados:
            self.manejador.copiar_a_version(archivo, dir_files)

        config = Configuracion.cargar(self.manejador.ruta_sbac)
        timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

        version = Version(
            id=nuevo_id,
            parent_id=version_padre,
            timestamp=timestamp,
            autor=config.autor,
            mensaje=mensaje.strip(),
            archivos=rastreados,
        )

        self.manejador.guardar_metadata(nuevo_id, version.a_dict())
        self.manejador.escribir_current_version(nuevo_id)

        return f'Versión {nuevo_id} registrada: "{mensaje.strip()}"'


    def status(self) -> str:
        """
        Muestra el estado actual del repositorio: archivos rastreados
        sin cambios, modificados, eliminados y sin seguimiento.

        Returns:
            str: Reporte del estado en español

        Raises:
            RepositorioNoInicializadoError: Si no existe .sbac/
        """
        if not self.manejador.existe_repositorio():
            raise RepositorioNoInicializadoError()

        rastreados = self.manejador.leer_tracked_files()
        version_actual = self.manejador.leer_current_version()

        sin_cambios: list[str] = []
        modificados: list[str] = []
        eliminados: list[str] = []

        for archivo in rastreados:
            if not self.manejador.existe_archivo(archivo):
                eliminados.append(archivo)
            elif version_actual and self._archivo_modificado(archivo, version_actual):
                modificados.append(archivo)
            else:
                sin_cambios.append(archivo)

        # Archivos del workspace que no están rastreados
        en_workspace = self.manejador.listar_workspace()
        sin_seguimiento = [a for a in en_workspace if a not in rastreados]

        return self._formatear_status(
            sin_cambios, modificados, eliminados, sin_seguimiento, version_actual)

    def history(self) -> str:
        """
        Muestra el historial completo de versiones en orden cronológico.
        
        Returns:
        str: Historial de versiones en orden cronológico

        Raises:
            RepositorioNoInicializadoError: Si no existe .sbac/
        """
        if not self.manejador.existe_repositorio():
            raise RepositorioNoInicializadoError()
        
        #usando lambda porque sorted no evalua el valor numérico de los números en un string y pondría 10 antes de 2
        versiones_ids = sorted(
            self.manejador.listar_versiones(),
            key=lambda v: int(v[1:])
        )
        if not versiones_ids:
            return 'No hay versiones.'
        
        resultado = ['Historial de versiones:']
        
        for version_id in versiones_ids:
            metadata = self.manejador.leer_metadata(version_id)
            version = Version.desde_dict(metadata)
            resultado.append(
                f'{version.id} | '
                f'{version.timestamp} | '
                f'{version.autor} | '
                f'{version.mensaje}'
            )
            
        return '\n'.join(resultado)

    def baseline(self, nombre: str) -> str:
        """
        Marca la versión actual como línea base con un nombre identificador.

        Args:
            nombre (str): Nombre identificador
        
        Returns:
            str: Mensaje de éxito

        Raises:
            RepositorioNoInicializadoError: Si no existe .sbac/
        """
        if not self.manejador.existe_repositorio():
            raise RepositorioNoInicializadoError()
        
        version_actual = self.manejador.leer_current_version()

        if not version_actual:
            return 'No existen versiones para marcar como línea base.'
        
        ruta_baseline = (
            self.manejador.ruta_sbac /
            self.manejador.SUBDIR_BASELINES /
            f'{nombre}.txt'
        )

        self.manejador.escribir_archivo(
            ruta_baseline,
            version_actual
        )

        return (
            f'Línea base "{nombre}" '
            f'creada sobre versión {version_actual}'
        )

def list_baselines(self) -> str:
    """
    Lista las líneas base registradas.

    Returns:
        str: Líneas base disponibles

    Raises:
        RepositorioNoInicializadoError: Si no existe .sbac/
    """
    if not self.manejador.existe_repositorio():
        raise RepositorioNoInicializadoError()

    baselines = (
        self.manejador.ruta_sbac /
        self.manejador.SUBDIR_BASELINES
    )

    archivos = sorted(baselines.glob('*.txt'))

    if not archivos:
        return 'No hay líneas base.'

    resultado = ['Líneas base:']

    for archivo in archivos:

        nombre = archivo.stem

        version = self.manejador.leer_archivo(archivo).strip()

        resultado.append(
            f'{nombre} -> {version}'
        )

    return '\n'.join(resultado)

def diff(self, v1: str, v2: str) -> str:
    """
    Compara dos versiones línea por línea.

    Args:
        v1 (str): Primera versión
        v2 (str): Segunda versión

    Returns:
        str: Diferencias entre versiones

    Raises:
        RepositorioNoInicializadoError: Si no existe .sbac/
    """
    if not self.manejador.existe_repositorio():
        raise RepositorioNoInicializadoError()

    versiones = self.manejador.listar_versiones()

    if v1 not in versiones or v2 not in versiones:
        return 'Una o ambas versiones no se encontraron.'

    metadata_v1 = Version.desde_dict(
        self.manejador.leer_metadata(v1)
    )

    metadata_v2 = Version.desde_dict(
        self.manejador.leer_metadata(v2)
    )

    archivos = sorted(
        list(set(metadata_v1.archivos + metadata_v2.archivos))
    )
    
    resultado = []

    for archivo in archivos:

        contenido_v1 = ''
        contenido_v2 = ''

        if archivo in metadata_v1.archivos:
            contenido_v1 = self.manejador.leer_archivo_de_version(
                v1,
                archivo
            )

        if archivo in metadata_v2.archivos:
            contenido_v2 = self.manejador.leer_archivo_de_version(
                v2,
                archivo
            )

        lineas_v1 = contenido_v1.splitlines()
        lineas_v2 = contenido_v2.splitlines()

        max_lineas = max(
            len(lineas_v1),
            len(lineas_v2)
        )

        for i in range(max_lineas):

            linea1 = (
                lineas_v1[i]
                if i < len(lineas_v1)
                else ''
            )

            linea2 = (
                lineas_v2[i]
                if i < len(lineas_v2)
                else ''
            )

            if linea1 != linea2:

                resultado.append(
                    f'[{archivo}] Línea {i + 1}'
                )

                resultado.append(
                    f'- {v1}: {linea1}'
                )

                resultado.append(
                    f'+ {v2}: {linea2}'
                )

    if not resultado:
        return 'Las versiones son iguales.'

    return '\n'.join(resultado)

def checkout(self, version_id: str) -> str:
    """
    Regresa el repositorio al estado de una versión específica.

    Args:
        version_id (str): ID de versión

    Returns:
        str: Mensaje de éxito

    Raises:
        RepositorioNoInicializadoError: Si no existe .sbac/
    """
    if not self.manejador.existe_repositorio():
        raise RepositorioNoInicializadoError()

    versiones = self.manejador.listar_versiones()

    if version_id not in versiones:
        return f'La versión "{version_id}" no se encontró.'

    metadata = self.manejador.leer_metadata(version_id)

    version = Version.desde_dict(metadata)

    for archivo in version.archivos:

        contenido = self.manejador.leer_archivo_de_version(
            version_id,
            archivo
        )

        ruta_destino = (
            self.ruta_workspace /
            archivo
        )

        ruta_destino.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        self.manejador.escribir_archivo(
            ruta_destino,
            contenido
        )

    self.manejador.escribir_current_version(
        version_id
    )

    return (
        f'Repositorio restaurado '
        f'a la versión {version_id}'
    )
    
    # ---> Helpers privados ---

    def _add_todos(self) -> str:
        """
        Añade al seguimiento todos los archivos del workspace que
        aún no estén rastreados.

        Returns:
            str: Resumen de los archivos añadidos
        """
        rastreados = self.manejador.leer_tracked_files()
        en_workspace = self.manejador.listar_workspace()

        nuevos = [a for a in en_workspace if a not in rastreados]

        if not nuevos:
            return 'No hay archivos nuevos para añadir al seguimiento'

        rastreados.extend(nuevos)
        self.manejador.escribir_tracked_files(rastreados)

        lineas = [f'{len(nuevos)} archivo(s) añadido(s) al seguimiento:']
        for archivo in nuevos:
            lineas.append(f'  {archivo}')
        return '\n'.join(lineas)
    
    def _add_multiple(self, candidatos: list[str]) -> str:
        """
        Añade al seguimiento los archivos de una lista que aún no
        estén rastreados. Ignora silenciosamente los ya rastreados.

        Args:
            candidatos (list[str]): Rutas relativas candidatas a añadir

        Returns:
            str: Resumen de los archivos añadidos
        """
        rastreados = self.manejador.leer_tracked_files()
        nuevos = [a for a in candidatos if a not in rastreados]

        if not nuevos:
            return 'No hay archivos nuevos para añadir al seguimiento'

        rastreados.extend(nuevos)
        self.manejador.escribir_tracked_files(rastreados)

        lineas = [f'{len(nuevos)} archivo(s) añadido(s) al seguimiento:']
        for archivo in nuevos:
            lineas.append(f'  {archivo}')
        return '\n'.join(lineas)

    def _siguiente_id(self) -> str:
        """
        Calcula el siguiente ID de versión secuencial.

        Returns:
            str: Siguiente ID (ej. si existen v1, v2 -> 'v3')
        """
        versiones = self.manejador.listar_versiones()
        numeros = [int(v[1:]) for v in versiones if v.startswith('v') and v[1:].isdigit()]
        siguiente = max(numeros) + 1 if numeros else 1
        return f'v{siguiente}'

    def _hay_cambios(self, rastreados: list[str], version_id: str) -> bool:
        """
        Determina si algún archivo rastreado difiere de la versión dada.

        Args:
            rastreados (list[str]): Archivos bajo seguimiento
            version_id (str): Versión contra la cual comparar

        Returns:
            bool: True si hay al menos un cambio
        """
        metadata = self.manejador.leer_metadata(version_id)
        archivos_version = metadata.get('archivos', [])

        # Cambio si la lista de archivos difiere
        if set(rastreados) != set(archivos_version):
            return True

        # Cambio si el contenido de algún archivo es diferente
        for archivo in rastreados:
            if self._archivo_modificado(archivo, version_id):
                return True

        return False

    def _archivo_modificado(self, archivo: str, version_id: str) -> bool:
        """
        Compara el contenido actual de un archivo con el de una versión.

        Args:
            archivo (str): Ruta relativa del archivo
            version_id (str): Versión contra la cual comparar

        Returns:
            bool: True si el contenido difiere o el archivo no estaba
                  en esa versión
        """
        metadata = self.manejador.leer_metadata(version_id)
        if archivo not in metadata.get('archivos', []):
            return True

        ruta_actual = self.ruta_workspace / archivo
        contenido_actual = self.manejador.leer_archivo(ruta_actual)
        contenido_version = self.manejador.leer_archivo_de_version(version_id, archivo)
        return contenido_actual != contenido_version

    def _formatear_status(self, sin_cambios, modificados, eliminados,
                          sin_seguimiento, version_actual) -> str:
        """
        Construye el reporte de estado.

        Returns:
            str: Reporte formateado
        """
        lineas = []
        if version_actual:
            lineas.append(f'Versión actual: {version_actual}')
        else:
            lineas.append('Versión actual: ninguna (sin commits todavía)')
        lineas.append('')

        def bloque(titulo: str, items: list[str]) -> None:
            lineas.append(f'{titulo}:')
            if items:
                for item in items:
                    lineas.append(f'  {item}')
            else:
                lineas.append('  ninguno')
            lineas.append('')

        bloque('Archivos modificados', modificados)
        bloque('Archivos eliminados', eliminados)
        bloque('Archivos sin cambios', sin_cambios)
        bloque('Archivos sin seguimiento', sin_seguimiento)

        return '\n'.join(lineas).rstrip()