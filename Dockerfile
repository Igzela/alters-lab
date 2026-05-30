# ── Stage 1: Build frontend ──────────────────────────────────────
FROM node:22-slim AS frontend

WORKDIR /build
COPY apps/web/package.json apps/web/package-lock.json* ./
RUN npm ci --ignore-scripts
COPY apps/web/ ./
RUN npm run build

# ── Stage 2: Runtime ────────────────────────────────────────────
FROM python:3.11-slim

LABEL org.opencontainers.image.title="Alters Lab"
LABEL org.opencontainers.image.description="Personal future-path simulation and calibration system"
LABEL org.opencontainers.image.source="https://github.com/Igzela/alters-lab"
LABEL org.opencontainers.image.licenses="MIT"

WORKDIR /opt/alters-lab

# Install Python dependencies
COPY apps/api/pyproject.toml ./
RUN pip install --no-cache-dir . 2>/dev/null || true

COPY apps/api/ ./
RUN pip install --no-cache-dir .

# Copy frontend build output
COPY --from=frontend /build/dist ./web/dist

# Copy sample data and config templates for first-run initialization
COPY alters/sample/ ./alters/sample/
COPY alters/product/config/ ./alters/product/config/

# Entrypoint script
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# Use /data as HOME so XDG paths land in the volume:
#   ~/.config/alters-lab → /data/.config/alters-lab
#   ~/.local/share/alters-lab → /data/.local/share/alters-lab
#   ~/.local/state/alters-lab → /data/.local/state/alters-lab
ENV HOME=/data
ENV ALTERS_LAB_MODE=packaged
ENV ALTERS_LAB_APP_ROOT=/opt/alters-lab
ENV PYTHONPATH=/opt/alters-lab/src

EXPOSE 18790

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["python", "-m", "uvicorn", "alters_lab.main:app", "--host", "0.0.0.0", "--port", "18790"]
