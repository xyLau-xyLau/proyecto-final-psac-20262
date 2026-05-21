import sys
import enums_ayuda as ea

from pathlib import Path
from repositorio import Repositorio
from errores import SBACError

def leer_entrada() -> None:
    """
    Función que procesa los argumentos de entrada y 
    llama a las funciones correspondientes

    """
    args = sys.argv
    longitud_args = len(args)

    if longitud_args == 1 or args[1] in ['-h', '--help']:
        print(ea.ayuda())
        return None
    
    repo = Repositorio(Path.cwd())

    match (args[1], longitud_args):
        case ('init', 2):
            _ejecutar(repo.init)
        case ('init', _):
            print(ea.error_cantidad_args(
                      ea.Error.REQUIERE_CERO_ARGUMENTOS,
                      ea.Ayuda.INIT))
        case ('status', 2):
            _ejecutar(repo.status)
        case ('status', _):
            print(ea.error_cantidad_args(
                      ea.Error.REQUIERE_CERO_ARGUMENTOS,
                      ea.Ayuda.STATUS))
        case ('history', 2):
            _ejecutar(repo.history)
        case ('history', _):
            print(ea.error_cantidad_args(
                      ea.Error.REQUIERE_CERO_ARGUMENTOS,
                      ea.Ayuda.HISTORY))
        case ('list-baselines', 2):
            _ejecutar(repo.list_baselines)
        case ('list-baselines', _):
            print(ea.error_cantidad_args(
                      ea.Error.REQUIERE_CERO_ARGUMENTOS,
                      ea.Ayuda.LIST_BASELINES))
        case ('add', 3):
            _ejecutar(repo.add, args[2])
        case ('add', _):
            print(ea.error_cantidad_args(
                      ea.Error.REQUIERE_UN_ARGUMENTO,
                      ea.Ayuda.ADD))
        case ('commit', 3):
            _ejecutar(repo.commit, args[2])
        case ('commit', _):
            print(ea.error_cantidad_args(
                      ea.Error.REQUIERE_UN_ARGUMENTO,
                      ea.Ayuda.COMMIT))
        case ('baseline', 3):
            _ejecutar(repo.baseline, args[2])
        case ('baseline', _):
            print(ea.error_cantidad_args(
                      ea.Error.REQUIERE_UN_ARGUMENTO,
                      ea.Ayuda.BASELINE))          
        case ('checkout', 3):
            _ejecutar(repo.checkout, args[2])
        case ('checkout', _):
            print(ea.error_cantidad_args(
                      ea.Error.REQUIERE_UN_ARGUMENTO,
                      ea.Ayuda.CHECKOUT))
        case ('diff', 4):
            _ejecutar(repo.diff, args[2], args[3])
        case ('diff', _):
            print(ea.error_cantidad_args(
                      ea.Error.REQUIERE_DOS_ARGUMENTOS,
                      ea.Ayuda.DIFF))
        case _:
            print(ea.error_y_ayuda(ea.Error.COMANDO_NO_RECONOCIDO))

def _ejecutar(funcion, *args) -> None:
    """
    Helper que ejecuta una operación del Repositorio,
    captura cualquier SBACError y lo imprime de forma uniforme.

    Args:
        funcion: Método del Repositorio a invocar
        *args: Argumentos posicionales para la función
    """
    try:
        mensaje = funcion(*args)
        print(mensaje)
    except SBACError as e:
        print(str(e))

leer_entrada()