# Manual de Usuario SBAC

**Sistema Básico de Administración de Configuración**

---

## 1. ¿Qué es SBAC?

SBAC es una herramienta de línea de comandos escrita en Python que implementa, a pequeña escala, los conceptos fundamentales de la administración de la configuración: versionar archivos, registrar metadatos de cada cambio, marcar líneas base y comparar versiones entre sí.

No pretende reemplazar a Git; su objetivo es **demostrar de forma práctica** los procesos de identificación, control, registro y comparación de elementos de configuración.

Toda la información del repositorio se guarda en una carpeta oculta `.sbac/` dentro de tu proyecto, de modo que no interfiere con tus archivos de trabajo.

---

## 2. Requisitos previos

- **Python 3.10 o superior** (se usan características modernas como `match`/`case`).
- **pip** (gestor de paquetes de Python).
- Sistema operativo: probado en **Linux (Ubuntu)**.
- Opcional: **Docker**, si prefieres ejecutarlo en un contenedor.

Verifica tu versión de Python:

```bash
python3 --version
```

---

## 3. Formas de instalar SBAC

SBAC se distribuye como un paquete de Python con un *comando de consola* llamado `sbac`.
Al instalarlo, pip crea un ejecutable `sbac` y lo coloca en una carpeta `bin/`. **De qué carpeta `bin/` se trate determina si el comando estará disponible siempre o solo dentro de un entorno virtual.** A continuación se explican las distintas formas, de la más aislada a la más global.

> En todos los casos, los comandos se ejecutan desde la raíz del proyecto (la carpeta que
> contiene `pyproject.toml`).

### 3.1. Opción A. Entorno virtual (recomendada para desarrollo)

Aísla las dependencias del proyecto del resto del sistema. **El comando `sbac` solo estará disponible mientras el entorno esté activado.**

```bash
# 1. Crear el entorno virtual
python3 -m venv .venv

# 2. Activarlo
source .venv/bin/activate

# 3. Instalar SBAC en modo editable
pip install --upgrade pip setuptools
pip install -e .
```

A partir de aquí, `sbac` funciona en cualquier carpeta **mientras veas `(.venv)` al inicio de tu prompt**. Para salir del entorno:

```bash
deactivate
```

> **Importante:** si instalas dentro del entorno virtual, el ejecutable queda en
> `.venv/bin/sbac`, que solo se agrega a tu `PATH` al activar el entorno. Por eso, al
> desactivarlo, el comando "desaparece". Esto es normal y esperado.

### 3.2. Opción B: Instalación a nivel usuario (comando global, sin activar nada)

Si quieres que `sbac` esté disponible **siempre**, desde cualquier carpeta y sin activar ningún entorno, instálalo a nivel usuario (fuera de cualquier venv):

```bash
deactivate                    # asegúrate de NO estar en un venv
pip install --user -e .
```

El ejecutable queda en `~/.local/bin/sbac`, que normalmente ya está en tu `PATH` en Ubuntu.
Si el sistema no encuentra el comando, agrega esta línea a tu `~/.bashrc` y reinicia la terminal:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

### 3.3. Opción C: Docker (entorno reproducible, sin tocar tu sistema)

Ver [INSTRUCCIONES_DOCKER.md](INSTRUCCIONES_DOCKER.md).

## 4. Verificar la instalación

Ejecuta:

```bash
sbac --help
```

Si la instalación fue correcta, verás la lista de comandos disponibles. También puedes usar `sbac -h`. Si no ves nada o aparece *"command not found"*, revisa la sección 6 (Solución de problemas).

---

## 5. Guía de comandos

Estructura general:

```bash
sbac <comando> [argumentos]
```

| Comando | Argumentos | Descripción |
|---|---|---|
| `init` | - | Inicializa un repositorio SBAC en el directorio actual. |
| `add` | `<archivo>` \| `.` \| `<directorio>` | Añade archivos al seguimiento. |
| `rm` | `<archivo>` | Quita un archivo del seguimiento (no lo borra del disco). |
| `status` | - | Muestra el estado actual del repositorio. |
| `commit` | `"<mensaje>"` | Registra una nueva versión de los archivos rastreados. |
| `history` | - | Muestra el historial de versiones en orden cronológico. |
| `baseline` | `"<nombre>"` | Marca la versión actual como línea base. |
| `list-baselines` | - | Lista las líneas base registradas. |
| `diff` | `<v1> <v2>` | Muestra las diferencias entre dos versiones. |
| `checkout` | `<versión>` | Restaura el repositorio al estado de una versión. |
| `--help`, `-h` | - | Muestra la ayuda general. |

### 5.1. `sbac init`

Crea la estructura interna del repositorio (`.sbac/` con `versions/`, `baselines/`, `config.json` y `tracked-files`).

```bash
sbac init
# Repositorio SBAC inicializado en .sbac/
```

### 5.2. `sbac add <archivo>`

Registra archivos para que el repositorio los rastree. Acepta tres formas:

```bash
sbac add main.py          # un archivo específico
sbac add src/             # todos los archivos de un directorio (recursivo)
sbac add .                # todos los archivos del directorio actual
```

### 5.3. `sbac rm <archivo>`

Deja de rastrear un archivo. **No lo elimina** de tu carpeta de trabajo.

```bash
sbac rm main.py
# "main.py" eliminado del seguimiento
```

### 5.4. `sbac status`

Muestra qué archivos están modificados, eliminados, sin cambios o sin seguimiento, así como la versión actual.

```bash
sbac status
```

### 5.5. `sbac commit "mensaje"`

Crea una nueva versión con los archivos rastreados y guarda sus metadatos (id, versión padre, fecha, autor y mensaje). El mensaje debe ir **entre comillas**.

```bash
sbac commit "Primera versión estable"
# Versión v1 registrada: "Primera versión estable"
```

Las versiones se identifican secuencialmente: `v1`, `v2`, `v3`, ...

### 5.6. `sbac history`

Lista todas las versiones en orden cronológico, con su id, fecha, autor y mensaje.

```bash
sbac history
```

### 5.7. `sbac baseline "nombre"`

Marca la versión actual como una línea base con un nombre identificador (por ejemplo, una entrega estable).

```bash
sbac baseline "entrega-1"
# Línea base "entrega-1" creada sobre versión v1
```

### 5.8. `sbac list-baselines`

Muestra las líneas base registradas y la versión asociada a cada una.

```bash
sbac list-baselines
```

### 5.9. `sbac diff <v1> <v2>`

Compara dos versiones línea por línea y muestra las diferencias.

```bash
sbac diff v1 v2
```

### 5.10. `sbac checkout <versión>`

Restaura los archivos del proyecto al estado de una versión específica.

```bash
sbac checkout v1
# Repositorio restaurado a la versión v1
```

---

## 6. Ejemplo de flujo de trabajo completo

```bash
# 1. Crear una carpeta de prueba e inicializar
mkdir mi-proyecto && cd mi-proyecto
sbac init

# 2. Crear un archivo y añadirlo al seguimiento
echo "print('hola')" > app.py
sbac add app.py

# 3. Registrar la primera versión
sbac commit "Versión inicial"

# 4. Hacer un cambio y registrar otra versión
echo "print('adios')" >> app.py
sbac commit "Agrego despedida"

# 5. Ver el historial
sbac history

# 6. Comparar las dos versiones
sbac diff v1 v2

# 7. Marcar la versión actual como línea base
sbac baseline "estable"
sbac list-baselines

# 8. Volver a la primera versión
sbac checkout v1
```

---

## 7. Solución de problemas

| Síntoma | Causa probable | Solución |
|---|---|---|
| `sbac: command not found` | El ejecutable no está en tu `PATH` (instalaste dentro de un venv que ahora está desactivado). | Activa el venv (`source .venv/bin/activate`) o instala a nivel usuario. |
| Funciona solo con el venv activado | El comando quedó en `.venv/bin/`. | Es el comportamiento normal del venv. Usa `pip install --user -e .` si lo quieres global. |
| `No module named 'sbac'` al usar `pytest` | El paquete no está instalado en el entorno actual. | Ejecuta `pip install -e .` antes de correr las pruebas. |
| `No se encontró un repositorio SBAC...` | No ejecutaste `sbac init` en esa carpeta. | Corre `sbac init` primero. |

Diagnóstico rápido de dónde está instalado el comando:

```bash
which sbac        # ruta del ejecutable en uso
pip show -f sbac  # ubicación del paquete y del script
```

---

## 8. Desinstalar

```bash
pip uninstall sbac
```

Para eliminar un repositorio SBAC de una carpeta, basta con borrar la carpeta oculta:

```bash
rm -rf .sbac
```

---

## 9. Mensajes de error comunes

SBAC responde con mensajes claros en español ante situaciones inválidas. Algunos ejemplos:

- *"El repositorio SBAC ya está inicializado en este directorio"*: intentaste `init`
  donde ya existe `.sbac/`.
- *"No se encontró un repositorio SBAC en este directorio. Ejecuta 'sbac init' primero"*:
  ejecutaste un comando sin haber inicializado.
- *"El mensaje del commit no puede estar vacío"*: hiciste `commit` sin mensaje.
- *"No hay archivos bajo seguimiento. Usa 'sbac add <archivo>' antes de hacer commit"*:
  intentaste versionar sin archivos rastreados.
- *"No hay cambios para commitear"*: no hubo modificaciones desde la última versión.
