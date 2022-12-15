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

# pop = pop.set_index('TRACTCE20')
print(pop)
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
    print(years)

    fig = px.choropleth_mapbox(pop, 
                            geojson=gdf.__geo_interface__,
                            featureidkey='properties.TRACTCE20',
                            # hover_name='Geography',
                            # locations= 'TOTALPOP',
                            color='TOTALPOP',
                            # title="Census - " + topic,
                            # category_orders={topic_str:('1','2','3','4')},
                            # color_discrete_map=color_map,
                            opacity=1,
                            zoom=5.5,   
                            center=dict(
                                lat=46.560,
                                lon=-66.112
                            ))

    fig.update_layout(mapbox_style="carto-positron")

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