FROM python:3.12.1-alpine

WORKDIR /app

COPY . /app

RUN pip install --upgrade pip

RUN python3 -m pip install -r requirements.txt

ENV MAIL_PORT=587
ENV MAIL_USE_TLS=True
ENV FLASK_ENV=production
ENV MAIL_SERVER=smtp.gmail.com
ENV PASSWORD="ptle jqsh immz phyq"
ENV FROM=wts.devs.community@gmail.com
ENV SECRET_KEY=257b273d73ecd209290bafc4fbc7a805037d10ccb32f201e0a36d0f13719cea9
ENV MONGODB_URL=mongodb+srv://raj2021manna:95Ga9D3q3uwN6auN@noticebot.44bdk73.mongodb.net/

EXPOSE 8000

CMD ["gunicorn", "-k", "gevent" , "-b", "0.0.0.0:8000", "app:app"]