import numpy as np
import pandas as pd
import os
import json



def time_to_int(time):

    # time is a string formated as 'mm:ss'
    secs = sum([int(x) * (60 ** i) for i,x in enumerate(reversed(time.split(':')))])
    return secs

def clean_data(df):
    new_df = df.drop(['rec', 'cnt', 'loc', 'lat','lng', 'alt', 'method', 'url',
       'file-name', 'sono', 'osci', 'time', 'date',
       'uploaded', 'also', 'rmk', 'animal-seen', 'playback-used',
       'temp', 'regnr', 'auto', 'dvc', 'mic', 'smp'], axis=1)
    
    new_df = new_df[df['bird-seen'] == 'yes']
    new_df = new_df[df['type'] == 'song']
    new_df['duration (s)'] = df['length'].apply(time_to_int)
    return new_df


def json_to_df(base_path):
   
    num_pages = 0
    recordings = list()

    # Get first page, including num pages
    with open(base_path + "page1.json",'r') as file:
        full_obj = json.load(file)
        if full_obj['numRecordings'] == 0:
            print('There are no recordings')
            quit()
        else:
            num_pages = full_obj['numPages']   
        recordings = recordings + full_obj['recordings']

    for i in range(2,num_pages):
      with open(base_path + "page{}.json".format(i),'r') as file:
        full_obj = json.load(file)
        recordings = recordings + full_obj['recordings']

    df = pd.DataFrame.from_records(recordings)
    return df
 

def drop_cols(df):
    df.drop(['rec', 'cnt', 'loc', 'lat','lng', 'alt', 'method',
       'file-name', 'sono', 'osci', 'lic', 'time', 'date',
       'uploaded', 'also', 'rmk', 'animal-seen', 'playback-used',
       'temp', 'regnr', 'auto', 'dvc', 'mic', 'smp'], axis=1, inplace=True)

    return
