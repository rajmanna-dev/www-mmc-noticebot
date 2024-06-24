FROM python:3.12.1-alpine

WORKDIR /app

RUN apk update && \
    apk add --no-cache supervisor nginx curl && \
    pip install --upgrade pip

COPY . /app
COPY nginx.conf /etc/nginx/nginx.conf

COPY supervisord_app.conf /etc/supervisor/conf.d/supervisord_app.conf
COPY supervisord_bot.conf /etc/supervisor/conf.d/supervisord_bot.conf

RUN pip install -r requirements.txt

ENV MAIL_PORT=XXX
ENV MAIL_USE_TLS=XXX
ENV FLASK_ENV=XXX
ENV MAIL_SERVER=XXX
ENV EMAIL_PASSWORD=XXX
ENV FROM_EMAIL=XXX
ENV SECRET_KEY=XXX
ENV MONGODB_URL=XXX
ENV DOMAIN=XXX
ENV NOTICE_URL=XXX

EXPOSE 80
EXPOSE 8000

CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord_app.conf"]
