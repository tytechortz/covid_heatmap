import dash
from dash import dcc, html

import numpy as np
import pandas as pd 
import geopandas as gpd
import plotly.express as px
from dash.dependencies import Input, Output, State

from geopandas.tools import sjoin

# Load mapbox token
mapbox_access_token = open(".mapbox_token").read()

# Build Dash layout
app = dash.Dash(__name__)

gdf = gpd.read_file('/Users/jamesswank/Python_projects/covid_heatmap/Census_Tracts_2020_SHAPE_WGS/Census_Tracts_2020_WGS.shp')
gdf = gdf.to_crs("epsg:4326")
gdf = gdf.set_geometry('geometry')
# print(gdf.columns)

pop = pd.read_csv('/Users/jamesswank/Python_projects/covid_heatmap/Tract_Data_2020.csv')
pop = pd.read_csv('/Users/jamesswank/Python_projects/covid_heatmap/Tract_Data_2020.csv')
pop['TRACTCE20'] = pop['TRACTCE20'].astype(str)
pop['TRACTCE20'] = pop['TRACTCE20'].str.zfill(6)
pop['TOTALPOP'] = pop['TOTALPOP'].astype(int)
pop['POPBIN'] = [1 if x<=3061 else 2 if 3061<x<=3817 else 3 if 3817<x<=5003 else 4 for x in pop['TOTALPOP']]
pop['COLOR'] = ['blue' if x==1 else 'green' if x==2 else 'orange' if x==3 else 'red' for x in pop['POPBIN']]

# print(pop)
# print(pop.columns)



# df_combo.set_geometry('geometry')
# print(df_combo.columns)

df_tests = pd.read_csv('/Users/jamesswank/Python_projects/covid_heatmap/TestingData_coordinates.csv')


df_tests = gpd.GeoDataFrame(df_tests, 
    geometry = gpd.points_from_xy(df_tests['geolongitude'], df_tests['geolatitude']))
df_tests = df_tests.set_crs('epsg:4326')
# print(df_tests.columns)

tIT = sjoin(df_tests, gdf, how='inner')
tIT = tIT.groupby('TRACTCE20').size().reset_index(name='count')


# print(df_tests.columns)
# print(tIT)

gdf = gdf.merge(tIT, on="TRACTCE20")
# df_combo = gdf.merge(tIT, on="TRACTCE20")
# print(gdf.columns)
gdf = gdf.merge(pop, on='TRACTCE20')
gdf['TpCap'] = gdf['count'] / gdf['TOTALPOP']
print(gdf.columns)


# print(pop.columns)
# df_combo = pd.merge(df_tests, gdf, on='TRACTCE20', how='outer')
# print(df_combo(type))
# defining colours
color_map = { '1': '#20fc03',
              '2': '#f0fc03',
              '3': '#fcb103',
              '4': '#fc0303'}

# pop = pop.set_index('TRACTCE20')
# print(pop)

factor = 0.9

app.layout = html.Div([
    html.H4("Arapahoe County Testing"),
    html.Div([
        html.Div([
            dcc.Slider(
            id = 'opacity',
            min = 0,
            max = 1,
            value = 1,
            # marks = {i for i in range(2020,2022)}
            ),
        ],
            className = 'four columns'
        ),
    ],
        className = 'row'
    ),
    dcc.Graph(id = 'ct'),
])

@app.callback(
    Output("ct", "figure"),
    Input("opacity", "value"))
def update_map(opacity):
    print(opacity)

    fig = px.choropleth_mapbox(gdf, 
                            geojson=gdf.__geo_interface__,
                            featureidkey='properties.TRACTCE20',
                            # hover_name='Geography',
                            locations= 'TRACTCE20',
                            color='TpCap',
                            color_continuous_scale = 
                                [[0, 'rgb(166,206,227, 0.5)'],
                                [0.05, 'rgb(31,120,180,0.5)'],
                                [0.2, 'rgb(178,223,138,0.5)'],
                                [0.5, 'rgb(51,160,44,0.5)'],
                                [factor, 'rgb(251,154,153,0.5)'],
                                [factor, 'rgb(227,26,28,0.5)'],
                                [1, 'rgb(227,26,28,0.5)']
                            ],
                            labels = {'TpCap': 'Tests Per Capita'},
                            # color_continuous_scale="Viridis",
                            # title="Census - " + topic,
                            # category_orders={'TOTALPOP':('1','2','3','4')},
                            # color_discrete_map=color_map,
                            opacity=opacity,
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