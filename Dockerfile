FROM python:3.6

RUN apt-get update

RUN apt-get install -y rsyslog
RUN apt-get install -y vim
RUN apt-get install -y cron
RUN apt-get install -y ffmpeg
RUN touch /app/syscronscrape.log
RUN service rsyslog start
RUN service cron start

COPY . /app
WORKDIR /app
ARG flask_app=server.py
ENV FLASK_APP=$flask_app
RUN pip install virtualenv
RUN pip install -r requirements.txt
EXPOSE 80

CMD ["gunicorn", "-b", "0.0.0.0:80", "--log-file=-" , "--workers=2", "--threads=4", "--worker-class=gthread" ,"server:app", "--reload"]