FROM python:3.7-stretch

WORKDIR /home/api

RUN apt-get update

COPY requirements.txt .
RUN pip3 install -r /home/api/requirements.txt

CMD python3 ./init.py
CMD python3 ./app.py