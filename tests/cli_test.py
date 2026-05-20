import pytest
import enums_ayuda as ea
import sys
from cli import leer_entrada

@pytest.fixture
def test_args() -> list[str]:
    """
    Fixture para simular sys.argv

    Returns: Lista con el nombre del programa
    """
    return ['cli.py']

def test_entrada_vacia(monkeypatch: pytest.MonkeyPatch, 
                       capsys:pytest.CaptureFixture[str], 
                       test_args: list[str]) -> None:
    """
    Test para entrada vacía
    Args:
        monkeypatch(pytest.MonkeyPatch): Fixture para manejo de entorno
        capsys(pytest.CaptureFixture[str]): Fixture para capturar stdout
        test_args(list[str]): Fixture para simular argv
    """
    monkeypatch.setattr(sys, 'argv', test_args)
    leer_entrada()
    capture = capsys.readouterr()
    assert capture.out[:-1] == ea.ayuda()

@pytest.mark.parametrize('comando', ['-h', '--help'])
def test_help(monkeypatch: pytest.MonkeyPatch, 
              capsys: pytest.CaptureFixture[str], 
              comando: str,
              test_args: list[str]) -> None:
    """
    Test para el comando de ayuda
    Args:
        monkeypatch(pytest.MonkeyPatch): Fixture para manejo de entorno
        capsys(pytest.CaptureFixture[str]): Fixture para capturar stdout
        test_args(list[str]): Fixture para simular argv
        comando(str): comandos para ayuda(-h, --help)
    """
    test_args += [comando]
    monkeypatch.setattr(sys, 'argv', test_args)
    leer_entrada()
    capture = capsys.readouterr()
    assert capture.out[:-1] == ea.ayuda()

@pytest.mark.parametrize('comando', 
                         ['init', 'status', 'history', 'list-baselines'])
@pytest.mark.parametrize('params', 
                         [['parametro1'], ['parametro2', 'parametro3']])
def test_entrada_comando_sin_parametros(monkeypatch: pytest.MonkeyPatch, 
                                        capsys: pytest.CaptureFixture[str], 
                                        comando: str, 
                                        params: list[str],
                                        test_args: list[str]) -> None:
    """
    Test para verificar manejo de errores en comandos
    que no requieren parámetros

    Args:
        monkeypatch(pytest.MonkeyPatch): Fixture para manejo de entorno
        capsys(pytest.CaptureFixture[str]): Fixture para capturar stdout
        test_args(list[str]): Fixture para simular argv
        comando(str): comando a probar
        params(list[str]): parametros para provocar errores 
    """
    test_args += [comando]
    test_args += params
    monkeypatch.setattr(sys, 'argv', test_args)
    leer_entrada()
    capture = capsys.readouterr()
    match comando:
        case 'init':
            assert capture.out[:-1] == ea.error_cantidad_args(
                                           ea.Error.REQUIERE_CERO_ARGUMENTOS, 
                                           ea.Ayuda.INIT)
        case 'status':
            assert capture.out[:-1] == ea.error_cantidad_args(
                                           ea.Error.REQUIERE_CERO_ARGUMENTOS, 
                                           ea.Ayuda.STATUS)
        case 'history':
            assert capture.out[:-1] == ea.error_cantidad_args(
                                           ea.Error.REQUIERE_CERO_ARGUMENTOS, 
                                           ea.Ayuda.HISTORY)
        case _:
            assert capture.out[:-1] == ea.error_cantidad_args(
                                           ea.Error.REQUIERE_CERO_ARGUMENTOS, 
                                           ea.Ayuda.LIST_BASELINES)

@pytest.mark.parametrize('comando', 
                         ['add', 'commit', 'baseline', 'checkout'])
@pytest.mark.parametrize('params', 
                         [[], ['parametro2', 'parametro3']])
def test_entrada_comando_un_parametro(monkeypatch: pytest.MonkeyPatch, 
                                      capsys: pytest.CaptureFixture[str],
                                      comando: str,
                                      params: list[str],
                                      test_args: list[str]) -> None:
    """
    Test para verificar manejo de errores en comandos
    que requieren un argumento

    Args:
        monkeypatch(pytest.MonkeyPatch): Fixture para manejo de entorno
        capsys(pytest.CaptureFixture[str]): Fixture para capturar stdout
        test_args(list[str]): Fixture para simular argv
        comando(str): comando a probar
        params(list[str]): parametros para provocar errores 
    """
    test_args += [comando]
    test_args += params
    monkeypatch.setattr(sys, 'argv', test_args)
    leer_entrada()
    capture = capsys.readouterr()
    match comando:
        case 'add':
            assert capture.out[:-1] == ea.error_cantidad_args(
                                       ea.Error.REQUIERE_UN_ARGUMENTO, 
                                       ea.Ayuda.ADD)
        case 'commit':
            assert capture.out[:-1] == ea.error_cantidad_args(
                                           ea.Error.REQUIERE_UN_ARGUMENTO, 
                                           ea.Ayuda.COMMIT)
        case 'baseline':
            assert capture.out[:-1] == ea.error_cantidad_args(
                                           ea.Error.REQUIERE_UN_ARGUMENTO, 
                                           ea.Ayuda.BASELINE)
        case _:
            assert capture.out[:-1] == ea.error_cantidad_args(
                                           ea.Error.REQUIERE_UN_ARGUMENTO, 
                                           ea.Ayuda.CHECKOUT)

@pytest.mark.parametrize('comando', 
                         ['diff'])
@pytest.mark.parametrize('params', 
                         [[], ['parametro2']])
def test_entrada_comando_dos_parametros(monkeypatch: pytest.MonkeyPatch, 
                                       capsys: pytest.CaptureFixture[str],
                                       comando: str,
                                       params: list[str],
                                       test_args: list[str]) -> None:
    """
    Test para verificar manejo de errores en comandos
    que requieren dos parametros

    Args:
        monkeypatch(pytest.MonkeyPatch): Fixture para manejo de entorno
        capsys(pytest.CaptureFixture[str]): Fixture para capturar stdout
        test_args(list[str]): Fixture para simular argv
        comando(str): comando a probar
        params(list[str]): parametros para provocar errores 
    """
    test_args += [comando]
    test_args += params
    monkeypatch.setattr(sys, 'argv', test_args)
    leer_entrada()
    capture = capsys.readouterr()
    assert capture.out[:-1] == ea.error_cantidad_args(
                                   ea.Error.REQUIERE_DOS_ARGUMENTOS,
                                   ea.Ayuda.DIFF)
    
@pytest.mark.parametrize('comando', 
                         ['pc', 'ko', '-', '09a'])
@pytest.mark.parametrize('params', 
                         [[], ['parametro'], ['parametro2', 'parametro3']])
def test_entrada_comandos_no_reconocidos(monkeypatch: pytest.MonkeyPatch, 
                                         capsys: pytest.CaptureFixture[str],
                                         comando: str,
                                         params: list[str],
                                         test_args: list[str]) -> None:
    """
    Test para verificar manejo de errores cuando
    se intentan usar comandos no reconocidos

    Args:
        monkeypatch(pytest.MonkeyPatch): Fixture para manejo de entorno
        capsys(pytest.CaptureFixture[str]): Fixture para capturar stdout
        test_args(list[str]): Fixture para simular argv
        comando(str): comandos ficticios
        params(list[str]): parametros al azar
    """
    test_args += [comando]
    test_args += params
    monkeypatch.setattr(sys, 'argv', test_args)
    leer_entrada()
    capture = capsys.readouterr()
    assert capture.out[:-1] == ea.error_y_ayuda(
                                   ea.Error.COMANDO_NO_RECONOCIDO)
