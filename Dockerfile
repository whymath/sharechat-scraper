FROM python:3.6

RUN apt-get update && apt-get -y install vim

COPY . /app
WORKDIR /app
ARG flask_app=application.py
ENV FLASK_APP=$flask_app
RUN pip install virtualenv
RUN pip install -r requirements.txt
EXPOSE 80

CMD ["gunicorn", "-b", "0.0.0.0:80", "--log-file=-" , "--workers=2", "--threads=4", "--worker-class=gthread" ,"server:app", "--reload"]