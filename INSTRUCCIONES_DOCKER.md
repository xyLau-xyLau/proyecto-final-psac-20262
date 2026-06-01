# Instrucciones SBAC con Docker

Estos pasos empaquetan y ejecutan SBAC en un contenedor, sin depender del Python local de tu máquina. Cumple la política **PD-001** (uso de contenedores) y el requisito de containerización del proyecto.

## Archivos incluidos

- **`Dockerfile`**: receta para construir la imagen.
- **`.dockerignore`**: evita copiar basura (`.git`, `.venv`, cachés…) a la imagen.

---

## 1. Construir la imagen

Desde la raíz del proyecto:

```bash
docker build -t sbac .
```

Esto crea una imagen llamada `sbac`. Solo necesitas reconstruir cuando cambie el código fuente.

---

## 2. Usar SBAC sobre tu proyecto

SBAC trabaja sobre el **directorio actual** (ahí crea la carpeta `.sbac/`). Para que el contenedor vea y modifique tus archivos, se monta tu carpeta de trabajo como un volumen en `/workspace`.

La forma cómoda es definir un alias:

```bash
alias sbac='docker run --rm -it -v "$(pwd)":/workspace sbac'
```

A partir de ahí, lo usas como si estuviera instalado de forma nativa:

```bash
sbac init
sbac add .
sbac commit "Version inicial"
sbac history
sbac diff v1 v2
```

Sin alias, el comando completo es:

```bash
docker run --rm -it -v "$(pwd)":/workspace sbac status
```

Desglose de las opciones:

| Opción | Para qué sirve |
|---|---|
| `--rm` | Borra el contenedor al terminar (no deja basura). |
| `-it` | Modo interactivo (útil para ver bien la salida). |
| `-v "$(pwd)":/workspace` | Monta tu carpeta actual dentro del contenedor. |
| `sbac` | Nombre de la imagen. |
| `status` (o el comando que sea) | Se pasa como argumento a `sbac`. |

> **Tip — autor de los commits:** SBAC toma el autor de la variable `USER`. Dentro
> del contenedor suele venir vacía (queda como `desconocido`). Para fijarlo:
> ```bash
> docker run --rm -it -e USER=tu_nombre -v "$(pwd)":/workspace sbac commit "msg"
> ```

---

## 3. Ejecutar las pruebas dentro del contenedor

La imagen también incluye la carpeta `tests/` y `pytest`. Para correr la suite:

```bash
docker run --rm --entrypoint pytest sbac /app/tests -v
```

Con cobertura:

```bash
docker run --rm --entrypoint pytest sbac /app/tests --cov=/app/src/sbac --cov-report=term-missing
```

---

## 4. Comandos útiles de mantenimiento

```bash
docker images | grep sbac         # ver la imagen
docker build --no-cache -t sbac . # reconstruir desde cero
docker rmi sbac                   # borrar la imagen
```

---

## Resumen rápido

```bash
# 1. Construir (una vez)
docker build -t sbac .

# 2. Crear alias (por sesión de terminal)
alias sbac='docker run --rm -it -v "$(pwd)":/workspace sbac'

# 3. Usar
sbac init
sbac add .
sbac commit "Mi primera version"
sbac history
```
