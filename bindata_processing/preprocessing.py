import os 
import random 
import numpy as np 
import pandas as pd 
import matplotlib.pyplot as plt 

import datetime 
import calendar 
import holidays 

plt.rcParams['font.size'] = 14 
plt.rcParams['figure.figsize'] = (15,5)
plt.rcParams['lines.linewidth'] = .5


from .utils import groupby_to_nested_dict , get_date_code 



def process_spot_data(spot_rows:list,date:str,time_index): 
    result_df = pd.concat(spot_rows, ignore_index=True )
    if result_df.empty : 
        raise ValueError(f'No Underlying found on {date}')
    result_df['Time'] = pd.to_datetime(date + ' ' + result_df['Time'] , format = '%d-%m-%Y %H:%M:%S')

    result_df['Close'] = result_df['Close']/100
    result_df = result_df.set_index('Time').reindex( time_index )
    result_df['Close'] = result_df['Close'].ffill().bfill()

    result_df['Spot Return %'] = result_df['Close'].pct_change()*100

    return result_df 


def process_strike_dict(strike_dict:dict,date:str,time_index,nresult_df) : 
    rm_strikes = []
    for strike in strike_dict.keys() :
        df = pd.DataFrame()
        try : 
            df = strike_dict[strike]['PE'].copy()
            df = df[[ 'Time' , 'Close']]
            df = df.rename(columns={'Close': 'PE_Close'})
            df['Time'] = pd.to_datetime(date + ' ' + df['Time'] , format = '%d-%m-%Y %H:%M:%S')
            df = df.set_index('Time').reindex( time_index )
            try : 
                df2 = strike_dict[strike]['CE'].copy()
                df2 = df2[['Time' , 'Close']]
                df2 = df2.rename(columns={'Close': 'CE_Close'})
                df2['Time'] = pd.to_datetime(date + ' ' + df2['Time'] , format = '%d-%m-%Y %H:%M:%S')
                df2 = df2.set_index('Time').reindex( time_index )
                df['CE_Close'] = df2['CE_Close']

                cols_to_fill = ['CE_Close', 'PE_Close']
                df[cols_to_fill] = df[cols_to_fill].ffill().bfill()

                df['Orb2'] = df['CE_Close'] - df['PE_Close'] - nresult_df['Close'] + strike
                df['Orb2_diff'] = df['Orb2'].diff()

            except : 
                print(f'No Conjugate Call Option is Present for {strike} Put Option on {date} \n This strike price will be droped .... ') 
                rm_strikes.append( strike )
        except : 
            print(f'No Conjugate Put Option is Present for {strike} Call Option on {date} \n This strike price will be droped .... ') 
            rm_strikes.append( strike )

        strike_dict[strike] = df 
    return rm_strikes 


def process_options_data( strike_rows:list, date:str, time_index , nresult_df ): 
    strike_df = pd.concat(strike_rows, ignore_index=True )
    strike_df['Close'] = strike_df['Close']/100

    if strike_df.empty : 
        raise ValueError(f'!!!!!Strike Bounds are Out of Range for {date}!!!')
        

    strike_dict = groupby_to_nested_dict( strike_df , ['Strike'  , 'Type' ] )
    rm_strikes = process_strike_dict( strike_dict , date , time_index , nresult_df )

    for key in rm_strikes : 
        strike_dict.pop( key , None )

    return strike_dict 





def create_main_dict( dates_formated , dates_log_path , time_indexs , inputs ) : 
    main_dict = {}
    for date , path , time_index in zip( dates_formated , dates_log_path , time_indexs): 
        symbol = inputs['underlying'] + '_' + get_date_code( inputs['exp'] )

        main_dict[date] = {}

        chunk_size = 100000 # Tune as needed
        spot_rows = []
        strike_rows = []

        for chunk in pd.read_csv(path, chunksize=chunk_size , usecols= [1,2,8]):
            # Filter rows where Symbol exactly matches 'NSEFNO_BANKNIFTY_F25'
            matched = chunk[chunk['Symbol'] == symbol]
            spot_rows.append(matched)
            # save to dict 
            main_dict[date]['Spot'] = process_spot_data( spot_rows , date , time_index )

            # For strike rows : 
            matched = chunk[
                chunk['Symbol'].str.startswith(symbol) & 
                (chunk['Symbol'] != symbol ) 
            ].copy()
            split_cols = matched['Symbol'].str.split('_', expand=True)

            matched.loc[:, 'Strike'] = split_cols[3].astype(float)
            matched.loc[:, 'Type'] = split_cols[5]

            # get the strike range : 
            # spot at 09:15:05 
            spot = main_dict[date]['Spot']['Close'].iloc[4]
            min_strike = spot - inputs['strike_range']/2 
            max_strike = spot + inputs['strike_range']/2

            matched['Strike'] = matched['Strike'].astype(float)
            
            matched = matched[
                (matched['Strike'] >= min_strike ) & 
                (matched['Strike'] <= max_strike )
            ]
            strike_rows.append(matched)

        # save to dict 
        main_dict[date]['Strike'] = process_options_data(strike_rows , date , time_index , main_dict[date]['Spot'])
    return main_dict 


def create_date_dict( date , path , time_index , inputs ): 
    symbol = inputs['underlying'] + '_' + get_date_code( inputs['exp'] )

    date_dict = {}

    chunk_size = 100000 # Tune as needed
    spot_rows = []
    strike_rows = []

    for chunk in pd.read_csv(path, chunksize=chunk_size , usecols= [1,2,8]):
        # Filter rows where Symbol exactly matches 'NSEFNO_BANKNIFTY_F25'
        matched = chunk[chunk['Symbol'] == symbol]
        spot_rows.append(matched)
        

        # For strike rows : 
        matched = chunk[
            chunk['Symbol'].str.startswith(symbol) & 
            (chunk['Symbol'] != symbol ) 
        ].copy()
        split_cols = matched['Symbol'].str.split('_', expand=True)

        matched.loc[:, 'Strike'] = split_cols[3].astype(float)
        matched.loc[:, 'Type'] = split_cols[5]

        # get the strike range : 
        # spot at 09:15:05 
        spot = spot_rows[0]['Close'].to_list()[0]/100 
        min_strike = spot - inputs['strike_range']/2 
        max_strike = spot + inputs['strike_range']/2

        matched['Strike'] = matched['Strike'].astype(float)
        
        matched = matched[
            (matched['Strike'] >= min_strike ) & 
            (matched['Strike'] <= max_strike )
        ]
        strike_rows.append(matched)

    # save to dict 
    date_dict['Spot'] = process_spot_data( spot_rows , date , time_index )
    # save to dict 
    date_dict['Strike'] = process_options_data(strike_rows , date , time_index , date_dict['Spot'])

    date_dict['Stamp'] = (
        pd.to_datetime(date + ' ' + '09:15:00', format = '%d-%m-%Y %H:%M:%S') , 
        pd.to_datetime(date + ' ' + '15:30:00' , format = '%d-%m-%Y %H:%M:%S')
    )

    return date_dict