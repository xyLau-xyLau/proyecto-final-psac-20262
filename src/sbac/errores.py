
class SBACError(Exception):
    """Excepción base para todos los errores del SBAC."""
    pass


class RepositorioYaExisteError(SBACError):
    """Se intentó inicializar un repositorio donde ya existe uno."""
    def __init__(self) -> None:
        super().__init__(
            'El repositorio SBAC ya está inicializado en este directorio'
        )


class RepositorioCreacionError(SBACError):
    """Falló la creación de la estructura .sbac/ (permisos, E/S, etc.)."""
    def __init__(self, detalle: str = '') -> None:
        mensaje = 'No se pudo crear la estructura del repositorio'
        if detalle:
            mensaje += f': {detalle}'
        super().__init__(mensaje)