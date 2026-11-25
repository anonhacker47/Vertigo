FROM --platform=$BUILDPLATFORM node:22-slim AS ui
WORKDIR /src/vertigo-ui
COPY vertigo-ui/package.json vertigo-ui/package-lock.json ./
RUN npm ci
COPY vertigo-ui/ ./
RUN npm run build


FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    VERTIGO_DATA_DIR=/data \
    USE_CORS=no
RUN apt-get update \
    && apt-get install -y --no-install-recommends webp \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY vertigo-backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY vertigo-backend/ .
COPY --from=ui /src/vertigo-backend/api/wwwroot ./api/wwwroot
RUN useradd --uid 1000 --create-home vertigo \
    && mkdir /data && chown vertigo:vertigo /data
USER vertigo
VOLUME /data
EXPOSE 6166
HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --start-interval=2s --retries=3 \
    CMD ["python", "-c", "import os, socket; socket.create_connection(('127.0.0.1', int(os.environ.get('VERTIGO_PORT') or 6166)), 3)"]
CMD ["python", "vertigo.py"]
