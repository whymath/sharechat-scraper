FROM python:3.8.1-buster
COPY . /app
WORKDIR /app
ENV FLASK_APP=server.py
RUN pip install -r requirements.txt
RUN pip install flask
EXPOSE 5000 
CMD flask run