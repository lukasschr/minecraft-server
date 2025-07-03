FROM python:3.12.10-alpine

WORKDIR /app

COPY configs /app
COPY requirements.txt /app
COPY src /app/src

COPY services/remote_storage_backups /app

RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["python", "main.py"]