from dataclasses import dataclass

@dataclass
class Baseline:
    """
    Representa una línea base marcada sobre una versión específica.

    Attributes:
        nombre (str): Nombre identificador de la línea base
        version_id (str): ID de la versión asociada
        fecha (str): Fecha de marcado
    """
    nombre: str
    version_id: str
    fecha: str