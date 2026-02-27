FROM python:3.10-slim

# Prevent Python from buffering logs
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install system deps (for httpx / rich if needed)
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install python deps
RUN pip install --no-cache-dir -r requirements.txt

# Default command
ENTRYPOINT ["python", "cli.py"]