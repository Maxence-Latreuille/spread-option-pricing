import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta



def data(ticker="BZ=F", start="01/01/2021", T=365):

    # Conversion des dates
    start_date = datetime.strptime(start, "%d/%m/%Y")
    end_date = start_date + timedelta(days=T)

    # Téléchargement des données
    data1 = yf.download(
        ticker,
        start=start_date.strftime("%Y-%m-%d"),
        end=(end_date + timedelta(days=1)).strftime("%Y-%m-%d"),
        interval="1d",
        auto_adjust=False,
        group_by="ticker",
        progress=False
    )

    # Extraction des prix de clôture
    St = data1[ticker]["Close"].dropna()

    # Création du tableau NumPy
    tableau = np.empty((len(St), 2), dtype=object)

    tableau[:, 0] = St.index.strftime("%d/%m/%Y").tolist()
    tableau[:, 1] = [round(float(p), 2) for p in St.to_numpy()]

    return tableau


print (data(ticker="BZ=F", start="01/01/2021", T=365))

