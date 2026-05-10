FROM python:3.13-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    git-lfs \
    ffmpeg \
    libsm6 \
    libxext6 \
    cmake \
    rsync \
    libgl1 \
    && rm -rf /var/lib/apt/lists/* \
    && git lfs install

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create user directory
RUN mkdir -p /home/user && \
    ( [ -e /home/user/app ] || ln -s /app/ /home/user/app ) || true

# Expose port
EXPOSE 7860

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
