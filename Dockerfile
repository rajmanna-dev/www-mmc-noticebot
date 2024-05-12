FROM python:3.12.1-alpine

WORKDIR /app

COPY . /app

RUN python3 -m pip install -r requirements.txt

EXPOSE 8080

CMD ["gunicorn", "-w", "4" ,"--bind", "0.0.0.0:8080", "app:app"]