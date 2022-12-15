import json
import random
import pandas as pd
import geopandas as gpd
import plotly.graph_objects as go
import plotly.express as px
import json
import numpy as np
import dash
from dash import dcc, html
# import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.express as px
from json import dumps
from geopandas.tools import sjoin
from shapely.geometry import Point



# Load mapbox token
mapbox_access_token = open(".mapbox_token").read()

# Build Dash layout
app = dash.Dash(__name__)


gdf = gpd.read_file('/Users/jamesswank/Python_projects/covid_heatmap/Census_Tracts_2020_SHAPE_WGS/Census_Tracts_2020_WGS.shp')
# print(df)
# print(gdf.crs)
gdf = gdf.to_crs("epsg:4326")
# print(gdf.crs)
# print(type(gdf))

gdf = gdf.set_geometry('geometry')
gdf['centroid'] = gdf['geometry'].centroid
# gdf['id'] = range(1, len(gdf) + 1)
# gdf = gdf.reset_index()
print(gdf)

pop = pd.read_csv('/Users/jamesswank/Python_projects/covid_heatmap/Tract_Data_2020.csv')
pop['TRACTCE20'] = pop['TRACTCE20'].astype(str)
pop['TRACTCE20'] = pop['TRACTCE20'].str.zfill(6)
pop['TOTALPOP'] = pop['TOTALPOP'].astype(int)
pop['POPBIN'] = [1 if x<=3061 else 2 if 3061<x<=3817 else 3 if 3817<x<=5003 else 4 for x in pop['TOTALPOP']]
pop['COLOR'] = ['blue' if x==1 else 'green' if x==2 else 'orange' if x==3 else 'red' for x in pop['POPBIN']]

print(pop.columns)
# df_combo = pd.merge(pop, gdf, on='TRACTCE20', how='outer')
# print(df_combo.columns)
# df_combo.set_geometry('geometry')

df_tests = pd.read_csv('/Users/jamesswank/Python_projects/covid_heatmap/TestingData_coordinates.csv')
df_tests = gpd.GeoDataFrame(df_tests,
    geometry = gpd.points_from_xy(df_tests['geolongitude'], df_tests['geolatitude']))

df_tests.crs = "EPSG:4326"
# print(df_tests.columns)
# defining colours
color_map = { '1': '#20fc03',
              '2': '#f0fc03',
              '3': '#fcb103',
              '4': '#fc0303'}


# points = df_combo.centroid
# # Define new columns 
# pop['lat'] = points.apply(lambda x : x.y if x else np.nan)
# pop['lon'] = points.apply(lambda x : x.x if x else np.nan)


app.layout = html.Div([
    html.H4("Here We Go"),
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

    fig = px.choropleth_mapbox(pop, 
                            geojson=gdf.__geo_interface__,
                            featureidkey='properties.TRACTCE20',
                            hover_name='TOTALPOP',
                            locations='TRACTCE20',
                            color='TOTALPOP',
                            #    title="Census - " + topic,
                            # category_orders={'TOTALPOP':('1','2','3','4')},
                            color_discrete_map=color_map,
                            opacity=1,
                            zoom=5.5,      
                            center=dict(
                                        lat=46.560,
                                        lon=-66.112
                                        )
                            )

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