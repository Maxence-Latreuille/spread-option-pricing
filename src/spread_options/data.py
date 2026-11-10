import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta



def data(ticker="BZ=F", start="01/01/2021", T=1):
    """Retrieve historical closing prices from the first available trading day over a maturity T (in years)."""
    start_date = datetime.strptime(start, "%d/%m/%Y")
    end_date = start_date + timedelta(days=365*T + 15)  

    data1 = yf.download(
        ticker,
        start=start_date.strftime("%Y-%m-%d"),
        end=(end_date + timedelta(days=1)).strftime("%Y-%m-%d"),
        interval="1d",
        auto_adjust=False,
        group_by="ticker",
        progress=False
    )

    St = data1[ticker]["Close"].dropna()  
    if St.empty:
        raise ValueError("Aucune donnée disponible.")

    start_reel = St.index[0]     
    fin = start_reel + timedelta(days=365*T)     
    St = St.loc[St.index <= fin]      

    tableau = np.empty((len(St), 2), dtype=object)
    tableau[:, 0] = St.index.strftime("%d/%m/%Y").tolist()
    tableau[:, 1] = [round(float(p), 2) for p in St.to_numpy()]

    return tableau




def sigma_histo(ticker="BZ=F", start="01/01/2021"):
    """Estimate annualized historical volatility from all available closing prices up to the specified date."""
    start_date = datetime.strptime(start, "%d/%m/%Y")

    data1 = yf.download(
        ticker,
        period="max",
        end=(start_date + timedelta(days=1)).strftime("%Y-%m-%d"),
        interval="1d",
        auto_adjust=False,
        group_by="ticker",
        progress=False
    )

    St = data1[ticker]["Close"].dropna()
    St = St[St > 0]

    if len(St) < 3:
        raise ValueError("Pas assez de données historiques.")

    returns = np.log(St / St.shift(1)).dropna()
    sigma = float(returns.std() * np.sqrt(252))

    return sigma




print(data(ticker="BZ=F", start="01/01/2021", T=1))
print(sigma_histo(ticker="BZ=F", start="01/01/2021"))

