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

dataframe.to_csv('data/processed.csv')

# %%

dataframe = pd.read_csv('data/processed.csv')

# %%
dataframe = dataframe[['AnimalGroupParent', 'x_mercator', 'y_mercator']]
dataframe['AnimalGroupParent'] = dataframe['AnimalGroupParent'].str.replace('cat', 'Cat')


# %%

tile_provider = get_provider(Vendors.STAMEN_TONER)
_tools_to_show = 'box_zoom,pan,save,hover,reset,tap,wheel_zoom'     

m = figure(
    title='Categories of animals',
    plot_width=880,
    plot_height=700,
    x_range=(-80000, 10000),
    y_range=(6654123, 6763961),
    x_axis_type='mercator',
    y_axis_type='mercator',
    tools=_tools_to_show
)

m.toolbar.active_scroll = m.select_one(WheelZoomTool)

m.add_tile(tile_provider)

source = ColumnDataSource(dataframe)

species = dataframe['AnimalGroupParent'].unique()
species.sort()
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

legend = Legend(items=items)
m.add_layout(legend)
m.legend.location = 'top_left'
m.legend.click_policy = 'hide'
m.legend.label_text_font_size = "10px"
m.toolbar.logo = None
m.toolbar_location = None
# m.legend.orientation = "ver"

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
m.legend.border_line_alpha = 0.0
m.background_fill_color = "#2C3033"
m.background_fill_alpha = 0.5
m.xgrid.grid_line_color = "white"
m.xgrid.grid_line_alpha = 0.1
m.ygrid.grid_line_color = "white"
m.ygrid.grid_line_alpha = 0.1
m.xaxis.axis_label_text_color = 'white'
m.yaxis.axis_label_text_color = 'white'

output_file("output/categories.html")
    
show(m)

# %%