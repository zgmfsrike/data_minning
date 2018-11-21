import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

import math
from ast import literal_eval
import time
from datetime import datetime

from bokeh.plotting import figure, show, curdoc
from bokeh.models import ColumnDataSource, Range1d, LinearColorMapper, ColorBar, BasicTicker, CustomJS, DateSlider
from bokeh.layouts import layout, column, row
from bokeh.palettes import Spectral3, Viridis, Inferno256, Viridis256
from bokeh.tile_providers import CARTODBPOSITRON, STAMEN_TERRAIN

# How to run: $- bokeh serve --show bokeh-server.py
# Link data set file:
# https://www.dropbox.com/s/o889qz7gpzf0cdn/2015%20USA%20Weather%20Data%20FINAL.csv?dl=0


df = pd.read_csv('2015 USA Weather Data FINAL.csv',sep=';')
# df = df.drop_duplicates(subset='STATION_NAME', keep='first')
# remove row that have '0' statename
df = df[(df.StateName != '0')]
df = df.drop(['STATION', 'LATLONG', 'Zip', 'State'], axis = 1)
# df


def merc(Coords):
    Coordinates = literal_eval(Coords)
    lat = Coordinates[0]
    lon = Coordinates[1]
    
    r_major = 6378137.000
    x = r_major * math.radians(lon)
    scale = x/lon
    y = 180.0/math.pi * math.log(math.tan(math.pi/4.0 + 
        lat * (math.pi/180.0)/2.0)) * scale
    return (x, y)


df['Date'] = df['Date'].apply(lambda x: x.split()[0])

df['Location'] = df[['LATITUDE', 'LONGITUDE']].apply(lambda x : '({},{})'.format(x[0],x[1]), axis=1)
df['coords_x'] = df['Location'].apply(lambda x: merc(x)[0])
df['coords_y'] = df['Location'].apply(lambda x: merc(x)[1])


# print(source.data['index'][2])
# df.head()


TOOLS="hover,crosshair,pan,wheel_zoom,zoom_in,zoom_out,box_zoom,undo,redo,reset,tap,save,box_select,poly_select,lasso_select,"
# source = ColumnDataSource(data=dict(coords_x=[], coords_y=[], color=[])


# range bounds supplied in web mercator coordinates
# p = figure(x_range=(df['coords_x'].min(), df['coords_x'].max()), y_range=(df['coords_y'].min(), df['coords_y'].max()),x_axis_type="mercator", y_axis_type="mercator",tools=TOOLS )
# p.add_tile(CARTODBPOSITRON)

COLORS = Inferno256
# Viridis256
# Inferno256
N_COLORS = len(COLORS)

color_low = df['MinTemp'].min() - 5
color_high = df['MaxTemp'].max() + 5

# color_low = -50
# color_high = 100

def color_value(AvgTemp):
    return COLORS[int((AvgTemp - color_low) / (color_high - color_low) * N_COLORS)]
        
df['color'] = df['AvgTemp'].apply(lambda x: color_value(x))
colors = [x for x in df['color']]
# print(colors)

color_mapper = LinearColorMapper(palette="Inferno256", low=color_low, high=color_high)

# if color.value != 'None':
#     if len(set(df[color.value])) > N_SIZES:
#         groups = pd.qcut(df[color.value].values, N_COLORS, duplicates='drop')
#     else:
#         groups = pd.Categorical(df[color.value])
#     c = [COLORS[xx] for xx in groups.codes]
# print(c)

color_bar = ColorBar(color_mapper=color_mapper, border_line_color=None, location=(0,0))
# df



# กำหนด source
# source = df.head()
# source = ColumnDataSource(dict(coords_x=source['coords_x'], coords_y=source['coords_y'], color=df['color']))



# p.add_layout(color_bar, 'right')

# p.circle(x = source.data['coords_x'], y = source.data['coords_y'], fill_color = source.data['color'], line_color=source.data['color'], fill_alpha=0.4, size=5)

def create_figure():
    p = figure(x_range=(df['coords_x'].min(), df['coords_x'].max()), y_range=(df['coords_y'].min(), df['coords_y'].max()),x_axis_type="mercator", y_axis_type="mercator",tools=TOOLS )
    p.add_tile(CARTODBPOSITRON)

    # กำหนด source
    source = df.head()
    source = ColumnDataSource(dict(coords_x=source['coords_x'], coords_y=source['coords_y'], color=df['color']))


    p.add_layout(color_bar, 'right')

    date_s = time.strptime("{}".format(date_slider.value), "%Y-%m-%d")
    # print(date_s)

    temp_source = df[(df['Date'].apply(lambda x: (time.strptime(x, "%m/%d/%y") == date_s)))]
    # newdate1 = time.strptime("9/1/10", "%m/%d/%y")
    # newdate2 = time.strptime(datetime.utcfromtimestamp(date_slider.value).strftime('%m/%d/%y'), "%m/%d/%y")

    # newdate1 == newdate2

    # filteredList = df[newdate1 == newdate2]
    source.data = dict(coords_x=temp_source['coords_x'], coords_y=temp_source['coords_y'], color=temp_source['color'])
    # print(len(source.data['coords_x']))
    p.circle(x = source.data['coords_x'], y = source.data['coords_y'], fill_color = source.data['color'], line_color=source.data['color'], fill_alpha=0.4, size=5)
    return p

def update(attr, old, new):
    layout.children[0] = create_figure()

date_start = "9/8/15"
date_end = "9/10/15"
date_init = "9/9/15"

date_slider = DateSlider(start=date_start, end=date_end, value=date_init, step=1, title="Date")
# date_slider.js_on_change('value', callback)
date_slider.on_change('value', update)



layout = column(create_figure(), date_slider)

curdoc().add_root(layout)
curdoc().title = "Whether"