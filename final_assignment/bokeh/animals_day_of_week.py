# %%
import numpy as np
import pandas as pd
from bokeh.tile_providers import get_provider, Vendors
from bokeh.models import ColumnDataSource, Toolbar, ToolbarBox, Legend, FactorRange, Range1d
from bokeh.io import output_file, show, reset_output
from bokeh.layouts import gridplot, layout
from bokeh.plotting import figure
from bokeh.transform import factor_cmap, factor_mark
from bokeh.palettes import viridis
from bokeh.models.tools import HoverTool, WheelZoomTool, PanTool
import seaborn as sns

# %%


dataframe = pd.read_csv('../data/processed.csv')

dataframe['DateTimeOfCall'] = pd.to_datetime(dataframe['DateTimeOfCall'])
dataframe['DayOfWeek'] = dataframe['DateTimeOfCall'].dt.dayofweek
dataframe['Day'] = dataframe['DateTimeOfCall'].dt.day
dataframe['Month'] = dataframe['DateTimeOfCall'].dt.month
dataframe['Hour'] = dataframe['DateTimeOfCall'].dt.hour

animals = pd.DataFrame(dataframe[['AnimalGroupParent', 'DayOfWeek']])
animals = animals.groupby(['DayOfWeek', 'AnimalGroupParent']).size().unstack()
animals.index = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']



animal_list = ['Bird', 'Budgie', 'Bull', 'Cat', 'Cow', 'Deer', 'Dog', 'Ferret', 'Fish',
       'Fox', 'Goat', 'Hamster', 'Hedgehog', 'Horse', 'Lamb', 'Lizard',
       'Pigeon', 'Rabbit', 'Sheep', 'Snake', 'Squirrel', 'Tortoise',
       'Unknown - Animal rescue from below ground - Farm animal',
       'Unknown - Animal rescue from water - Farm animal',
       'Unknown - Domestic Animal Or Pet', 'Unknown - Heavy Livestock Animal',
       'Unknown - Wild Animal'
]

plots = []

# animals = animals.reset_index()

for animal in animal_list:
    
    df = pd.DataFrame(animals[animal]).reset_index()
    
    source = ColumnDataSource(df)
    
    p = figure(
        x_range=FactorRange(factors=df['index']),
        plot_height=250,
        plot_width=600,
        toolbar_location=None,
        title='{} — Incidents per weekday'.format(animal),
        x_axis_label='Weekday',
        y_axis_label='Frequency'
    )
    
    p.vbar(
        x='index',
        top=animal,
        source=source,
        width=0.6,
        fill_alpha=0.5,
        color='#E84AA3'
    )
    
    p.border_fill_color = "#2C3033"
    p.title.text_color ='white'
    p.xaxis.major_label_text_color = 'white'
    p.xaxis.major_tick_line_color = 'white'
    p.xaxis.minor_tick_line_color = 'white'
    p.xaxis.axis_line_color = 'white'
    p.yaxis.major_label_text_color = 'white'
    p.yaxis.major_tick_line_color = 'white'
    p.yaxis.minor_tick_line_color = 'white'
    p.yaxis.axis_line_color = 'white'
    p.xgrid.grid_line_color = 'white'
    p.ygrid.grid_line_color = 'white'
    p.background_fill_color = "#2C3033"
    p.xgrid.grid_line_color = "white"
    p.xgrid.grid_line_alpha = 0.1
    p.ygrid.grid_line_color = "white"
    p.ygrid.grid_line_alpha = 0.1
    p.xaxis.axis_label_text_color = 'white'
    p.yaxis.axis_label_text_color = 'white'
    
    p.y_range.start = 0
    # p.y_range = Range1d(0, 500)
    p.toolbar.logo = None
    p.toolbar_location = None
    plots.append(p)
    
plots_new = []
        
animals_distro = gridplot(plots, ncols=3, merge_tools=False)

show(animals_distro)