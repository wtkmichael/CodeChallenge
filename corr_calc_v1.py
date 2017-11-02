#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import numpy as np
from numpy.fft import fft, ifft, fft2, ifft2, fftshift
import pandas as pd
import re
import datetime as dt

data = pd.read_json('crime_count.json', orient='records')
data = pd.melt(data.reset_index(), id_vars=['index'], var_name=['county'])
data = data.rename(columns={'index': 'crime'})

def auto_correlation_using_panda(x):
    lag = np.arange(1,35)
    c = list(map(lambda lag: pd.Series(x).autocorr(lag),lag))
    
    if np.isnan(c).all():
        return (0,0)
    else:
        shift = np.nanargmax(np.abs(c))
        corr = c[np.nanargmax(np.abs(c))]
    return (shift, corr)

def cross_correlation_using_fft(x, y):
    if np.std(x) > 0: x = (x - np.mean(x))/(np.std(x)*len(x))
    if np.std(y) > 0: y = (y - np.mean(y))/np.std(y)
                                                      
    f1 = fft(x)
    f2 = fft(np.flipud(y))
    cc = np.real(ifft(f1 * f2))
    return fftshift(cc)
 
# shift &lt; 0 means that y starts 'shift' time steps before x # shift &gt; 0 means that y starts 'shift' time steps after x
def compute_shift(x, y):
    assert len(x) == len(y)
    c = cross_correlation_using_fft(x, y)
    assert len(c) == len(x)
    zero_index = int(len(x) / 2) - 1    
    shift = zero_index - np.argmax(c)
    corr = np.max(c)
        
    return (shift, corr)

"""Calculation of cross correlations between all time series
1. Cross correlation are calculated for all
2. Dropping all lag with -ve sign (trailing another signal)
3. Dropping x=y series - this will be compare with autocorrelation later
"""
sliding_scale = data.iloc[:,:2]
sliding_scale = sliding_scale.rename(columns={'crime': 'bcrime','county': 'bcounty'})
df_cross = pd.DataFrame(columns=['acrime', 'acounty', 'bcrime', 'bcounty', 'corr_type','corr_rec'])

t0 = dt.datetime.now()
print( "  Start Cross Correlation Calculation= ", dt.datetime.now())
for i in range(0,len(data)):

    origin = data.iloc[i,:]
    sliding_scale['corr_rec'] = data.apply(lambda x: compute_shift(origin[2],x['value']),axis=1)
    sliding_scale['acrime'] = data.iloc[i,0]
    sliding_scale['acounty'] = data.iloc[i,1]
    sliding_scale['corr_type'] = 'cross'
    
    df_cross = pd.concat([df_cross, sliding_scale])
    #print('completed correlation count for ', data.iloc[i,0], '-', data.iloc[i,1])

print( "  Total time used for fold= ", (dt.datetime.now() - t0).seconds)
df_cross[['lag','calc_corr']] = pd.DataFrame(df_cross['corr_rec'].values.tolist(), index=df_cross.index)
df_cross = df_cross[(df_cross.acounty != df_cross.bcounty) & (df_cross.acrime != df_cross.bcrime)]
df_cross = df_cross[(df_cross.lag > 0) & (df_cross.calc_corr >0)]
df_cross = df_cross.drop('corr_rec', axis=1)

"""Calculation of auto correlations between all time series
"""
df_auto = data.iloc[:,:2]
df_auto = df_auto.rename(columns={'crime': 'acrime','county': 'acounty'})
df_auto['corr_rec'] = data.apply(lambda x: auto_correlation_using_panda(x['value']),axis=1)
df_auto[['lag','calc_corr']] = pd.DataFrame(df_auto['corr_rec'].values.tolist(), index=df_auto.index)

df_auto = df_auto[(df_auto.lag > 0) & (df_auto.calc_corr !=0)]
df_auto = df_auto.drop('corr_rec', axis=1)
df_auto['corr_type'] = 'auto'

df_out = pd.concat([df_cross, df_auto], axis=0)

df_out = df_out.reset_index(drop=True)
df_out = df_out.reindex(df_out.calc_corr.abs().sort_values().index).reset_index(drop=True)
df_out = df_out.reset_index().sort_values(by=['acounty','acrime','index'],ascending=[True, True, False]).reset_index(drop=True)
df_out.drop('index',axis=1).to_csv('Ranked_correlation_v1.csv')


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

df1.drop(['county'],axis=1).to_csv('Corr_with_coord_v1.csv')