from pathlib import Path


class ManejadorArchivos:
    """Encapsula todas las operaciones de E/S del SBAC."""

    NOMBRE_DIR_INTERNO: str = '.sbac'
    SUBDIR_VERSIONS: str = 'versions'
    SUBDIR_BASELINES: str = 'baselines'
    ARCHIVO_TRACKED: str = 'tracked-files'

    def __init__(self, ruta_workspace: Path) -> None:
        """
        Inicializa el manejador asociándolo a un workspace.

        Args:
            ruta_workspace (Path): Directorio raíz del proyecto del usuario
        """
        self.ruta_workspace: Path = ruta_workspace
        self.ruta_sbac: Path = ruta_workspace / self.NOMBRE_DIR_INTERNO

    def existe_repositorio(self) -> bool:
        """
        Verifica si el directorio .sbac/ existe en el workspace.

        Returns:
            bool: True si existe, False en caso contrario
        """
        return self.ruta_sbac.is_dir()

    def crear_estructura(self) -> None:
        """
        Crea la estructura interna del repositorio:
        .sbac/versions/ y .sbac/baselines/.

        Raises:
            OSError: Si no se puede crear alguno de los directorios
        """
        self.ruta_sbac.mkdir(parents=False, exist_ok=False)
        (self.ruta_sbac / self.SUBDIR_VERSIONS).mkdir()
        (self.ruta_sbac / self.SUBDIR_BASELINES).mkdir()

    def existe_archivo(self, ruta_relativa: str) -> bool:
        """
        Verifica si un archivo existe en el workspace.

        Args:
            ruta_relativa (str): Ruta del archivo relativa al workspace

        Returns:
            bool: True si el archivo existe y es un archivo regular
        """
        ruta_absoluta = self.ruta_workspace / ruta_relativa
        return ruta_absoluta.is_file()

    def leer_archivo(self, ruta: Path) -> str:
        """
        Lee el contenido completo de un archivo de texto.

        Args:
            ruta (Path): Ruta absoluta del archivo

        Returns:
            str: Contenido del archivo
        """
        return ruta.read_text(encoding='utf-8')

    def escribir_archivo(self, ruta: Path, contenido: str) -> None:
        """
        Escribe contenido en un archivo de texto.
        Crea el archivo si no existe, lo sobreescribe si existe.

        Args:
            ruta (Path): Ruta absoluta del archivo
            contenido (str): Contenido a escribir
        """
        ruta.write_text(contenido, encoding='utf-8')

    def leer_tracked_files(self) -> list[str]:
        """
        Lee la lista de archivos bajo seguimiento.

        Returns:
            list[str]: Lista de rutas relativas. Lista vacía si no
                       existe el archivo tracked-files
        """
        archivo = self.ruta_sbac / self.ARCHIVO_TRACKED
        if not archivo.is_file():
            return []
        contenido = archivo.read_text(encoding='utf-8')
        return [linea.strip() for linea in contenido.splitlines() if linea.strip()]

    def escribir_tracked_files(self, rutas: list[str]) -> None:
        """
        Escribe la lista de archivos bajo seguimiento.

        Args:
            rutas (list[str]): Lista de rutas relativas
        """
        archivo = self.ruta_sbac / self.ARCHIVO_TRACKED
        contenido = '\n'.join(rutas) + ('\n' if rutas else '')
        archivo.write_text(contenido, encoding='utf-8')