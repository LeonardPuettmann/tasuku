import yfinance as yf

def get_stock_price(ticker):
    try:
        ticker = yf.Ticker(ticker)
        ticker_data = ticker.history(period="1d")
        
        closing_price = round(ticker_data['Close'][0], 2)
        return f"The latest closing price is {closing_price} USD"
    except:
        return "Something went wrong while getting the stock data!"
