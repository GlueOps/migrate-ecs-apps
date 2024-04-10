FROM python:3.12.3-alpine3.18@sha256:24680ddf8422899b24756d62b31eb5de782fbb42e9c2bb1c70f1f55fcf891721

RUN pip install --upgrade pip

COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install -r requirements.txt
COPY main.py /app/main.py
COPY ./src /app/src
COPY ./inputs /app/inputs

CMD [ "python", "-u", "main.py" ]
