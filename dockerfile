FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

COPY . .

# Expose port used by Gunicorn
EXPOSE 8080

# For Postgres, ensure DATABASE_URL env var is set in your deployment
CMD ["gunicorn", "-w", "3", "-b", "0.0.0.0:8080", "app:app"]