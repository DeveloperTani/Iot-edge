FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install only what's needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libssl-dev \
    ca-certificates \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# Copy app code
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# Default command
CMD ["python", "-u", "thermostat_reader.py"]
