FROM python:3.12.1-alpine

WORKDIR /app

COPY . /app

RUN python3 -m pip install -r requirements.txt

EXPOSE 5000

CMD python ./app.py