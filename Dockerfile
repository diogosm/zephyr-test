FROM python:3.9-slim-buster

RUN apt-get update \
        && DEBIAN_FRONTEND=noninteractive; \
        apt-get install -y libaio1 wget unzip; 

RUN apt-get install -y gcc

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

## copia tudo para o workdir do /app
COPY . .

EXPOSE 5000
CMD ["gunicorn", "--workers=2", "--timeout=90", "--worker-class=gevent", "--threads=3", "--bind=0.0.0.0:5000", "main:app"]
