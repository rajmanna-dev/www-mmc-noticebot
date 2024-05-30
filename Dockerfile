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

ENV MAIL_PORT=465
ENV MAIL_USE_TLS=True
ENV FLASK_ENV=production
ENV MAIL_SERVER=smtp.gmail.com
ENV PASSWORD="ptle jqsh immz phyq"
ENV FROM=wts.devs.community@gmail.com
ENV SECRET_KEY=257b273d73ecd209290bafc4fbc7a805037d10ccb32f201e0a36d0f13719cea9
ENV MONGODB_URL=mongodb+srv://raj2021manna:95Ga9D3q3uwN6auN@noticebot.44bdk73.mongodb.net/
ENV DOMAIN=http://www.mmccollege.co.in
ENV NOTICE_URL=http://www.mmccollege.co.in/NoticePage/Student%20Notice

EXPOSE 80
EXPOSE 8000

CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord_app.conf"]
