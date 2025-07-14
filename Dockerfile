# Dockerfile

# --- Stage 1: Base image with all dependencies installed ---
FROM python:3.10-slim AS base

WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# Upgrade pip
RUN pip install --upgrade pip

# Copy only the requirements file first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
# This is the slow step that will be cached
RUN pip install --no-cache-dir -r requirements.txt

# --- Stage 2: Final image with application code ---
FROM python:3.10-slim AS final

WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# Copy installed packages from the base stage
COPY --from=base /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=base /usr/local/bin /usr/local/bin

# Copy the rest of the application code
COPY . .