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

dataframe = pd.read_csv('data/Animal Rescue incidents attended by LFB from Jan 2009.csv', encoding='ISO-8859-1')

# %%

dataframe['DateTimeOfCall'] = pd.to_datetime(dataframe['DateTimeOfCall'])

dataframe['Easting_m'] = dataframe['Easting_m'].fillna(dataframe['Easting_rounded'])
dataframe['Northing_m'] = dataframe['Northing_m'].fillna(dataframe['Northing_rounded'])

# %%

from pyproj import Proj, transform

east_north_prj = Proj('epsg:27700')
mercator_proj = Proj('epsg:3857')
long_lat_proj = Proj('epsg:4326')

# %%

dataframe['mercator'] = dataframe.apply(
    lambda row: transform(east_north_prj, mercator_proj, row['Easting_m'], row['Northing_m']),
    axis=1
)

# %%

dataframe['longlat'] = dataframe.apply(
    lambda row: transform(east_north_prj, long_lat_proj, row['Easting_m'], row['Northing_m']),
    axis=1
)

# %%

dataframe[['x_mercator', 'y_mercator']] = pd.DataFrame(dataframe['mercator'].tolist(), index=dataframe.index)

dataframe['Easting_m'] = dataframe['Easting_m'].fillna(dataframe['Easting_rounded'])
dataframe['Northing_m'] = dataframe['Northing_m'].fillna(dataframe['Northing_rounded'])

# %%

dataframe[['x_mercator', 'y_mercator']] = pd.DataFrame(dataframe['mercator'].tolist(), index=dataframe.index)

# %%

dataframe.to_csv('processed.csv')

# %%

dataframe = pd.read_csv('processed.csv')

# %%
dataframe = dataframe[['AnimalGroupParent', 'x_mercator', 'y_mercator']]


# %%

tile_provider = get_provider(Vendors.STAMEN_TONER)
_tools_to_show = 'box_zoom,pan,save,hover,reset,tap,wheel_zoom'     

m = figure(
    title='Categories of animals',
    plot_width=900,
    plot_height=725,
    x_range=(-65000, 50000),
    y_range=(6674123, 6743961),
    x_axis_type='mercator',
    y_axis_type='mercator',
    tools=_tools_to_show
)

m.border_fill_color = "#2C3033"
m.title.text_color ='white'
m.xaxis.major_label_text_color = 'white'
m.xaxis.major_tick_line_color = 'white'
m.xaxis.minor_tick_line_color = 'white'
m.xaxis.axis_line_color = 'white'
m.yaxis.major_label_text_color = 'white'
m.yaxis.major_tick_line_color = 'white'
m.yaxis.minor_tick_line_color = 'white'
m.yaxis.axis_line_color = 'white'
m.xgrid.grid_line_color = 'white'
m.ygrid.grid_line_color = 'white'
m.legend.background_fill_alpha = 0.0
m.legend.border_line_alpha = 0.0
m.legend.label_text_color = "white"
m.background_fill_color = "#2C3033"
# m.background_fill_alpha = 0.5
m.xgrid.grid_line_color = "white"
m.xgrid.grid_line_alpha = 0.1
m.ygrid.grid_line_color = "white"
m.ygrid.grid_line_alpha = 0.1
m.xaxis.axis_label_text_color = 'white'
p.yaxis.axis_label_text_color = 'white'

m.toolbar.active_scroll = m.select_one(WheelZoomTool)

m.add_tile(tile_provider)

source = ColumnDataSource(dataframe)

species = dataframe['AnimalGroupParent'].unique()
markers = ['hex'] * len(species)

scatters = {}
items = []

cmap = viridis(len(species))

counter = 0

for index, animal in enumerate(species):
    source = ColumnDataSource(dataframe.loc[dataframe['AnimalGroupParent'] == animal])
    scatters[animal] = m.scatter(
        x='x_mercator', y='y_mercator',
        source=source,
        fill_alpha=0.3,
        size=15,
        color=cmap[index],
        marker=factor_mark('AnimalGroupParent', markers, species),
        visible=False, muted_alpha=0.00)
    items.append((animal, [scatters[animal]]))
    
    hover = m.select(dict(type=HoverTool))
    hover.tooltips = [("Animal", "@AnimalGroupParent"),]
    hover.mode = 'mouse'

# m.scatter(
#     x='x_mercator', y='y_mercator',
#     source=source,
#     legend_field="AnimalGroupParent",
#     fill_alpha=0.5,
#     size=20,
#     marker=factor_mark('AnimalGroupParent', markers, species),
#     color=factor_cmap('AnimalGroupParent', viridis(len(species)), species)
# )

legend = Legend(items=items)
m.add_layout(legend)
m.legend.location = 'top_left'
m.legend.click_policy = 'hide'
m.legend.label_text_font_size = "9px"
m.toolbar.logo = None
m.toolbar_location = None
# m.legend.orientation = "ver"

maps = m

output_file("categories.html")
    
show(m)

# %%



# %%

dataframe = pd.read_csv('processed.csv')

dataframe['DateTimeOfCall'] = pd.to_datetime(dataframe['DateTimeOfCall'])

# %%

dataframe['DayOfWeek'] = dataframe['DateTimeOfCall'].dt.dayofweek
dataframe['Day'] = dataframe['DateTimeOfCall'].dt.day
dataframe['Month'] = dataframe['DateTimeOfCall'].dt.month

dataframe['Hour'] = dataframe['DateTimeOfCall'].dt.hour

dataframe['AnimalGroupParent'] = dataframe['AnimalGroupParent'].replace('cat', 'Cat')


# %%

animals = pd.DataFrame(dataframe[['AnimalGroupParent', 'DayOfWeek']])
animals = animals.groupby(['DayOfWeek', 'AnimalGroupParent']).size().unstack()
animals = animals.reindex(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])

# %%

animal_list = ['Bird', 'Budgie', 'Bull', 'Cat', 'Cow', 'Deer', 'Dog', 'Ferret', 'Fish',
       'Fox', 'Goat', 'Hamster', 'Hedgehog', 'Horse', 'Lamb', 'Lizard',
       'Pigeon', 'Rabbit', 'Sheep', 'Snake', 'Squirrel', 'Tortoise',
       'Unknown - Animal rescue from below ground - Farm animal',
       'Unknown - Animal rescue from water - Farm animal',
       'Unknown - Domestic Animal Or Pet', 'Unknown - Heavy Livestock Animal',
       'Unknown - Wild Animal']

animals = dataframe[['AnimalGroupParent', 'Hour', 'IncidentNumber']]
animals = animals.groupby(['Hour', 'AnimalGroupParent']).count().reset_index()


animals['Normalisation'] = animals.reset_index().apply(
    lambda x: x['IncidentNumber'] / animals.groupby('AnimalGroupParent').sum().loc[x['AnimalGroupParent'], 'IncidentNumber'],
    axis=1
)
animals = animals.drop(['IncidentNumber'], axis=1)

animals_pivot = pd.pivot_table(animals, index='Hour', columns='AnimalGroupParent')
animals_pivot.columns = animals_pivot.columns.droplevel(0)

# %%

# animals_pivot.columns = ['Bird', 'Budgie', 'Bull', 'Cat', 'Cow', 'Deer', 'Dog', 'Ferret', 'Fish',
#        'Fox', 'Goat', 'Hamster', 'Hedgehog', 'Horse', 'Lamb', 'Lizard',
#        'Pigeon', 'Rabbit', 'Sheep', 'Snake', 'Squirrel', 'Tortoise',
#        'Unknown - Animal rescue from below ground - Farm animal',
#        'Unknown - Animal rescue from water - Farm animal',
#        'Unknown - Domestic Animal Or Pet', 'Unknown - Heavy Livestock Animal',
#        'Unknown - Wild Animal']

animals_pivot.index = animals_pivot.index.map(str)

source = ColumnDataSource(animals_pivot)
p = figure(
    x_range=FactorRange(factors=animals_pivot.index),
    plot_height=1000,
    plot_width=1800, toolbar_location=None,
    title='Incidents per hour', x_axis_label='Hour of the day', y_axis_label='Relative frequency')
# Using seaborn colour palette in the Hex format for colouring each category of the crime in each iteration.
cmap = sns.color_palette('husl', len(animals_pivot.columns)).as_hex()

bar = {}
items = list()

for index, animal in enumerate(animal_list):
    bar[animal] = p.vbar(
        x='Hour', top=animal, source=source,
        width=0.6,
        color=cmap[index], fill_alpha=0.5,
        muted=False, muted_alpha=0.05)
    items.append((animal, [bar[animal]]))
    
# "Sticking" the bars to the x-axis
p.y_range.start = 0

output_file("distro.html")

legend = Legend(items=items)
p.add_layout(legend, 'right')
# p.legend.label_text_font_size = "8px"
p.legend.click_policy = 'mute'

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
p.legend.background_fill_alpha = 0.0
p.legend.border_line_alpha = 0.0
p.legend.label_text_color = "white"
p.background_fill_color = "#2C3033"
# p.background_fill_alpha = 0.5
p.xgrid.grid_line_color = "white"
p.xgrid.grid_line_alpha = 0.1
p.ygrid.grid_line_color = "white"
p.ygrid.grid_line_alpha = 0.1
p.xaxis.axis_label_text_color = 'white'
p.yaxis.axis_label_text_color = 'white'

show(p)



# %%

animals = pd.DataFrame(dataframe[['AnimalGroupParent', 'DayOfWeek']])
animals = animals.groupby(['DayOfWeek', 'AnimalGroupParent']).size().unstack()
animals.index = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']



animal_list = ['Cat', 'Dog', 'Fox']

plots = []

# animals = animals.reset_index()

for animal in animal_list:
    
    df = pd.DataFrame(animals[animal]).reset_index()
    
    print(df)
    
    source = ColumnDataSource(df)
    
    p = figure(
        x_range=FactorRange(factors=df['index']),
        plot_height=400,
        plot_width=500,
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
    p.legend.background_fill_alpha = 0.0
    p.legend.border_line_alpha = 0.0
    p.legend.label_text_color = "white"
    p.background_fill_color = "#2C3033"
    # p.background_fill_alpha = 0.5
    p.xgrid.grid_line_color = "white"
    p.xgrid.grid_line_alpha = 0.1
    p.ygrid.grid_line_color = "white"
    p.ygrid.grid_line_alpha = 0.1
    p.xaxis.axis_label_text_color = 'white'
    p.yaxis.axis_label_text_color = 'white'
    
    # p.y_range.start = 0
    p.y_range = Range1d(0, 500)
    p.toolbar.logo = None
    p.toolbar_location = None
    plots.append(p)
    
plots_new = []
        
animals_distro = gridplot(plots, ncols=4, merge_tools=False)

output_file("distro-animals.html")
show(animals_distro)
    
# %%
    
boroughs = pd.DataFrame(dataframe[['Borough', 'DayOfWeek']])
boroughs = boroughs.groupby(['DayOfWeek', 'Borough']).size().unstack()
boroughs.index = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']



borough_list = ['Croydon', 'Sutton', 'Hillingdon', 'Havering',
       'Barking and Dagenham', 'Waltham Forest', 'Redbridge', 'Hackney',
       'Bromley', 'Wandsworth', 'Southwark', 'Richmond upon Thames',
       'Lewisham', 'Lambeth', 'Tower Hamlets', 'Harrow', 'Barnet',
       'Westminster', 'Hounslow', 'Ealing', 'Camden',
       'Kingston upon Thames', 'Islington', 'Greenwich', 'Newham',
       'Bexley', 'Haringey', 'Hammersmith and Fulham',
       'Kensington and Chelsea', 'Epping Forest', 'Brent', 'Merton',
       'Enfield', 'City of London', 'Brentwood', 'Broxbourne',
       'Tandridge', 'HOUNSLOW', 'WANDSWORTH', 'TOWER HAMLETS', 'LEWISHAM',
       'HARINGEY', 'BROMLEY', 'CROYDON', 'EALING', 'NEWHAM', 'REDBRIDGE',
       'ENFIELD', 'HILLINGDON', 'GREENWICH', 'HAVERING', 'SUTTON',
       'BEXLEY', 'ISLINGTON', 'KENSINGTON AND CHELSEA', 'BRENT',
       'WALTHAM FOREST', 'KINGSTON UPON THAMES', 'HACKNEY', 'LAMBETH',
       'CAMDEN', 'BARNET', 'BARKING AND DAGENHAM', 'SOUTHWARK', 'MERTON',
       'HARROW', 'RICHMOND UPON THAMES', 'CITY OF LONDON',
       'HAMMERSMITH AND FULHAM', 'WESTMINSTER']

plots = []

# animals = animals.reset_index()

for index, borough in enumerate(borough_list[::-1]):
    if index == 6:
        break
    
    df = pd.DataFrame(boroughs[borough]).reset_index()
    
    print(df)
    
    source = ColumnDataSource(df)
    
    p = figure(
        x_range=FactorRange(factors=df['index']),
        plot_height=333,
        plot_width=600,
        toolbar_location=None,
        title='{} — Incidents per weekday'.format(borough),
        x_axis_label='Weekday',
        y_axis_label='Frequency'
    )
    
    p.vbar(
        x='index',
        top=borough,
        source=source,
        width=0.6,
        fill_alpha=0.5,
        color='#0CC6E8'
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
    p.legend.background_fill_alpha = 0.0
    p.legend.border_line_alpha = 0.0
    p.legend.label_text_color = "white"
    p.background_fill_color = "#2C3033"
    # p.background_fill_alpha = 0.5
    p.xgrid.grid_line_color = "white"
    p.xgrid.grid_line_alpha = 0.1
    p.ygrid.grid_line_color = "white"
    p.ygrid.grid_line_alpha = 0.1
    p.xaxis.axis_label_text_color = 'white'
    p.yaxis.axis_label_text_color = 'white'
    
    # p.y_range.start = 0
    p.y_range = Range1d(0, 40)
    p.toolbar.logo = None
    p.toolbar_location = None

    plots.append(p)
    
    
plots_new = []

for index, value in enumerate(plots):
    if index % 2 == 0:
        plots_new.append([plots[index], plots[index + 1]])
        
boroughs_distro = gridplot(plots_new, merge_tools=False)
output_file("density-boroughs.html")

# show(boroughs_distro)
    
    
    
# %%

plot = layout([
    [maps, animals_distro],
    [hexes]
    
])

show(plot)