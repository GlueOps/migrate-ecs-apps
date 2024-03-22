FROM python:3.11.8-alpine3.18@sha256:b3f5c8df67b7519eaf2ae4230482a65ef95ffa3a50cb27fbd1db3d8a73d88ee2

RUN pip install --upgrade pip

COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install -r requirements.txt
COPY main.py /app/main.py
COPY ./src /app/src
COPY ./inputs /app/inputs

CMD [ "python", "-u", "main.py" ]
