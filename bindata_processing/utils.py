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

date_format = '%Y%m%d'
date_time_format = '%d-%m-%Y %H:%M:%S'


# drop weekends from the date range 
def drop_weekends(date_range: pd.DatetimeIndex) -> pd.DatetimeIndex:
    """Remove weekends (Saturday and Sunday) from a pandas date range."""
    return date_range[~date_range.weekday.isin([5, 6])]

# format from one fromat to another 
def format_dates(date_list):
    n = len( date_list )
    parsed_dates = [pd.to_datetime(date_list[i], format='%Y%m%d') for i in range(n)]
    return [parsed_dates[i].strftime('%d-%m-%Y').tolist() for i in range(n) ]


def get_log_file_path( inputs , dates_list ) : 
    paths = []
    for parent , dates in zip(inputs['parent_dir'] , dates_list) : 
        paths.append( [os.path.join( parent , date , 'bin_data_archival_' + date + '.log') for date in dates ] ) 
    return paths 


month_to_nse_code = {
    1: 'F',   # January
    2: 'G',   # February
    3: 'H',   # March
    4: 'J',   # April
    5: 'K',   # May
    6: 'M',   # June
    7: 'N',   # July
    8: 'Q',   # August
    9: 'U',   # September
    10: 'V',  # October
    11: 'X',  # November
    12: 'Z'   # December
}


nse_code_to_month = {
    'F': 1,
    'G': 2,
    'H': 3,
    'J': 4,
    'K': 5,
    'M': 6,
    'N': 7,
    'Q': 8,
    'U': 9,
    'V': 10,
    'X': 11,
    'Z': 12
}



def last_thursday(year, month):
    # Find the last day of the month
    last_day = calendar.monthrange(year, month)[1]
    # Create a date object for the last day of the month
    last_date = datetime.date(year, month, last_day)
    # Calculate the offset to the last Thursday (weekday 3)
    offset = (last_date.weekday() - 3) % 7
    # Subtract the offset to get the last Thursday
    last_thursday_date = last_date - datetime.timedelta(days=offset)
    return last_thursday_date



def get_date_code( date : str ) : 
    date = pd.to_datetime( date , format = '%Y%m%d')
    
    yy = date.strftime('%y')  # Last two digits of the year
    mm = date.strftime('%m')  # Two-digit month

    mm = int( mm )

    code = month_to_nse_code[mm] + str(yy)

    return code 


def get_code_date( code : str ): 
    month = nse_code_to_month( code[0] )
    year = 2000 + int( code[1:] )
    
    return last_thursday( year , month )


def groupby_to_nested_dict(df, group_cols):
    if not group_cols:
        return df.reset_index(drop=True)
    col = group_cols[0]
    return {
        key: groupby_to_nested_dict(sub_df, group_cols[1:])
        for key, sub_df in df.groupby(col)
    }


def get_pickel_name( inputs , i , date ) : 
    return 'cache/' + '_'.join([date,inputs['underlying'][i],str(inputs['strike_range'][i]),inputs['exp'][i]] ) + '.pkl' 