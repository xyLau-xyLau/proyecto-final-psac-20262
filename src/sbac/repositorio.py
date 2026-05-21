from pathlib import Path

from configuracion import Configuracion
from manejador_archivos import ManejadorArchivos
from errores import (RepositorioYaExisteError, RepositorioCreacionError,
                    RepositorioNoInicializadoError, ArchivoNoEncontradoError,
                    ArchivoYaRastreadoError)


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
        Añade un archivo al seguimiento del repositorio.

        Args:
            ruta_archivo (str): Ruta del archivo relativa al workspace

        Returns:
            str: Mensaje de éxito en español

        Raises:
            RepositorioNoInicializadoError: Si no existe .sbac/
            ArchivoNoEncontradoError: Si el archivo no existe en el workspace
            ArchivoYaRastreadoError: Si el archivo ya está bajo seguimiento
        """
        if not self.manejador.existe_repositorio():
            raise RepositorioNoInicializadoError()

        if not self.manejador.existe_archivo(ruta_archivo):
            raise ArchivoNoEncontradoError(ruta_archivo)

        rastreados = self.manejador.leer_tracked_files()
        if ruta_archivo in rastreados:
            raise ArchivoYaRastreadoError(ruta_archivo)

        rastreados.append(ruta_archivo)
        self.manejador.escribir_tracked_files(rastreados)

        return f'"{ruta_archivo}" añadido al seguimiento'
    
    # --- Comandos pendientes ---

    def status(self) -> str:
        """Pendiente para RF-03."""
        raise NotImplementedError('Pendiente para RF-03')

    def commit(self, mensaje: str) -> str:
        """Pendiente para RF-04."""
        raise NotImplementedError('Pendiente para RF-04')

    def history(self) -> str:
        """Pendiente para RF-05."""
        raise NotImplementedError('Pendiente para RF-05')

    def baseline(self, nombre: str) -> str:
        """Pendiente para RF-06."""
        raise NotImplementedError('Pendiente para RF-06')

    def list_baselines(self) -> str:
        """Pendiente para RF-07."""
        raise NotImplementedError('Pendiente para RF-07')

    def diff(self, v1: str, v2: str) -> str:
        """Pendiente para RF-08."""
        raise NotImplementedError('Pendiente para RF-08')

    def checkout(self, version_id: str) -> str:
        """Pendiente para RF-09."""
        raise NotImplementedError('Pendiente para RF-09')