FROM python:3.12-alpine

RUN apk add --no-cache \
    git \
    openssh \
    docker-cli \
    docker-cli-compose \
    bash

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "-m", "main"]
