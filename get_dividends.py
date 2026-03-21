def get_div_rate(ticker):
    import pandas as pd
    import numpy as np  
    from datetime import datetime, timedelta
    import yfinance as yf  
    import pytz

    # STOCK PRICE
    now = datetime.now(pytz.utc) + timedelta(days=1)  # Ensure 'now' is in UTC
    end_date = now.strftime("%Y-%m-%d")
    start_date = (now - timedelta(days=5)).strftime("%Y-%m-%d")

    # Most recent stock price
    SP = yf.download(
        tickers=[ticker],
        start=start_date,
        end=end_date,
        interval="1m",
        auto_adjust=True
    )

    SP = SP[['Close']]
    SP = SP.reset_index()

    # Handling the DST ambiguity
    #SP['Date'] = SP['Date'].apply(lambda x: x.tz_localize('UTC').tz_convert( ambiguous='NaT'))

    max_date = np.max(SP['Datetime'].dropna())  # Drop NaT values if any ambiguity exists
    last_known_price = SP[SP['Datetime'] == max_date]['Close'].iloc[0]

    # DIVIDENDS DATA
    stock = yf.Ticker(ticker)
    df = pd.DataFrame( stock.dividends )

    df = df.reset_index()
    df['Date'] = pd.to_datetime(df['Date'])

    min_date, max_date = np.min(df['Date']) , np.max(df['Date'])
    max_date_minus_one_year = max_date - timedelta(days = 365) 

    sub_dividends = df[ (df['Date'] >= max_date_minus_one_year) ]

    divs_paid_last_year = float( np.sum( sub_dividends['Dividends']) )


    dividend_rate = divs_paid_last_year / last_known_price
    return(dividend_rate.iloc[0])



s = get_div_rate('VIG') ; print(s)

s = get_div_rate('SPY') ; print(s)

s = get_div_rate('AAPL') ; print(s)

s = get_div_rate('AVGO') ; print(s)

s = get_div_rate('MSFT') ; print(s)

s = get_div_rate('JPM') ; print(s)



