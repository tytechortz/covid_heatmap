import json
import random
import pandas as pd
import geopandas as gpd
import plotly.graph_objects as go
import json
import numpy as np
import dash
from dash import dcc, html
# import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.express as px



# Load mapbox token
mapbox_access_token = open(".mapbox_token").read()

# Build Dash layout
app = dash.Dash(__name__)





geo_df = gpd.read_file('Census_Tracts_2020_SHAPE_UTM/Census_Tracts_2020_UTM.shp')
# print(geodf)

geo_df = geo_df.to_crs("WGS84")
tracts = geo_df.to_json()
# print(type(tracts))
print(geo_df.columns.values)
# print(geo_df)
# print(tracts.keys())



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

    layers = [dict(sourcetype = "json",
        source = json.loads(geo_df.geometry.to_json()),

    )]
    print(layers[0])

    data = [dict(
        lat = 39.5,
        lon = -104.5,
        # text = df_smr['name'],
        # hoverinfo = 'text',
        type = 'scattermapbox',
        # customdata = df['uid'],
        # marker = dict(size=df_smr['marker_size'],color='forestgreen',opacity=.5),
        )]

    layout = {
        "autosize": True,
        "datarevision": 0,
        "hovermode": "closest",
        "mapbox": {
            "accesstoken": mapbox_access_token,
            "bearing": 0,
            "center": {"lat": 39.6050991, "lon": -104.4052438},
            "pitch": 0,
            # "opacity": 0.2,
            "zoom": 8,
            "style": "open-street-map",
            "layers": layers
        },
        "margin": {"r": 0, "t": 0, "l": 0, "b": 0, "pad": 0},
    }

    fig = dict(data=data, layout=layout)
    return fig






if __name__ == '__main__':
    app.run_server(port=8080,debug=True)