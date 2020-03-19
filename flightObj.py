import numpy as np                 #number crunching library
import pandas as pd                #Numpy on big data steroids
from datetime import datetime      #does all the heavy lifting with dates and times
from datetime import date
import dateutil


class Flight():    #main class for flights
    def __init__(self, flightid, data):         #starts object
        self.fid = flightid                     #using flight ID
        self.df = data
        self.df.reset_index(drop=True)      #solves issues where the index stays from previous, resets it to start at 1,2,3.. etc
        
        self.data_prepare()                 #main pointer to data prepare function
        
    def data_prepare(self):                 #prepare function, seperate so it can be called seperately
        
        self.populate()
        self.make_dataset()
        
        
        
    def populate(self):                    #take constant values from the data and attach it to the object
        self.tid = self.df['TRACK_ID'].iloc[0]
        self.call = self.df['CALLSIGN'].iloc[0]
        self.actype = self.df['ICAO_ACTYPE'].iloc[0]
        self.dest = self.df['DEST'].iloc[0]
        self.adep = self.df['ADEP'].iloc[0]
        self.ftype = self.df['FLIGHT_TYPE'].iloc[0]
        self.radar = self.df['RADAR'].iloc[0]
        if self.ftype == 'OUTBOUND':                         #the data has different collumns for inbound and outbound flights
            self.aptime = self.df['TAKEOFF_TIME'].iloc[0]
        else:
            self.aptime = self.df['LANDING_TIME'].iloc[0]
    
    def calc_tplus(self, start, row):                         #a function that gives the difference in seconds between given row of data and the start time of the flight.
        tplus = datetime.strptime(row['TIME'], '%d-%m-%Y %H:%M:%S') - start
        return tplus
    
    def make_dataset(self):
        self.ds = self.df[['FLIGHT_ID', 'X', 'Y', 'MODE_C', 'TIME']]
        self.first_timestamp = datetime.strptime(self.ds['TIME'].iloc[0], '%d-%m-%Y %H:%M:%S')
        #self.first_timestamp = datetime.strptime('2019', '%Y')
        self.ds['TPLUS'] = self.ds.apply(lambda row : self.calc_tplus(self.first_timestamp, row), axis=1).apply(lambda x: int(x.total_seconds()))
        
        self.calc_vel()
        
    def calc_vel(self):
    #This part calculates the velocity by substracting taking the derivative with respect to time before and after a specific point. [a, b, c, d]: (b-a) - (b-c) = c-a
        ds_c = self.ds[['X', 'Y', 'MODE_C', 'TPLUS']].diff(periods = 1) - self.ds[['X', 'Y', 'MODE_C', 'TPLUS']].diff(periods = -1)
        self.ds['VEL_X'] = ds_c['X'] / ds_c['TPLUS']
        self.ds['VEL_Y'] = ds_c['Y'] / ds_c['TPLUS']
        self.ds['VEL_Z'] = ds_c['MODE_C'] / ds_c['TPLUS']
        
        self.ds['VEL_HOZ'] = np.sqrt(self.ds['VEL_X']**2 + self.ds['VEL_Y']**2)
        self.ds['VEL_TOT'] = np.sqrt(self.ds['VEL_X']**2 + self.ds['VEL_Y']**2 + self.ds['VEL_Z']**2)
        