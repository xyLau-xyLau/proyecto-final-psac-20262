FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 1. Instalacion del codigo de SBAC (vive en /app dentro del contenedor)
WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip setuptools \
    && pip install --no-cache-dir -r requirements.txt

# Se copia el resto del proyecto y se instala el paquete.
# Al instalar el paquete, pip crea el ejecutable de consola "sbac"
# (definido en pyproject.toml -> [project.scripts]).
COPY pyproject.toml README.md ./
COPY src/ ./src/
COPY tests/ ./tests/
RUN pip install --no-cache-dir .

# 2. Directorio de trabajo del usuario
# SBAC opera sobre el directorio actual (crea ahi la carpeta .sbac/).
# /workspace es el punto donde el usuario montara su proyecto como volumen.
WORKDIR /workspace

# 3. Punto de entrada
# Con ENTRYPOINT "sbac", cualquier argumento que se pase a "docker run"
# se interpreta como un subcomando de sbac. Ejemplo:
#   docker run ... sbac-img status   ->  ejecuta "sbac status"
# Sin argumentos, muestra la ayuda.
ENTRYPOINT ["sbac"]
CMD ["--help"]
