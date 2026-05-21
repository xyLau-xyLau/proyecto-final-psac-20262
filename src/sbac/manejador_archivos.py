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
