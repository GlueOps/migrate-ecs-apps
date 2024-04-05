FROM python:3.11.6-alpine3.18@sha256:64bf6d40f8bbb4f7565642494bb267aa92f1ce1beade6c1a8a3581688abf7a52

RUN pip install --upgrade pip

COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install -r requirements.txt
COPY main.py /app/main.py
COPY ./src /app/src
COPY ./inputs /app/inputs

CMD [ "python", "-u", "main.py" ]
