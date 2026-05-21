from dataclasses import dataclass, field

@dataclass
class Version:
    """
    Representa una versión registrada en el historial.

    Attributes:
        id (str): Identificador secuencial (v1, v2, ...)
        parent_id (str): ID de la versión padre, o '' para la primera
        timestamp (str): Fecha y hora de creación
        autor (str): Autor del commit
        mensaje (str): Mensaje descriptivo del commit
        archivos (list[str]): Rutas relativas incluidas en esta versión
    """
    id: str
    parent_id: str
    timestamp: str
    autor: str
    mensaje: str
    archivos: list[str] = field(default_factory=list) 