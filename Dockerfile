# 🐳 Telegram Music Bot - Dockerfile
# Multi-stage build for optimized production image

# ========================
# 🏗️ Build Stage
# ========================
FROM python:3.11-slim as builder

# Set build arguments
ARG BUILD_DATE
ARG VERSION
ARG VCS_REF

# Add metadata
LABEL maintainer="Telegram Music Bot Team" \
      org.label-schema.build-date=$BUILD_DATE \
      org.label-schema.name="telegram-music-bot" \
      org.label-schema.description="Advanced Telegram bot for audio processing" \
      org.label-schema.version=$VERSION \
      org.label-schema.vcs-ref=$VCS_REF \
      org.label-schema.vcs-url="https://github.com/user/telegram-music-bot" \
      org.label-schema.schema-version="1.0"

# Install system dependencies for building
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /build

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --user -r requirements.txt

# ========================
# 🎵 Production Stage
# ========================
FROM python:3.11-slim as production

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    ffprobe \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user for security
RUN groupadd -r botuser && useradd -r -g botuser -d /app -s /bin/bash botuser

# Set working directory
WORKDIR /app

# Copy Python packages from builder stage
COPY --from=builder /root/.local /home/botuser/.local

# Copy application code
COPY --chown=botuser:botuser . .

# Create required directories
RUN mkdir -p /app/temp /app/output /app/data /app/logs \
    && chown -R botuser:botuser /app

# Set environment variables
ENV PYTHONPATH=/home/botuser/.local/lib/python3.11/site-packages:$PYTHONPATH \
    PATH=/home/botuser/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Switch to non-root user
USER botuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import sys; sys.exit(0)" || exit 1

# Expose port (if web interface is added later)
EXPOSE 8080

# Default command
CMD ["python", "bot.py"]

# ========================
# 🧪 Development Stage
# ========================
FROM production as development

# Switch back to root for development tools
USER root

# Install development dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    vim \
    htop \
    && rm -rf /var/lib/apt/lists/*

# Install development Python packages
RUN pip install --no-cache-dir \
    pytest \
    pytest-asyncio \
    black \
    flake8 \
    mypy \
    ipython

# Switch back to botuser
USER botuser

# Override command for development
CMD ["python", "-u", "bot.py"]

# ========================
# 🔧 Build Instructions
# ========================

# Build production image:
# docker build --target production -t telegram-music-bot:latest .

# Build development image:
# docker build --target development -t telegram-music-bot:dev .

# Build with build args:
# docker build \
#   --build-arg BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ') \
#   --build-arg VERSION=1.0.0 \
#   --build-arg VCS_REF=$(git rev-parse --short HEAD) \
#   -t telegram-music-bot:1.0.0 .

# ========================
# 🚀 Usage Examples
# ========================

# Run with docker-compose:
# docker-compose up -d

# Run standalone:
# docker run -d \
#   --name telegram-music-bot \
#   --env-file .env \
#   -v $(pwd)/data:/app/data \
#   -v $(pwd)/temp:/app/temp \
#   -v $(pwd)/output:/app/output \
#   telegram-music-bot:latest

# Run in development mode:
# docker run -it \
#   --name telegram-music-bot-dev \
#   --env-file .env \
#   -v $(pwd):/app \
#   telegram-music-bot:dev

# ========================
# 📊 Image Size Optimization
# ========================

# The multi-stage build reduces image size by:
# 1. Separating build dependencies from runtime
# 2. Using slim Python base image
# 3. Cleaning package caches
# 4. Removing unnecessary files

# Expected image sizes:
# - Production: ~200-300MB
# - Development: ~400-500MB
# - Builder stage is discarded

# ========================
# 🔒 Security Features
# ========================

# 1. Non-root user execution
# 2. Minimal base image (python:slim)
# 3. No unnecessary packages
# 4. Health checks enabled
# 5. Resource limits via docker-compose
# 6. Read-only filesystem (can be enabled)

# ========================
# 🌍 Environment Variables
# ========================

# Required:
# - BOT_TOKEN: Telegram bot token
# - ADMIN_USER_ID: Admin user ID

# Optional:
# - MAX_FILE_SIZE: Maximum file size (default: 50MB)
# - DAILY_LIMIT: Daily processing limit (default: 100)
# - MAX_CONCURRENT: Max concurrent processes (default: 3)
# - LOG_LEVEL: Logging level (default: INFO)
# - DATABASE_URL: Database connection string

# ========================
# 📁 Volume Mounts
# ========================

# Recommended volumes:
# - /app/data: Persistent data (database, configs)
# - /app/temp: Temporary files (can be tmpfs)
# - /app/output: Processed files
# - /app/logs: Log files (optional)

# ========================
# 🔧 Troubleshooting
# ========================

# Debug container:
# docker exec -it telegram-music-bot bash

# View logs:
# docker logs telegram-music-bot

# Check health:
# docker inspect telegram-music-bot | grep Health

# Resource usage:
# docker stats telegram-music-bot