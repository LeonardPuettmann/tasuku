import yfinance as yf
import sqlite3
import requests
import os

def get_stock_price(ticker: str) -> str:
    """ 
    @param ticker: the stock ticker to search for, eg MSFT, AAPL.
    @return: String with the latest closing price
    """
    try:
        ticker = yf.Ticker(ticker)
        ticker_data = ticker.history(period="1d")
        
        closing_price = round(ticker_data['Close'][0], 2)
        return f"The latest closing price is {closing_price} USD"
    except:
        return "Something went wrong while getting the stock data!"
    

def bing_search(query, market="de-DE", response_size="full") -> str:
    """ Search Bing Search for a given query and return the results.
    @param query: The query to search with.
    @param market: The market to search in. Further markets here: <https://learn.microsoft.com/en-us/bing/search-apis/bing-web-search/reference/market-codes>
    @param response_size: The size of the response. Choose "compact" to only get text snippet of the first result. "full" creates a json dump of the results.
    @return: The search results.
    """
    search_url = "https://api.bing.microsoft.com/v7.0/search"

    api_key = os.getenv("BING_SEARCH_API_KEY")

    headers = {"Ocp-Apim-Subscription-Key" : api_key}
    params  = {"q": query, "textDecorations": True, "textFormat": "HTML", "mkt": market}

    response = requests.get(search_url, headers=headers, params=params)
    response.raise_for_status()
    search_results = response.json()

    if response_size == "full":
        results = search_results["webPages"]["value"]
        output = ""
        for result in results[:3]:
            url = result["url"]
            text = result["name"]
            description = result["snippet"]
            output += f"URL: {url}\nText: {text}\nDescription: {description}\n\n"
        return output
    elif response_size == "compact":
        return search_results["webPages"]["value"][0]["snippet"]


def save_todo(task):
    conn = sqlite3.connect('todos.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS todos (task TEXT)''')
    c.execute("INSERT INTO todos VALUES (?)", (task,))
    conn.commit()
    conn.close()