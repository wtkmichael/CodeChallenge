#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import pandas as pd
from bokeh.io import curdoc
from bokeh.layouts import widgetbox, Column
from bokeh.models.widgets import Select
from bokeh.models import (
    GMapPlot, GMapOptions, ColumnDataSource, Circle, DataRange1d, PanTool, WheelZoomTool, BoxSelectTool,
    HoverTool, ResetTool
)

# Sets color depending on density:
colors = ["#0000ff","#0080ff","#00ffff","#00ff80","#00ff00","#80ff00","#ffff00","#ff8000","#ff0000"] 
numcolors = len(colors)


df = pd.read_csv('Corr_with_coord.csv')
df['color'] = df.apply(lambda x: colors[int((x['calc_cor']+1)/2*9-1)],axis=1)

county_list = df.acounty.unique().tolist()
crime_list = df.acrime.unique().tolist()

county_select = Select(title="LSOA Name:", value=county_list[0], options=county_list)
crime_select = Select(title="Crime:", value=crime_list[0], options=crime_list)

print df.head()
# Default data source
df2 = df[(df.acounty==county_select.value) & (df.acrime == crime_select.value)]
source = ColumnDataSource(data=dict(
        acounty = df2.acounty,
        acrime = df2.acrime,
        county = df2.bcounty,
        crime = df2.bcrime,
        lag = df2.lag,
        calc_cor = df2.calc_cor,
        latitude= df2.latitude,
        longitude = df2.longitude,
        size_mult = df2.size_mult,
        color = df2.color))

map_options = GMapOptions(lat=51.5, lng=-0.11, map_type="terrain", zoom=10)
    
plot = GMapPlot(
    x_range=DataRange1d(), y_range=DataRange1d(), map_options=map_options)
    
plot.title.text = "London Crime Correlation Heatmap"

# For GMaps to function, Google requires you obtain and enable an API key:
plot.api_key = "AIzaSyDtqvTUngIFXhplF4PPjcnJzCqy-it2OmE"
    
hover = HoverTool(tooltips=[("CountySel", "@acounty"),
                            ("CountyComp", "@county"),
                            ("Crime", "@acrime"),
                            ("Lag","@lag")])
circle = Circle(x="longitude", y="latitude", size="size_mult", fill_color="color", fill_alpha=0.8, line_color=None)
plot.add_glyph(source, circle)

plot.add_tools(ResetTool(), PanTool(), WheelZoomTool(), BoxSelectTool(),hover)
 
def generic_update(attr,old, new):
    global df, colors
    df2 = df[(df.acounty==county_select.value) & (df.acrime == crime_select.value)]
    source.data = dict(
        acounty = df2.acounty,
        acrime = df2.acrime,
        county = df2.bcounty,
        crime = df2.bcrime,
        lag = df2.lag,
        calc_cor = df2.calc_cor,
        latitude= df2.latitude,
        longitude = df2.longitude,
        size_mult = df2.size_mult,
        color = df2.color)

county_select.on_change('value', generic_update)
crime_select.on_change('value', generic_update)

layout = Column(widgetbox(county_select, crime_select),plot)
curdoc().add_root(layout)