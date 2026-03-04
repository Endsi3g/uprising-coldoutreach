# Multi-stage Dockerfile for Uprising ColdOutreach

# Stage 1: Build Frontend
FROM node:20-slim AS frontend-builder
WORKDIR /app/prospectai
COPY prospectai/package*.json ./
RUN npm install
COPY prospectai/ ./
RUN npm run build

# Stage 2: Backend & Final Image
FROM python:3.11-slim
WORKDIR /app

# Install system dependencies for Playwright and PostgreSQL
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers (optional, comment out if not using local browsers)
RUN playwright install chromium --with-deps

# Copy Backend Source
COPY app/ ./app/
COPY .env .env

# Copy Built Frontend from Stage 1
COPY --from=frontend-builder /app/prospectai/dist ./prospectai/dist

# Expose port
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Start Application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
