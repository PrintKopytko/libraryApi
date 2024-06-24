FROM python:3.10.14-slim-bookworm

WORKDIR /usr/src/app


RUN pip install --upgrade pip
COPY ./libraryapi/requirements.txt /usr/src/app/requirements.txt
RUN pip install -r requirements.txt

# copy project
COPY ./libraryapi /usr/src/app/libraryapi