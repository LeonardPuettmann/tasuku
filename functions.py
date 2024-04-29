import yfinance as yf

def get_stock_price(ticker):
    try:
        ticker = yf.Ticker(ticker)
        data = ticker.history(period="1d")
        return f"The latest closing price is {data['Close'][0]}"
    except Exception as e:
        print("Failed to get required data.", e)

# # User inputs the ticker symbol
# ticker = input("Enter the ticker symbol for the stock you want to check: ")

# # Get the stock price and print it to the console
# stock_price = get_stock_price(ticker)
# print(f"The current price for {ticker} is ${stock_price}")