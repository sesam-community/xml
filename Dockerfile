FROM python:3.9-alpine3.15
LABEL author="Endre Brønnum"
LABEL author.email="endre.bronnum@sesam.io"

RUN apk update
RUN apk add openssl-dev libffi-dev musl-dev gcc make

RUN pip install --upgrade pip

COPY ./service/requirements.txt /service/requirements.txt
RUN pip install -r /service/requirements.txt
COPY ./service /service

EXPOSE 5000/tcp

CMD ["python3", "-u", "./service/service.py"]