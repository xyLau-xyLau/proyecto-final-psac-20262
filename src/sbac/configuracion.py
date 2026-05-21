import json
import os
from datetime import datetime, timezone
from pathlib import Path


class Configuracion:
    """Representa la configuración general de un repositorio SBAC."""

    NOMBRE_ARCHIVO: str = 'config.json'

    def __init__(self, autor: str, fecha_creacion: str) -> None:
        """
        Args:
            autor (str): Nombre del autor por defecto del repositorio
            fecha_creacion (str): Fecha en formato ISO 8601
        """
        self.autor: str = autor
        self.fecha_creacion: str = fecha_creacion

    @classmethod
    def por_defecto(cls) -> 'Configuracion':
        """
        Crea una configuración con valores por defecto:
        autor leído de la variable de entorno USER (o 'desconocido')
        y fecha de creación al momento actual.

        Returns:
            Configuracion: Instancia con valores por defecto
        """
        autor = os.environ.get('USER') or os.environ.get('USERNAME', 'desconocido')
        fecha = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        return cls(autor=autor, fecha_creacion=fecha)

    def guardar(self, ruta_sbac: Path) -> None:
        """
        Persiste la configuración como JSON en .sbac/config.json.

        Args:
            ruta_sbac (Path): Ruta absoluta del directorio .sbac/
        """
        datos = {
            'autor': self.autor,
            'fecha_creacion': self.fecha_creacion,
        }
        archivo = ruta_sbac / self.NOMBRE_ARCHIVO
        archivo.write_text(
            json.dumps(datos, indent=2, ensure_ascii=False),
            encoding='utf-8'
        )

    @classmethod
    def cargar(cls, ruta_sbac: Path) -> 'Configuracion':
        """
        Carga la configuración desde .sbac/config.json.

        Args:
            ruta_sbac (Path): Ruta absoluta del directorio .sbac/

        Returns:
            Configuracion: Instancia con los valores leídos
        """
        archivo = ruta_sbac / cls.NOMBRE_ARCHIVO
        datos = json.loads(archivo.read_text(encoding='utf-8'))
        return cls(autor=datos['autor'], fecha_creacion=datos['fecha_creacion'])