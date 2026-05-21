from enum import Enum

class Error(Enum):
    """
    Enumeration para mensajes de error
    """
    COMANDO_NO_RECONOCIDO = ('ERROR: Combinación de comandos '
                             'y parámetros no reconocidos')
    REQUIERE_CERO_ARGUMENTOS = 'No requiere parámetros'
    REQUIERE_UN_ARGUMENTO = 'Requiere exactamente un argumento'
    REQUIERE_DOS_ARGUMENTOS = 'Requiere exactamente dos argumentos'


class Ayuda(Enum):
    """
    Enumeration para los comandos básicos de SBAC
    """
    SBAC = 'SBAC - Sistema básico de administración de la configuración'
    LINEA = '-----------------------------------------------------------'
    INIT = 'init               | Inicializa el repositorio'
    ADD = 'add <archivo>      | Agrega archivo al seguimiento'
    STATUS = 'status             | Despliega el estado del repositorio'
    COMMIT = 'commit "mensaje"   | Crea una nueva versión'
    HISTORY = 'history            | Ver historial de versiones'
    BASELINE = 'baseline "nombre"  | Marcar línea base'
    LIST_BASELINES = 'list-baselines     | Listar líneas base'
    DIFF = 'diff <v1> <v2>     | Ver diferencias entre versiones'
    CHECKOUT = 'checkout <version> | Regresar a versión específica'

def ayuda() -> str:
    """
    Función para generar una cadena con la información de ayuda

    Returns:
        str: Cadena con información de ayuda
    """
    salida = Ayuda.LINEA.value + '\n'
    for x in Ayuda:
        salida += x.value + '\n'
    return salida[:-1]

def error_y_ayuda(tipo_error: Error) -> str:
    """
    Función para generar una cadena especificando el error
    cuando se manejan comandos desconocidos.

    Añade la ayuda general

    Args:
        tipo_error (Error): que comando genera el error
    
    Returns:
        str: Cadena con la información del error y la ayuda
    """
    salida = tipo_error.value + '\n\n'
    salida += ayuda()
    return salida

def error_cantidad_args(tipo_error: Error, ayuda:Ayuda) -> str:
    """ 
    Función para generar una cadena especificando errores
    y la ayuda específica para el comando ejecutado
    
    Args:
        tipo_error (Error): el comando que genera el error
        ayuda (Ayuda): qué comando listar como recomendación de uso
    
    Returns:
        str: Cadena con la información generada
    """
    salida = 'El comando: ' + ayuda.name.lower() + ' - '
    salida += tipo_error.value + '\n'
    salida += 'Uso recomendado: \n' + ayuda.value
    return salida