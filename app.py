import yfinance as yf
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import requests
import io
import os

from flask import Flask, request, render_template, send_file, jsonify
from datetime import datetime
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv


app = Flask(__name__)

load_dotenv()


def exists(asset: str) -> bool:

    if not asset.isalpha():
        return False
    
    try:
        ticker = yf.Ticker(asset)
        info = ticker.info
        if "symbol" in info and info["symbol"] == asset:
            return True
        
    except Exception:
        pass

    return False


def generate_stock_plot(ticker: str):
    
    endPeriod = datetime.today()
    startPeriod = endPeriod - relativedelta(years=1)
    endPeriod_str = endPeriod.strftime('%Y-%m-%d')
    startPeriod_str = startPeriod.strftime('%Y-%m-%d')

    df = yf.download(tickers=ticker, start=startPeriod_str, end=endPeriod_str, interval='1d')
    
    plt.plot(df.index, df['Close'], label='Closing Price')
    plt.title(f'{ticker} Closing Prices for the Past Year')
    plt.xlabel('Date')
    plt.ylabel('Closing Price (USD)')
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    img = io.BytesIO()
    plt.savefig(img, format='png')
    plt.close()
    img.seek(0)

    return img


def fetchArticles(ticker: str):
    
    NEWS_API_URL = os.getenv("NEWS_API_URL")
    NEWS_API_KEY = os.getenv("NEWS_API_KEY")

    params = {
        "api_token" : NEWS_API_KEY,
        "search" : ticker,
        "categories" : "business,finance",
        "language" : "en",
        "limit" : 5
    }

    response = requests.get(NEWS_API_URL, params=params)

    if response.status_code == 200:
        data = response.json()
        articles = data.get("data", [])
        return [
            {
                "title" : article["title"],
                "url" : article["url"],
                "source" : article["source"],
                "published_at" : article["published_at"]
            }
            for article in articles
        ]
    else:
        raise Exception(f"Failed to fetch news: {response.status_code}, {response.text}")
    

@app.route('/')
def index():

    return render_template('index.html')


@app.route('/get_stock_data', methods=['POST'])
def get_stock_data():

    ticker = request.form.get('ticker', '').upper()

    if exists(ticker):
        try:
            image_url = f'/get_image/{ticker}'
            articles_url = f'/get_articles/{ticker}'

            return {"image_url": image_url, "articles)url" : articles_url}, 200
        
        except Exception as e:
            return {"error": f"An error occurred: {str(e)}"}, 500
        
    else:
        return {"error" : "Invalid ticker"}, 400


@app.route('/get_image/<ticker>')
def get_image(ticker):

    try:
        img = generate_stock_plot(ticker)

        return send_file(img, mimetype='image/png')
    
    except Exception as e:
        return render_template("error.html", error_message=f"An error occurred: {str(e)}"), 500


@app.route('/get_articles/<ticker>')
def get_articles(ticker):

    try:
        articles = fetchArticles(ticker)

        return jsonify(articles), 200
    
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}, 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

