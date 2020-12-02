FROM python:3.7

LABEL maintainer="ghksdl6025@gmail.com"

COPY . /app

WORKDIR /app

#Install dependencies

RUN cd /app && pip3 install -r requirements.txt

EXPOSE 5000

RUN ["chmod", "+x", "./flaskapp.sh"]


# ENTRYPOINT python run_app.py
