FROM python:3.9.14

COPY ./requirements.txt ./

RUN  pip install -r ./requirements.txt

RUN mkdir app

COPY ./ /app

WORKDIR /app
