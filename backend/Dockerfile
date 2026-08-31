FROM python:3.12-slim

WORKDIR /app

# WeasyPrint (servicio de informes PDF) necesita estas librerias de sistema
# para renderizar HTML/CSS a PDF -- no alcanza con pip install.
# Nota: desde WeasyPrint 53 el motor de render es propio (pydyf), ya no usa
# cairo ni gdk-pixbuf -- por eso NO estan en esta lista (en Debian trixie,
# que usa esta imagen base, esos paquetes viejos ni siquiera existen mas).
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libharfbuzz-subset0 \
    fontconfig \
    fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
