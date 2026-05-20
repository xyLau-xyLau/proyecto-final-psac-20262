import sys
import enums_ayuda as ea

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
    match (args[1], longitud_args):
        case ('init', 2):
            print("Llamada a función init")
        case ('init', _):
            print(ea.error_cantidad_args(
                      ea.Error.REQUIERE_CERO_ARGUMENTOS,
                      ea.Ayuda.INIT))
        case ('status', 2):
            print("Llamada a función status")
        case ('status', _):
            print(ea.error_cantidad_args(
                      ea.Error.REQUIERE_CERO_ARGUMENTOS,
                      ea.Ayuda.STATUS))
        case ('history', 2):
            print("Llamada a función history")
        case ('history', _):
            print(ea.error_cantidad_args(
                      ea.Error.REQUIERE_CERO_ARGUMENTOS,
                      ea.Ayuda.HISTORY))
        case ('list-baselines', 2):
            print("Llamada a función list-baselines")
        case ('list-baselines', _):
            print(ea.error_cantidad_args(
                      ea.Error.REQUIERE_CERO_ARGUMENTOS,
                      ea.Ayuda.LIST_BASELINES))
        case ('add', 3):
            print("Llamada a función add")
        case ('add', _):
            print(ea.error_cantidad_args(
                      ea.Error.REQUIERE_UN_ARGUMENTO,
                      ea.Ayuda.ADD))
        case ('commit', 3):
            print("Llamada a función commit")
        case ('commit', _):
            print(ea.error_cantidad_args(
                      ea.Error.REQUIERE_UN_ARGUMENTO,
                      ea.Ayuda.COMMIT))
        case ('baseline', 3):
            print("Llamada a función baseline")
        case ('baseline', _):
            print(ea.error_cantidad_args(
                      ea.Error.REQUIERE_UN_ARGUMENTO,
                      ea.Ayuda.BASELINE))          
        case ('checkout', 3):
            print("Llamada a función checkout")
        case ('checkout', _):
            print(ea.error_cantidad_args(
                      ea.Error.REQUIERE_UN_ARGUMENTO,
                      ea.Ayuda.CHECKOUT))
        case ('diff', 4):
            print("Llamada a función diff")
        case ('diff', _):
            print(ea.error_cantidad_args(
                      ea.Error.REQUIERE_DOS_ARGUMENTOS,
                      ea.Ayuda.DIFF))
        case _:
            print(ea.error_y_ayuda(ea.Error.COMANDO_NO_RECONOCIDO))

leer_entrada()
