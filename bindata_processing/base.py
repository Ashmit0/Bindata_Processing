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

        self.N = len(inputs['underlying'])

        # list of working dates 
        self.dates = [pd.date_range( start= inputs['start_date'][i] , end = inputs['end_date'][i] , freq = 'D' ) for i in range(self.N) ]
        self.dates = [drop_weekends( self.dates[i] ) for i in range(self.N) ]
        self.dates = [self.dates[i].strftime( date_format= date_format).to_list() for i in range(self.N) ]

        # dates in standard format 
        self.dates_formated = format_dates( self.dates )

        # lof file paths : 
        self.dates_log_path = get_log_file_path( self.inputs , self.dates )

        # second wise time indices : 
        self.time_indexs = [[ pd.date_range(start= date + ' ' + "09:15:01", end=date + ' ' + "15:30:00", freq='s') for date in self.dates[i] ] for i in range(self.N)]

        self.main_dict = {}

    
    def load_dict(self)-> None : 
        main_dict = {}
        for underlying in self.inputs['underlying'] : 
            main_dict[underlying] = {}
        for i , underlying in enumerate( self.inputs['underlying'] ):
            code = self.inputs['exp'][i]
            main_dict[underlying][code] = {}
            for date , path , time_index in zip(self.dates_formated[i] , self.dates_log_path[i], self.time_indexs[i] ) : 
                pkl_name = get_pickel_name( self.inputs , i  , date  )
                try : 
                    with open(pkl_name , 'rb' ) as f : 
                        main_dict[underlying][code][date] = pickle.load(f)
                except : 
                    print(f'Creating {pkl_name}. This is a one time process ...')
                    main_dict[underlying][code][date] = create_date_dict( date , path , time_index , self.inputs , i  )
                    with open(pkl_name , 'wb' ) as f : 
                        pickle.dump( main_dict[underlying][code][date] , f )
        self.main_dict =  main_dict 


    def __str__(self):
        return dict_hierarchy_to_str( self.main_dict )
