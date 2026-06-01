# Sistema Básico de Administración de Configuración(SBAC)

## Datos de la institución y asignatura

- Institución: UNAM - Facultad de Ciencias
- Carrera: Ciencias de la Computación
- Asignatura: Pruebas de Software y Administración de la Configuración
- Semestre: 2026-2

## Equipo de desarrollo

- Alatorre Méndez Sofía Guadalupe
- Badager Estrada Aaron Omar
- Cárdenas Torres Ernesto
- Solano Juárez Sebastián
- Vargas Herrera Eduardo

## Descripción del proyecto

Herramienta CLI en Python que versiona archivos, registra metadatos, marca líneas base y compara versiones; el detalle de uso está en [MANUAL_USUARIO.md](MANUAL_USUARIO.md).

## Instrucciones

### Instalar el SBAC
```bash
pip install --upgrade pip setuptools
pip install -e .
```
Otras formas de instalar (a nivel usuario, etc.): ver [MANUAL_USUARIO.md](MANUAL_USUARIO.md).

Para ejecutar con Docker: ver [INSTRUCCIONES_DOCKER.md](INSTRUCCIONES_DOCKER.md).

### Verificar la instalación

```bash
sbac --help
```

Si la instalación fue correcta, se mostrará la ayuda con la lista de comandos disponibles.

### Ejecutar las pruebas

Requiere haber instalado el paquete antes (`pip install -e .`).

```bash
pytest                                              # toda la suite
pytest --cov=src/sbac --cov-report=term-missing     # con cobertura
```