FROM python:3.12-alpine

RUN apk add --no-cache \
    git \
    openssh \
    docker-cli \
    docker-cli-compose

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY agent.py .

CMD ["python", "agent.py"]
