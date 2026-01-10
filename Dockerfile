# Stage 1: Build React frontend
FROM node:22-alpine AS frontend-builder

WORKDIR /app

# Install dependencies
COPY package.json package-lock.json ./
RUN npm ci

# Copy source and build
COPY src/ ./src/
COPY index.html vite.config.js postcss.config.js tailwind.config.js eslint.config.js ./
COPY public/ ./public/

RUN npm run build

# Stage 2: Python/Django production
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Django project
COPY config/ ./config/
COPY support_board/ ./support_board/
COPY manage.py ./

# Copy built frontend from Stage 1
COPY --from=frontend-builder /app/support_board/static/support_board ./support_board/static/support_board

# Collect static files
RUN python manage.py collectstatic --noinput || true

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "config.wsgi:application"]
