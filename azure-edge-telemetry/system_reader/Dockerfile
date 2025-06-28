FROM python:3.11-slim

WORKDIR /app
COPY /system_reader.py .
COPY /requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "system_reader.py"]