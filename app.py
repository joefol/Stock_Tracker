import yfinance as yf
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io

from flask import Flask, request, render_template, send_file
from datetime import datetime
from dateutil.relativedelta import relativedelta

app = Flask(__name__)

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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_stock_data', methods=['POST'])
def get_stock_data():
    ticker = request.form.get('ticker', '').upper()

    if exists(ticker):
        try:
            image_url = f'/get_image/{ticker}'

            return {"image_url": image_url}, 200
        
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

if __name__ == '__main__':
    app.run(debug=True)
