import json
import random
import pandas as pd
import geopandas as gpd
import plotly.graph_objects as go
import json
import numpy as np
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State


# Load mapbox token
mapbox_access_token = open(".mapbox_token").read()

# Build Dash layout
app = dash.Dash(__name__)





geodf = gpd.read_file('Census_Tracts_2020_SHAPE_UTM/Census_Tracts_2020_UTM.shp')
# print(geodf)

geodf = geodf.to_crs("WGS84")

# fig = go.Figure(go.Choroplethmapbox(geojson = json.loads(geodf.to_json())
# ))

# fig.update_layout(mapbox_style="open-street-map",
#                         height = 1000,
#                         autosize=True,
#                         margin={"r":0,"t":0,"l":0,"b":0},
#                         paper_bgcolor='#303030',
#                         plot_bgcolor='#303030',
#                         mapbox=dict(center=dict(lat=39.1699, lon=-104.9384),zoom=9),
                        # )


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
    # fig
])

# @app.callback(
#     Output('CT')
# )

@app.callback(
    Output('ct', 'figure'),
    Input('years', 'value'))
def update_figure(years):

    
    # geodf = geodf.to_crs("WGS84")
    print(geodf)

    df = geodf.to_json()

    print(df)
    layers=[dict(sourcetype = 'json',
        source = df,
        below="water", 
        type = 'fill',
        # color = sources[k]['features'][0]['properties']['COLOR'],
        opacity = 0.5),
        ]
    data = [dict(
        lat = 39.5,
        lon = -104.5,
        # text = df_smr['name'],
        hoverinfo = 'text',
        type = 'scattermapbox',
        # customdata = df['uid'],
        # marker = dict(size=df_smr['marker_size'],color='forestgreen',opacity=.5),
        )]
    layout = dict(
            mapbox = dict(
                accesstoken = mapbox_access_token,
                center = dict(lat=39.05, lon=-105.5),
                zoom = 5.85,
                style = 'light',
                layers = layers
            ),
            hovermode = 'closest',
            height = 450,
            margin = dict(r=0, l=0, t=0, b=0)
            )
    fig = dict(data=data, layout=layout)
    return fig





if __name__ == '__main__':
    app.run_server(port=8000,debug=True)