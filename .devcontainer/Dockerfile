FROM python:3.13.1-slim-bookworm

COPY ./requirements.txt .
RUN pip install -r ./requirements.txt
RUN rm ./requirements.txt

RUN useradd python -m

WORKDIR /home/python/data

COPY . .