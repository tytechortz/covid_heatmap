import dash
from dash import dcc, html

import numpy as np
import pandas as pd 
import geopandas as gpd
import plotly.express as px
from dash.dependencies import Input, Output, State

# Load mapbox token
mapbox_access_token = open(".mapbox_token").read()

# Build Dash layout
app = dash.Dash(__name__)

gdf = gpd.read_file('/Users/jamesswank/Python_projects/covid_heatmap/Census_Tracts_2020_SHAPE_WGS/Census_Tracts_2020_WGS.shp')
gdf = gdf.to_crs("epsg:4326")
gdf = gdf.set_geometry('geometry')
print(gdf)
pop = pd.read_csv('/Users/jamesswank/Python_projects/covid_heatmap/Tract_Data_2020.csv')

pop = pd.read_csv('/Users/jamesswank/Python_projects/covid_heatmap/Tract_Data_2020.csv')
pop['TRACTCE20'] = pop['TRACTCE20'].astype(str)
pop['TRACTCE20'] = pop['TRACTCE20'].str.zfill(6)
pop['TOTALPOP'] = pop['TOTALPOP'].astype(int)
pop['POPBIN'] = [1 if x<=3061 else 2 if 3061<x<=3817 else 3 if 3817<x<=5003 else 4 for x in pop['TOTALPOP']]
pop['COLOR'] = ['blue' if x==1 else 'green' if x==2 else 'orange' if x==3 else 'red' for x in pop['POPBIN']]

print(pop.columns)
# df_combo = pd.merge(pop, gdf, on='TRACTCE20', how='outer')

# defining colours
color_map = { '1': '#20fc03',
              '2': '#f0fc03',
              '3': '#fcb103',
              '4': '#fc0303'}

# pop = pop.set_index('TRACTCE20')
print(pop)
app.layout = html.Div([
    html.H4("Arapahoe County Testing"),
    html.Div([
        dcc.RangeSlider(
        id = 'years',
        min = 2020,
        max = 2023,
        # marks = {i for i in range(2020,2022)}
        ),
    ]),
    dcc.Graph(id = 'ct'),
])

@app.callback(
    Output("ct", "figure"),
    Input("years", "value"))
def update_map(years):
    print(years)

    fig = px.choropleth_mapbox(pop, 
                            geojson=gdf.__geo_interface__,
                            featureidkey='properties.TRACTCE20',
                            # hover_name='Geography',
                            locations= 'TRACTCE20',
                            color='TOTALPOP',
                            # title="Census - " + topic,
                            # category_orders={'TOTALPOP':('1','2','3','4')},
                            # color_discrete_map=color_map,
                            opacity=1,
                            zoom=10,   
                            center=dict(
                                lat=39.66,
                                lon=-104.85
                            ))

    fig.update_layout(mapbox_style="carto-positron",margin={"r":0,"t":0,"l":0,"b":0})

    fig.update_layout(
        mapbox={'layers': [{
            'source': gdf.__geo_interface__,
            'type': "fill", 'below': "traces", 'color': "#dedede",
            'opacity': 0.3
        }]}
    )

    return fig



if __name__ == '__main__':
    app.run_server(port=8080,debug=True)