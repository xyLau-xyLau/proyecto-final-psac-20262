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


    def a_dict(self) -> dict:
        """
        Convierte la versión a un diccionario serializable a JSON.

        Returns:
            dict: Representación de la versión
        """
        return {
            'id': self.id,
            'parent_id': self.parent_id,
            'timestamp': self.timestamp,
            'autor': self.autor,
            'mensaje': self.mensaje,
            'archivos': self.archivos,
        }
    
    @classmethod
    def desde_dict(cls, datos: dict) -> 'Version':
        """
        Reconstruye una Version a partir de un diccionario.

        Args:
            datos (dict): Metadatos leídos de metadata.json

        Returns:
            Version: Instancia reconstruida
        """
        return cls(
            id=datos['id'],
            parent_id=datos['parent_id'],
            timestamp=datos['timestamp'],
            autor=datos['autor'],
            mensaje=datos['mensaje'],
            archivos=datos.get('archivos', []),
        )