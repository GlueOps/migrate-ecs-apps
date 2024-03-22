FROM python:3.12.2-alpine3.18@sha256:b7a2a34021c40b197c129712a86c03fc7933e470e20fa0f1ab6509926fcc6054

RUN pip install --upgrade pip

COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install -r requirements.txt
COPY main.py /app/main.py
COPY ./src /app/src
COPY ./inputs /app/inputs

CMD [ "python", "-u", "main.py" ]
