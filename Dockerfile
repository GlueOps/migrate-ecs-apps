FROM python:3.12.2-alpine3.18@sha256:3a8e2cf5d2d128b6f14a7e73fdeff30109ace32a67d39ba477ef181f89d1fc57

RUN pip install --upgrade pip

COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install -r requirements.txt
COPY main.py /app/main.py
COPY ./src /app/src
COPY ./inputs /app/inputs

CMD [ "python", "-u", "main.py" ]
