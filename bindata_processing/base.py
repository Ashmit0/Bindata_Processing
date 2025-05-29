import os 
import yaml 
import random 
import pickle
import numpy as np 
import pandas as pd 
import matplotlib.pyplot as plt 

random.seed( 17 )
import datetime 
import calendar 
import holidays 


plt.rcParams['font.size'] = 14 
plt.rcParams['figure.figsize'] = (15,5)
plt.rcParams['lines.linewidth'] = .5


from .utils import * 
from .preprocessing import *  
from .plots import * 




class bindata_query : 

    def __init__(self,inputs) -> None:
        self.inputs = inputs 

        # list of working dates 
        self.dates = pd.date_range( start= inputs['start_date'] , end = inputs['end_date'] , freq = 'D' )
        self.dates = drop_weekends( self.dates )
        self.dates = self.dates.strftime( date_format= date_format).to_list()

        # dates in standard format 
        self.dates_formated = format_dates( self.dates )

        # lof file paths : 
        self.dates_log_path = [ get_log_file_path(date , inputs['parent_dir']) for date in self.dates ]

        # contract exp code  :
        self.code = get_date_code( inputs['exp'] )

        # second wise time indices : 
        self.time_indexs = [ pd.date_range(start= date + ' ' + "09:15:01", end=date + ' ' + "15:30:00", freq='s') for date in self.dates ]

    
    def load_dict(self)-> None : 
        main_dict = {}
        for date , path , time_index in zip(self.dates_formated , self.dates_log_path, self.time_indexs ) : 
            pkl_name = get_pickel_name( self.inputs , date , self.code )
            try : 
                with open(pkl_name , 'rb' ) as f : 
                    main_dict[date] = pickle.load(f)
            except : 
                main_dict[date] = create_date_dict( date , path , time_index , self.inputs  )
                with open(pkl_name , 'wb' ) as f : 
                    pickle.dump( main_dict[date] , f )
        self.main_dict =  main_dict 
