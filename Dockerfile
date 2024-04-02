# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster

WORKDIR /python-docker

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

ENV STEAM_KEY=<API_URL>
ENV WEB_URL=<API_URL>

CMD [ "python3", "app.py" ]