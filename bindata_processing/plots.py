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

def plot_time_series( df , col  , strike , start_end_stamp , date , inputs ,  x : bool = True , save_dir = None  ): 
    start_time , end_time = start_end_stamp
    plt.figure()
    if x : 
        plt.plot( df.index[1:] , df[col][1:]  , 'o-' , color = 'r' , markersize=0.1)
    else : 
        plt.plot( df.index , df[col]  , 'o-' , color = 'r' , markersize=0.1)
    plt.xlim( start_time , end_time )
    plt.tight_layout()
    plt.xticks(
        ticks = pd.date_range(start=start_time, end=end_time, freq='1h') , 
        labels = pd.date_range( start = start_time  , end = end_time, freq = '1h' ).time
    )
    plt.grid()
    plt.title( f"{col} for {inputs['underlying']}; exp: {inputs['exp']}; strike: {strike}; date : {date} {pd.to_datetime( date , dayfirst=True).day_name()}")
    if save_dir != None : 
        plt.savefig( save_dir )
    plt.show()