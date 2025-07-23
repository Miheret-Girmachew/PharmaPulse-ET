# Dockerfile (Improved and Final Version)

# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Install a comprehensive set of system dependencies for OpenCV and other libraries.
# This prevents multiple "missing .so file" errors.
# - libgl1-mesa-glx: Provides libGL.so.1 (the first missing library).
# - libglib2.0-0: Provides libgthread-2.0.so.0 (the second missing library).
# - libsm6, libxext6: Common X11 libraries that OpenCV may need stubs for.
# - ffmpeg: A powerful library for video/audio processing.
# - rm -rf /var/lib/apt/lists/*: Cleans up the apt cache to keep the final image size smaller.
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy only the requirements file first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Now, copy the rest of the application's code
COPY . .

# Expose ports
EXPOSE 8000
EXPOSE 3000

# The command to run is specified in docker-compose.yml,
# this is just a fallback.
CMD ["dagster", "dev"]