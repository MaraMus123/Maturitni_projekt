FROM python:3.9-slim
LABEL maintainer="Markos-Maturita"

ENV PYTHONUNBUFFERED=1

COPY requirements.txt /tmp/requirements.txt

WORKDIR /app

RUN pip install --no-cache-dir -r /tmp/requirements.txt && \
    apt-get update && \
    apt-get install -y postgresql-client


COPY ./app /app

CMD ["python", "script.py"]
