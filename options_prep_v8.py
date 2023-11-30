#
#  PRO:      options_prep
#  PURPOSE:  get options data from yahoo finance 
#  DATE:     winter 2022
#  
#  BS file will output the following:
#                          CALL        PUT
#               Price   6.216300   5.717600
#               Delta   0.543134  -0.456866
#               Gamma   0.026441   0.026441
#               Theta -12.860186 -10.870161
#               Vega   19.830406  19.830406
#               Rho    12.024283 -12.851029
#               Psi   -13.578359  11.421641

import os
import pandas as pd
import numpy as np  
import yfinance as yf          # https://pypi.org/project/yfinance/

from BS import *
from get_dividends import *

from datetime import datetime, timedelta, date
from pandas.tseries.holiday import USFederalHolidayCalendar
import calendar

import warnings
warnings.filterwarnings("ignore")

program_start_time = datetime.now()

ticker = 'SPY'

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


holidays = cal.holidays(start=datetime.now(), end=datetime.now()).to_pydatetime()


if len(holidays) >=1:
    print("TODAY IS A HOLIDAY .. STOP PROGRAM!")
    exit()

else:

    # Most recent stock price
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

    print('DATA PREP \n')
    call_col_names = TICKER.option_chain(dates[0]).calls.columns
    put_col_names = TICKER.option_chain(dates[0]).puts.columns

    # START AN EMPTY DATA FRAME
    stacked_call_data = pd.DataFrame(columns =  call_col_names)
    stacked_call_data['OPTION_TYPE'] = []
    stacked_call_data['EXPIRATION_DATE']  = []

    stacked_put_data = pd.DataFrame(columns =  put_col_names)
    stacked_put_data['OPTION_TYPE'] = []
    stacked_put_data['EXPIRATION_DATE']  = []


    # STACK THE DATASETS
    # print("STACK IT! \n") 
    for i in range(0, l):

        OPTIONS_d = TICKER.option_chain(dates[i])

        temp_call_df = OPTIONS_d.calls
        call_rows, call_columns = temp_call_df.shape


        temp_put_df = OPTIONS_d.puts
        put_rows, put_columns = temp_put_df.shape


        temp_call_df['OPTION_TYPE'] = ['CALLS'] * call_rows
        temp_call_df['EXPIRATION_DATE'] = [dates[i]] * call_rows

        temp_put_df['OPTION_TYPE'] = ['PUTS'] * put_rows
        temp_put_df['EXPIRATION_DATE'] = [dates[i]] * put_rows


        stacked_call_data = stacked_call_data.append( temp_call_df )
        stacked_put_data = stacked_put_data.append( temp_put_df )


    # MERGE CALL AND PUTS
    joined_df = pd.merge(stacked_call_data, stacked_put_data, left_on = ['strike', 'EXPIRATION_DATE'], right_on = ['strike', 'EXPIRATION_DATE'], how = 'inner', suffixes=('_CALL', '_PUT'))
    n_row, n_col = joined_df.shape

    joined_df['EXPIRATION_DATE'] = pd.to_datetime(joined_df['EXPIRATION_DATE'])  
    
    # DATA CLEANING AND PREP
    joined_df['SNAPSHOT_DATE'] = pd.to_datetime("today").strftime("%Y-%m-%d %H:%M:%S")    #  when was data collected? 
    joined_df['SNAPSHOT_DATE'] = pd.to_datetime(joined_df['SNAPSHOT_DATE'])

    joined_df['SNAPSHOT_DATE_ET'] = joined_df['SNAPSHOT_DATE'] - pd.Timedelta(5, unit = 'hours')

    
    # options expire at market close! 
    for i in range(0, n_row):
        joined_df['EXPIRATION_DATE'].iloc[i] = joined_df['EXPIRATION_DATE'].iloc[i].replace(hour = 16, minute = 0 )


    joined_df['TIME_TO_MATURITY_(YRS)'] = joined_df['EXPIRATION_DATE'] - joined_df['SNAPSHOT_DATE_ET'] 
    joined_df['TIME_TO_MATURITY_(DAYS)']  = joined_df['TIME_TO_MATURITY_(YRS)'].dt.days
    joined_df['TIME_TO_MATURITY_(YRS)'] = joined_df['TIME_TO_MATURITY_(YRS)'].dt.days / 252

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
    
    # What day of week?
    joined_df.insert( (n_col + 3 ), 'WEEKDAY' ,  [day_of_week]*n_row )

    # option greeks
    call_delta, call_gamma, call_theta, call_vega, call_rho, call_psi = [], [], [], [], [], []
    put_delta,  put_gamma, put_theta, put_vega, put_rho, put_psi = [], [], [], [], [], []
    for i in range(0, n_row):
        BS_CALL = BS(joined_df[stock_price_name].iloc[i], joined_df['STRIKE'].iloc[i], joined_df['IMPLIED_VOLATILITY_CALL'].iloc[i], delta, T_BILL, joined_df['TIME_TO_MATURITY_(YRS)'].iloc[i] )
        BS_PUT = BS(joined_df[stock_price_name].iloc[i], joined_df['STRIKE'].iloc[i], joined_df['IMPLIED_VOLATILITY_PUT'].iloc[i], delta, T_BILL, joined_df['TIME_TO_MATURITY_(YRS)'].iloc[i] )

        call_delta.append(BS_CALL['CALL'].iloc[1])
        call_gamma.append(BS_CALL['CALL'].iloc[2])
        call_theta.append(BS_CALL['CALL'].iloc[3])
        call_vega.append(BS_CALL['CALL'].iloc[4])
        call_rho.append(BS_CALL['CALL'].iloc[5])
        call_psi.append(BS_CALL['CALL'].iloc[6])

        put_delta.append(BS_PUT['PUT'].iloc[1])
        put_gamma.append(BS_PUT['PUT'].iloc[2])
        put_theta.append(BS_PUT['PUT'].iloc[3])
        put_vega.append(BS_PUT['PUT'].iloc[4])
        put_rho.append(BS_PUT['PUT'].iloc[5])
        put_psi.append(BS_PUT['PUT'].iloc[6])

    joined_df.insert( (n_col + 4 ), 'CALL_DELTA' ,  call_delta )
    joined_df.insert( (n_col + 5 ), 'CALL_GAMMA' ,  call_gamma )
    joined_df.insert( (n_col + 6 ), 'CALL_THETA' ,  call_theta )
    joined_df.insert( (n_col + 7 ), 'CALL_VEGA' ,   call_vega )
    joined_df.insert( (n_col + 8 ), 'CALL_RHO' ,    call_rho )
    joined_df.insert( (n_col + 9 ), 'CALL_PSI' ,    call_psi )

    joined_df.insert( (n_col + 10 ), 'PUT_DELTA' ,  put_delta )
    joined_df.insert( (n_col + 11 ), 'PUT_GAMMA' ,  put_gamma )
    joined_df.insert( (n_col + 12 ), 'PUT_THETA' ,  put_theta )
    joined_df.insert( (n_col + 13 ), 'PUT_VEGA' ,   put_vega )
    joined_df.insert( (n_col + 14 ), 'PUT_RHO' ,    put_rho )
    joined_df.insert( (n_col + 15 ), 'PUT_PSI' ,    put_psi )


    # WRITE TO EXCEL  
    max_date = max_date.strftime('%Y-%m-%d')
    time_now_string = str(time_now.strftime('%Y-%m-%d__%H-%M'))

    file_name = 'options_data/' + ticker + '__' + time_now_string  +'.xlsx'
    #print(file_name)
    #joined_df = joined_df[joined_df['STRIKE'] == 397]
    joined_df.to_excel(file_name, index = False)

    

    program_end_time = datetime.now()

    total_time = (program_end_time - program_start_time).total_seconds()
    total_time = round( total_time , ndigits = 2)
    print("PROGRAM COMPLETE (" + str(total_time) + " seconds)" )






