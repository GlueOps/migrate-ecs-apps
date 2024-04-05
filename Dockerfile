FROM python:3.11.9-alpine3.18@sha256:4799cdc47a1b7ecc2829e71e74d06ce7c0af54dec4f5ff139f869cc2c4283b1d

RUN pip install --upgrade pip

COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install -r requirements.txt
COPY main.py /app/main.py
COPY ./src /app/src
COPY ./inputs /app/inputs

CMD [ "python", "-u", "main.py" ]
