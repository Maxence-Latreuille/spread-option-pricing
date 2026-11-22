import warnings
from datetime import datetime, timedelta

import yfinance as yf

# yfinance still uses an old pandas option (inplace=...): pandas warns, but results are correct
warnings.filterwarnings("ignore", message="The inplace keyword", module="yfinance")

def get_prices(tickers, start, end):
    """Daily closing prices between two dates (dd/mm/yyyy): a Series for one ticker, a DataFrame for several."""
    start_date = datetime.strptime(start, "%d/%m/%Y")
    end_date = datetime.strptime(end, "%d/%m/%Y") + timedelta(days=1) # yfinance excludes the end day
    prices = yf.download(tickers, start=start_date, end=end_date, auto_adjust=True, progress=False)["Close"]
    prices = prices.dropna() # keep only the days where every ticker has a price (needed for a spread)
    if isinstance(tickers, str):
        return prices[tickers] # one ticker: a simple Series
    return prices

if __name__ == "__main__":
    # quick check, runs only with "python src/spread_options/data.py", never on import
    spy = get_prices("SPY", "01/01/2023", "31/12/2023")
    print(spy.head(3))
    both = get_prices(["HO=F", "CL=F"], "01/01/2023", "31/12/2023")
    crack = 42 * both["HO=F"] - both["CL=F"] # 42 gallons per barrel
    print(crack.head(3))