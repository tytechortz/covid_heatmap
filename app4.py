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
import shapefile
from json import dumps



# Load mapbox token
mapbox_access_token = open(".mapbox_token").read()

# Build Dash layout
app = dash.Dash(__name__)






geo_df = gpd.read_file('Census_Tracts_2020_SHAPE_WGS/Census_Tracts_2020_WGS.shp')
# print(geo_df)
geo_df.to_file('tracts.geojson', driver="GeoJSON")
print(geo_df.columns)
# reader = shapefile.Reader('/Users/jamesswank/Python_projects/covid_heatmap/Census_Tracts_2020_SHAPE_WGS/Census_Tracts_2020_WGS.shp')
# fields = reader.fields[1:]
# field_names = [field[0] for field in fields]
# buffer = []
# for sr in reader.shapeRecords():
#     atr = dict(zip(field_names, sr.record))
#     geom = sr.shape.__geo_interface__
#     buffer.append(dict(type="Feature", \
#     geometry=geom, properties=atr)) 
   
#     # write the GeoJSON file
   
# geojson = open("pyshp-demo.json", "w")
# geojson.write(dumps({"type": "FeatureCollection", "features": buffer}, indent=2) + "\n")
# geojson.close()


with open('pyshp-demo.json') as json_file:
    jdata = json_file.read()
    topoJSON = json.loads(jdata)

sources=[]
for feat in topoJSON['features']: 
        sources.append({"type": "FeatureCollection", 'features': [feat]})

print(sources)

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

    def fill_color():
        for k in range(len(sources)):
            sources[k]['features'][0]['properties']['COLOR'] = 'lightgreen'
                           
    fill_color()

    layers=[dict(sourcetype = 'json',
        source =sources[k],
        below="water", 
        type = 'fill',
        color = sources[k]['features'][0]['properties']['COLOR'],
        opacity = 0.5
        ) for k in range(len(sources))] 
    # print(layers[0])

    data = [dict(
        lat = 39.5,
        lon = -104.5,
        # text = df_smr['name'],
        # hoverinfo = 'text',
        type = 'scattermapbox',
        # customdata = df['uid'],
        mode = 'markers',
        marker = dict(size=10, color='red')
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
            "style": "light",
            "layers": layers
        },
        "margin": {"r": 0, "t": 0, "l": 0, "b": 0, "pad": 0},
    }

    fig = dict(data=data, layout=layout)
    return fig






if __name__ == '__main__':
    app.run_server(port=8080,debug=True)