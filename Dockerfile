FROM python:3.8.1-alpine3.11
RUN apk add gcc
RUN apk add linux-headers
RUN apk add --update alpine-sdk
RUN apk add libffi-dev
COPY . /app
WORKDIR /app
ENV FLASK_APP=server.py
RUN pip install -r requirements.txt
RUN pip install flask
EXPOSE 5000 
CMD flask run