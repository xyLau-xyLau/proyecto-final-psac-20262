from pathlib import Path


class ManejadorArchivos:
    """Encapsula todas las operaciones de E/S del SBAC."""

    NOMBRE_DIR_INTERNO: str = '.sbac'
    SUBDIR_VERSIONS: str = 'versions'
    SUBDIR_BASELINES: str = 'baselines'
    ARCHIVO_TRACKED: str = 'tracked-files'
    ARCHIVO_CURRENT: str = 'current-version' # Archivo que almacena el ID de la versión actual

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

    def listar_workspace(self) -> list[str]:
            """
            Lista los archivos regulares del workspace, excluyendo
            el directorio interno .sbac/.

            Returns:
                list[str]: Rutas relativas de los archivos del workspace
            """
            resultado = []
            for ruta in self.ruta_workspace.rglob('*'):
                if ruta.is_file():
                    relativa = ruta.relative_to(self.ruta_workspace)
                    # Excluir todo lo que esté dentro de .sbac/
                    if relativa.parts and relativa.parts[0] == self.NOMBRE_DIR_INTERNO:
                        continue
                    resultado.append(str(relativa))
            return resultado

    def leer_current_version(self) -> str:
        """
        Lee el ID de la última versión registrada.

        Returns:
            str: ID de la versión actual (ej. 'v3'), o '' si no hay
                 versiones registradas todavía
        """
        archivo = self.ruta_sbac / self.ARCHIVO_CURRENT
        if not archivo.is_file():
            return ''
        return archivo.read_text(encoding='utf-8').strip()

    def escribir_current_version(self, version_id: str) -> None:
        """
        Actualiza el puntero a la última versión registrada.

        Args:
            version_id (str): ID de la versión (ej. 'v3')
        """
        archivo = self.ruta_sbac / self.ARCHIVO_CURRENT
        archivo.write_text(version_id, encoding='utf-8')

    def crear_dir_version(self, version_id: str) -> Path:
        """
        Crea la carpeta de una versión con su subcarpeta files/.

        Args:
            version_id (str): ID de la versión (ej. 'v1')

        Returns:
            Path: Ruta absoluta de la carpeta files/ de la versión
        """
        dir_version = self.ruta_sbac / self.SUBDIR_VERSIONS / version_id
        dir_files = dir_version / 'files'
        dir_files.mkdir(parents=True, exist_ok=False)
        return dir_files

    def listar_versiones(self) -> list[str]:
        """
        Lista los IDs de todas las versiones registradas.

        Returns:
            list[str]: IDs de versión presentes en versions/
        """
        dir_versions = self.ruta_sbac / self.SUBDIR_VERSIONS
        if not dir_versions.is_dir():
            return []
        return [p.name for p in dir_versions.iterdir() if p.is_dir()]

    def copiar_a_version(self, ruta_relativa: str, dir_files: Path) -> None:
        """
        Copia un archivo del workspace a la carpeta files/ de una versión.

        Args:
            ruta_relativa (str): Ruta del archivo relativa al workspace
            dir_files (Path): Carpeta files/ destino de la versión
        """
        import shutil
        origen = self.ruta_workspace / ruta_relativa
        destino = dir_files / ruta_relativa
        destino.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(origen, destino)

    def leer_archivo_de_version(self, version_id: str, ruta_relativa: str) -> str:
        """
        Lee el contenido de un archivo tal como quedó en una versión.

        Args:
            version_id (str): ID de la versión
            ruta_relativa (str): Ruta del archivo relativa al workspace

        Returns:
            str: Contenido del archivo en esa versión
        """
        ruta = (self.ruta_sbac / self.SUBDIR_VERSIONS / version_id
                / 'files' / ruta_relativa)
        return ruta.read_text(encoding='utf-8')

    def guardar_metadata(self, version_id: str, datos: dict) -> None:
        """
        Persiste el metadata.json de una versión.

        Args:
            version_id (str): ID de la versión
            datos (dict): Diccionario con los metadatos
        """
        import json
        ruta = self.ruta_sbac / self.SUBDIR_VERSIONS / version_id / 'metadata.json'
        ruta.write_text(
            json.dumps(datos, indent=2, ensure_ascii=False),
            encoding='utf-8'
        )

    def leer_metadata(self, version_id: str) -> dict:
        """
        Lee el metadata.json de una versión.

        Args:
            version_id (str): ID de la versión

        Returns:
            dict: Metadatos de la versión
        """
        import json
        ruta = self.ruta_sbac / self.SUBDIR_VERSIONS / version_id / 'metadata.json'
        return json.loads(ruta.read_text(encoding='utf-8'))
    

    def existe_directorio(self, ruta_relativa: str) -> bool:
        """
        Verifica si una ruta del workspace es un directorio existente.

        Args:
            ruta_relativa (str): Ruta relativa al workspace

        Returns:
            bool: True si existe y es un directorio
        """
        ruta_absoluta = self.ruta_workspace / ruta_relativa
        return ruta_absoluta.is_dir()

    def listar_directorio(self, ruta_relativa: str) -> list[str]:
        """
        Lista recursivamente los archivos regulares dentro de un
        directorio del workspace, excluyendo el directorio interno .sbac/.

        Args:
            ruta_relativa (str): Ruta relativa del directorio

        Returns:
            list[str]: Rutas relativas (respecto al workspace) de los
                       archivos encontrados
        """
        dir_absoluto = self.ruta_workspace / ruta_relativa
        resultado = []
        for ruta in dir_absoluto.rglob('*'):
            if ruta.is_file():
                relativa = ruta.relative_to(self.ruta_workspace)
                if relativa.parts and relativa.parts[0] == self.NOMBRE_DIR_INTERNO:
                    continue
                resultado.append(str(relativa))
        return resultado