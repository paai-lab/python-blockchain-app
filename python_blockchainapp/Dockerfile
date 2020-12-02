FROM python:3.7

LABEL maintainer="ghksdl6025@gmail.com"

WORKDIR /app

#Install dependencies
COPY . /app

RUN cd /app && pip3 install -r requirements.txt

EXPOSE 5000

