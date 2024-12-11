FROM python:3.10-slim

#Flask env variables
ENV FLASK_RUN_HOST=0.0.0.0 \
    FLASK_RUN_PORT=5000

WORKDIR /STOCK_APP

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

COPY .env /app/.env

EXPOSE 5000

CMD ["flask", "run"]