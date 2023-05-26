FROM python:3.7-slim

WORKDIR /app

COPY requirements.txt .


RUN apt-get update && apt-get upgrade -y && \
     pip install -r requirements.txt && pip install --upgrade pip

COPY . .


CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000" ]