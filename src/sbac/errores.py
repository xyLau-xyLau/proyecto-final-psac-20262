
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

class RepositorioNoInicializadoError(SBACError):
    """Se intentó operar sobre un directorio sin repositorio SBAC."""

    def __init__(self) -> None:
        super().__init__(
            'No se encontró un repositorio SBAC en este directorio. '
            'Ejecuta "sbac init" primero'
        )

class ArchivoNoEncontradoError(SBACError):
    """Se referenció un archivo que no existe en el workspace."""

    def __init__(self, ruta: str) -> None:
        super().__init__(f'El archivo "{ruta}" no existe')


class ArchivoYaRastreadoError(SBACError):
    """Se intentó añadir un archivo que ya está bajo seguimiento."""

    def __init__(self, ruta: str) -> None:
        super().__init__(f'El archivo "{ruta}" ya está bajo seguimiento')