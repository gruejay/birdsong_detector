import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import json
import xenocanto_download as xcd
import asyncio

recordings = list()

with open("dataset/metadata/BeardedBellbird/page1.json",'r') as file:
        full_obj = json.load(file)
        recordings = recordings + full_obj['recordings']


df = pd.DataFrame.from_records(recordings)
df.drop(['rec', 'cnt', 'loc', 'lat','lng', 'alt', 'method',
       'file-name', 'sono', 'osci', 'lic', 'time', 'date',
       'uploaded', 'also', 'rmk', 'animal-seen', 'playback-used',
       'temp', 'regnr', 'auto', 'dvc', 'mic', 'smp'], axis=1, inplace=True)

df = df[df['q'] == 'A']
df = df[(df['type'] == 'song')]
df = df[df['bird-seen'] == 'yes']
url_list = list(map(tuple, df[['id', 'file']].to_numpy()))
path = "dataset/audio/" + df['gen'][1] + df['sp'][1] + '/'
asyncio.run(xcd.download(url_list, path))



