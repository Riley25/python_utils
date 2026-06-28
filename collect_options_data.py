import pandas as pd
from pandas.tseries.holiday import USFederalHolidayCalendar

import numpy as np  
from scipy.stats import norm

from datetime import datetime, timedelta
import pytz


import yfinance as yf          # https://pypi.org/project/yfinance/

import os
import calendar

import warnings
warnings.filterwarnings("ignore")


# HELPER FUNCTIONS
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


def get_options_data(ticker):


    program_start_time = datetime.now()

    print(' ')
    print("BEGIN PROGRAM .... " + ticker + ' Data')
    print('----------------------------- \n')


    cal = USFederalHolidayCalendar()   #  Import the federal holidays
    time_now = datetime.now()
    day_of_week = calendar.day_name[time_now.weekday()]   #  'monday', 'tuesday'


    # Cast a wide net 
    now = datetime.now() + timedelta(days = 1) 
    end_date = now.strftime("%Y-%m-%d")
    start_date = (now - timedelta(days = 5)).strftime("%Y-%m-%d")


    SP = yf.download( tickers = [ticker, '^VIX', '^IRX'],   
                        start=start_date, 
                        end=end_date,
                        interval = "1d", 
                        auto_adjust = True  )    

    SP  = SP[['Close']]
    SP.columns = SP.columns.droplevel()
    SP = SP.reset_index()
    max_date = np.max(SP['Date'])  

    print(SP)

    last_known_price =  ( SP[SP['Date'] == max_date] ).copy()


    tick_price = last_known_price[ticker].iloc[0]
    print('THE MOST CURRENT STOCK PRICE = $ ' + str(tick_price))

    VIX = last_known_price['^VIX'].iloc[0]
    T_BILL = (last_known_price['^IRX'].iloc[0])/100

    delta = get_div_rate(ticker)
    print('The dividend rate = ' + str(delta) )

    # Get options data  
    print('GETTING OPTIONS DATA (YaHoo!) \n')
    TICKER = yf.Ticker(ticker)

    dates = TICKER.options
    l = len(dates)



    print("DATA PREP \n")

    call_frames = []
    put_frames = []

    # STACK THE DATASETS
    for expiration_date in dates:
        options_chain = TICKER.option_chain(expiration_date)

        temp_call_df = options_chain.calls.copy()
        temp_call_df["OPTION_TYPE"] = "CALLS"
        temp_call_df["EXPIRATION_DATE"] = expiration_date
        call_frames.append(temp_call_df)
        
        temp_put_df = options_chain.puts.copy()
        temp_put_df["OPTION_TYPE"] = "PUTS"
        temp_put_df["EXPIRATION_DATE"] = expiration_date
        put_frames.append(temp_put_df)

    stacked_call_data = pd.concat(call_frames, ignore_index=True)
    stacked_put_data = pd.concat(put_frames, ignore_index=True)

    # MERGE CALL AND PUTS
    joined_df = pd.merge(
        stacked_call_data,
        stacked_put_data,
        left_on=["strike", "EXPIRATION_DATE"],
        right_on=["strike", "EXPIRATION_DATE"],
        how="inner",
        suffixes=("_CALL", "_PUT")
    )

    n_row, n_col = joined_df.shape

    # DATA CLEANING AND PREP
    joined_df["EXPIRATION_DATE"] = pd.to_datetime(joined_df["EXPIRATION_DATE"]) + pd.Timedelta(hours=16)

    joined_df["SNAPSHOT_DATE"] = pd.Timestamp.now().floor("s")

    snapshot_et = pd.Timestamp.now(tz="America/New_York").floor("s").tz_localize(None)
    joined_df["SNAPSHOT_DATE_ET"] = snapshot_et



    time_to_expiration = joined_df["EXPIRATION_DATE"] - joined_df["SNAPSHOT_DATE_ET"]
    joined_df["TIME_TO_MATURITY_(DAYS)"] = ( time_to_expiration.dt.total_seconds() / 86_400 )
    joined_df["TIME_TO_MATURITY_(YRS)"] = ( time_to_expiration.dt.total_seconds() / (365.25 * 86_400) )


    joined_df['mid_price_CALL'] = (joined_df['bid_CALL'] + joined_df['ask_CALL'])/2
    joined_df['mid_price_PUT'] = (joined_df['bid_PUT'] + joined_df['ask_PUT'])/2



    # SELECT A SUBSET OF COLUMNS
    joined_df = joined_df[['contractSymbol_CALL' ,  'strike'  , 'bid_CALL', 'ask_CALL', 'mid_price_CALL', 'volume_CALL', 'openInterest_CALL', 'impliedVolatility_CALL', 'inTheMoney_CALL', 
                        'contractSymbol_PUT'  ,               'bid_PUT', 'ask_PUT',  'mid_price_PUT',  'volume_PUT' , 'openInterest_PUT' , 'impliedVolatility_PUT' , 'inTheMoney_PUT' , 
                        'EXPIRATION_DATE', 'SNAPSHOT_DATE_ET' ,  'TIME_TO_MATURITY_(YRS)', 'TIME_TO_MATURITY_(DAYS)' ]]


    # RENAME THE COLUMNS
    joined_df.columns = ['CONTRACT_SYMBOL_CALL' ,  'STRIKE'  , 'BID_CALL', 'ASK_CALL', 'MID_PRICE_CALL', 'VOLUME_CALL', 'OPEN_INTEREST_CALL', 'IMPLIED_VOLATILITY_CALL', 'IN_THE_MONEY_CALL', 
                        'CONTRACT_SYMBOL_PUT'  ,             'BID_PUT', 'ASK_PUT',  'MID_PRICE_PUT',  'VOLUME_PUT' , 'OPEN_INTEREST_PUT' , 'IMPLIED_VOLATILITY_PUT' , 'IN_THE_MONEY_PUT' , 
                        'EXPIRATION_DATE', 'SNAPSHOT_DATE_ET' ,  'TIME_TO_MATURITY_(YRS)', 'TIME_TO_MATURITY_(DAYS)' ]


    n_row, n_col = joined_df.shape


    # INCLUDE THE LAST KNOWN STOCK PRICE
    stock_price_name = 'STOCK_PRICE_' + ticker
    joined_df.insert( (n_col ), stock_price_name ,  [tick_price]*n_row )

    # INCLUDE THE LAST KNOWN VIX
    joined_df.insert( (n_col + 1 ), 'VIX' ,  [VIX]*n_row )
    joined_df.insert( (n_col + 2 ), '13_week_T_BILL_RATE', [T_BILL]*n_row)




    # OPTIONS GREEKS
    S = joined_df[stock_price_name]
    K = joined_df["STRIKE"]
    T = joined_df["TIME_TO_MATURITY_(YRS)"]
    r = joined_df["13_week_T_BILL_RATE"]
    q = float( get_div_rate(ticker) )

    sigma_call = joined_df["IMPLIED_VOLATILITY_CALL"]
    sigma_put = joined_df["IMPLIED_VOLATILITY_PUT"]

    d1_call = ( np.log(S / K) + (r - q + 0.5 * sigma_call**2) * T) / (sigma_call * np.sqrt(T))

    d2_call = d1_call - sigma_call * np.sqrt(T)

    d1_put = (
        np.log(S / K) + (r - q + 0.5 * sigma_put**2) * T
    ) / (sigma_put * np.sqrt(T))

    d2_put = d1_put - sigma_put * np.sqrt(T)


    joined_df["CALL_DELTA"] = np.exp(-q * T) * norm.cdf(d1_call)
    joined_df["PUT_DELTA"] = -np.exp(-q * T) * norm.cdf(-d1_put)

    joined_df["CALL_GAMMA"] = ( np.exp(-q * T) * norm.pdf(d1_call) / (S * sigma_call * np.sqrt(T)) )

    joined_df["PUT_GAMMA"] = ( np.exp(-q * T) * norm.pdf(d1_put) / (S * sigma_put * np.sqrt(T)) )

    joined_df["CALL_VEGA"] = ( S * np.exp(-q * T) * norm.pdf(d1_call) * np.sqrt(T) )

    joined_df["PUT_VEGA"] = ( S * np.exp(-q * T) * norm.pdf(d1_put) * np.sqrt(T))


    joined_df["CALL_THETA"] = (
        -(S * sigma_call * np.exp(-q * T) * norm.pdf(d1_call)) / (2 * np.sqrt(T))
        - r * K * np.exp(-r * T) * norm.cdf(d2_call)
        + q * S * np.exp(-q * T) * norm.cdf(d1_call)
    ) / 365

    joined_df["PUT_THETA"] = (
        -(S * sigma_put * np.exp(-q * T) * norm.pdf(d1_put)) / (2 * np.sqrt(T))
        + r * K * np.exp(-r * T) * norm.cdf(-d2_put)
        - q * S * np.exp(-q * T) * norm.cdf(-d1_put)
    ) / 365


    joined_df["CALL_RHO"] = ( K * T * np.exp(-r * T) * norm.cdf(d2_call) ) / 100
    joined_df["PUT_RHO"] = ( -K * T * np.exp(-r * T) * norm.cdf(-d2_put) ) / 100


    # WRITE TO EXCEL  
    max_date = max_date.strftime('%Y-%m-%d')
    time_now_string = str(time_now.strftime('%Y-%m-%d__%H-%M'))
    file_name = 'options_data/' + ticker + '__' + time_now_string  +'.xlsx'


    #joined_df = joined_df[joined_df['STRIKE'] == 397]
    #joined_df.to_excel(file_name, index = False)



    program_end_time = datetime.now()

    total_time = (program_end_time - program_start_time).total_seconds()
    total_time = round( total_time , ndigits = 2)
    print("PROGRAM COMPLETE (" + str(total_time) + " seconds)" )

    n_row, n_col = joined_df.shape
    print("DATAFRAME SHAPE: " + str(n_row) + " rows, " + str(n_col) + " columns")
    return(joined_df)


df = get_options_data( 'SPY' )

#df.to_excel('test.xlsx', index=False)

