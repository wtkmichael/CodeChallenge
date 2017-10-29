#!/usr/bin/env python2
# -*- coding: utf-8 -*-


import numpy as np
import pandas as pd
import re

data = pd.read_json('crime_count.json', orient='records')
data = pd.melt(data.reset_index(), id_vars=['index'], var_name=['county'])
data = data.rename(columns={'index': 'crime'})

def cross_corr_max_val(a,b):
    N = len(a)    
        
    if np.array_equal(a,b):
        x = np.arange(1,N-1)
    else:
        x = np.arange(0,N-1)
        
    cross_set = list(map(lambda x: pd.Series(a).corr(pd.Series(b).shift(x)),x))
    if np.isnan(cross_set).all():
        return [-999,0]
    else:
        lag = np.nanargmax(np.abs(cross_set))
        valcorr = cross_set[np.nanargmax(np.abs(cross_set))]
        return [lag, valcorr]

# Change to only compare with either same county or same crime
df_out = pd.DataFrame(columns=['acrime', 'acounty', 'bcrime', 'bcounty', 'corr_rec'])

for i in range(0,len(data)):
    # Correlation of similar crime across Geographical region
    origin = data.iloc[i,:]
    compare = data[data.crime == origin[0]]
    sliding_scale = compare.iloc[:,:2]
    sliding_scale = sliding_scale.rename(columns={'crime': 'bcrime','county': 'bcounty'})
    sliding_scale['corr_rec'] = compare.apply(lambda x: cross_corr_max_val(origin[2],x['value']),axis=1)
    
    sliding_scale['acrime'] = origin[0]
    sliding_scale['acounty'] = origin[1]
    df_out = pd.concat([df_out, sliding_scale])
    
    # Correlation between crime in same region
    compare = data[data.county == origin[1]]
    sliding_scale = compare.iloc[:,:2]    
    sliding_scale = sliding_scale.rename(columns={'crime': 'bcrime','county': 'bcounty'})
    sliding_scale['corr_rec'] = compare.apply(lambda x: cross_corr_max_val(origin[2],x['value']),axis=1)
    
    sliding_scale['acrime'] = origin[0]
    sliding_scale['acounty'] = origin[1]
    df_out = pd.concat([df_out, sliding_scale])
    #print('completed correlation count for ', data.iloc[i,0], '-', data.iloc[i,1])

corr_count = pd.DataFrame(df_out.corr_rec.values.tolist())
df_out[['lag','calc_cor']] = corr_count
df_out = df_out.drop('corr_rec', axis=1)
df_out = df_out[df_out.lag != -999].reset_index(drop=True)

df_out = df_out[df_out.lag != -999].reset_index(drop=True)
df_out = df_out.reindex(df_out.calc_cor.abs().sort_values().index).reset_index(drop=True)
df_out = df_out.reset_index().sort_values(by=['acounty','acrime','index'],ascending=[True, True, False]).reset_index(drop=True)
df_out.drop('index',axis=1).to_csv('Ranked_correlation.csv')

f = open("policeGeoJSON.js","r")

r = f.readlines()
f.close()

word = 'LSOAname'
def if_word_in_line(word, xstring,y):
    if word in xstring: 
        return y
    
element = [if_word_in_line(word, x, r.index(x)) for x in r]
element = list(set(element))
element = [x for x in element if x is not None]

LSO = [r[i] for i in element]
longitude = [r[i+6] for i in element]
latitude = [r[i+7] for i in element]

m = [re.search('LSOAname":(.*)', x) for x in LSO]

new_location = [''.join(x.groups()).strip().replace('"','').replace(',','') for x in m]
new_latitude = [float(x.strip().replace(',','')) for x in latitude]
new_longitude = [float(x.strip().replace(',','')) for x in longitude]

df_coord = pd.DataFrame(new_location, columns=['county'])
df_coord.loc[:,'latitude']= new_latitude
df_coord.loc[:,'longitude']= new_longitude

df1 = pd.merge(df_out, df_coord, how='left', left_on='acounty', right_on='county',
         suffixes=('_x', '_y'))

df1.drop(['county'],axis=1).to_csv('Corr_with_coord.csv')