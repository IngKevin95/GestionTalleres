FROM python:3.11-slim

WORKDIR /

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./
COPY pyproject.toml .
COPY init_db.py .

RUN mkdir -p /logs

ENV PYTHONPATH=/app

EXPOSE 8000

CMD ["uvicorn", "app.drivers.api.main:app", "--host", "0.0.0.0", "--port", "8000"]

