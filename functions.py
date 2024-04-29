import yfinance as yf

def get_stock_price(ticker):
    """
    Fetches the current stock price for a given ticker symbol using the yfinance library.

    Args:
        ticker (str): The ticker symbol for the stock of interest.

    Returns:
        float: The current stock price for the given ticker symbol.
    """

    # Create a Yahoo Finance Ticker object
    ticker_data = yf.Ticker(ticker)

    # Get the latest market data for the ticker
    current_price = ticker_data.info['regularMarketPrice']
    print(current_price)

    return current_price

# # User inputs the ticker symbol
# ticker = input("Enter the ticker symbol for the stock you want to check: ")

# # Get the stock price and print it to the console
# stock_price = get_stock_price(ticker)
# print(f"The current price for {ticker} is ${stock_price}")