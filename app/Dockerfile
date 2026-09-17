# ------------------------------------------------------------------
# Multi-stage build.
#
# Stage 1 ("builder") installs dependencies — including any that need
# compilers — into an isolated location.
# Stage 2 (runtime) copies ONLY the installed packages and the app
# code onto a slim base: no pip cache, no build tools, smaller and
# safer image.
# ------------------------------------------------------------------

# ---------- Stage 1: builder ----------
FROM python:3.12-slim AS builder

WORKDIR /build

# Copy requirements alone first: Docker caches layers, so as long as
# requirements.txt is unchanged, rebuilds skip the pip install entirely.
COPY requirements.txt .

RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ---------- Stage 2: runtime ----------
FROM python:3.12-slim

# Run as a non-root user — container-security table stakes.
RUN groupadd --system appgroup && useradd --system --gid appgroup appuser

WORKDIR /app

# Bring in the installed packages from the builder stage, then the code.
COPY --from=builder /install /usr/local
COPY main.py .

USER appuser

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]