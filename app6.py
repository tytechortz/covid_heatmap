import numpy as np
import json
import plotly.graph_objs as go
import pandas as pd 
import geopandas as gpd

import dash
from dash import dcc, html

import plotly.express as px
from dash.dependencies import Input, Output, State




# Load mapbox token
mapbox_access_token = open(".mapbox_token").read()

gdf = gpd.read_file('/Users/jamesswank/Python_projects/covid_heatmap/Census_Tracts_2020_SHAPE_WGS/Census_Tracts_2020_WGS.shp')
gdf = gdf.to_crs("epsg:4326")
gdf = gdf.set_geometry('geometry')
gdf['TRACTCE20'].astype(str)

pop = pd.read_csv('/Users/jamesswank/Python_projects/covid_heatmap/Tract_Data_2020.csv')
pop['TRACTCE20'] = pop['TRACTCE20'].astype(str)
pop['TRACTCE20'] = pop['TRACTCE20'].str.zfill(6)
pop['TOTALPOP'] = pop['TOTALPOP'].astype(int)

t_gdf = gdf.merge(pop, on='TRACTCE20')

f = open('/Users/jamesswank/Python_projects/covid_heatmap/tracts.geojson')
geojson=json.load(f)

# Prepare a lookup dictionary for selecting highlight areas in geojson
CT_lookup = {feature['properties']['TRACTCE20']: feature
                for feature in geojson['features']}


# function to get the geojson file for highlighted area
def get_highlights(selections, geojson=geojson, district_lookup=CT_lookup):
    geojson_highlights = dict()
    for k in geojson.keys():
        if k != 'features':
            geojson_highlights[k] = geojson[k]
        else:
            geojson_highlights[k] = [CT_lookup[selection] for selection in selections]        
    return geojson_highlights

def get_figure(selections):
    # Base choropleth layer --------------#
    fig = px.choropleth_mapbox(t_gdf, geojson=geojson, 
                               color="TOTALPOP",                               
                               locations="TRACTCE20", 
                               featureidkey="properties.TRACTCE20",
                               opacity=0.5)

    # Second layer - Highlights ----------#
    if len(selections) > 0:
        # highlights contain the geojson information for only 
        # the selected districts
        highlights = get_highlights(selections)

        fig.add_trace(
            px.choropleth_mapbox(t_gdf, geojson=highlights, 
                                 color="TOTALPOP",
                                 locations="TRACTCE20", 
                                 featureidkey="properties.TRACTCE20",                                 
                                 opacity=1).data[0]
        )

    #------------------------------------#
    fig.update_layout(mapbox_style="carto-positron", 
                      mapbox_zoom=10.4,
                      mapbox_center={"lat": 39.65, "lon": -104.8},
                      margin={"r":0,"t":0,"l":0,"b":0},
                      uirevision='constant')
    
    return fig


selections = list(CT_lookup.keys())[:5]
fig = get_figure(selections)


# Build Dash layout
app = dash.Dash(__name__)

# Keep track of the clicked region by using the variable "selections" 
selections = set()

#-------------------------------#
app.layout = html.Div([    
    dcc.Graph(
        id='choropleth',
        figure=fig
    )
])

#-------------------------------#



@app.callback(
    Output('choropleth', 'figure'),
    [Input('choropleth', 'clickData')])
def update_figure(clickData):    
    if clickData is not None:            
        location = clickData['points'][0]['location']

        if location not in selections:
            selections.add(location)
        else:
            selections.remove(location)
        
    return get_figure(selections)

if __name__ == '__main__':
    app.run_server(port=8080,debug=True)