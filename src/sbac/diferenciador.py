from version import Version


class Diferenciador:
    """Encapsula la lógica de comparación entre versiones (difflib)."""

    def comparar(self, v1: Version, v2: Version) -> str:
        """
        Compara dos versiones y devuelve las diferencias.

        Args:
            v1 (Version): Primera versión
            v2 (Version): Segunda versión

        Returns:
            str: Diferencias en formato legible
        """
        raise NotImplementedError('Pendiente para RF-08')