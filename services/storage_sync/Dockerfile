FROM python:3.12.10-alpine

WORKDIR /app

COPY services/storage_sync /app

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "storage_sync_daemon.py"]