FROM python:3.11-slim

WORKDIR /app

COPY cloud_publisher.py .
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "cloud_publisher.py"]