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


# Load mapbox token
mapbox_access_token = open(".mapbox_token").read()

# Build Dash layout
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H4("Here We Go")
])




geodf = gpd.read_file('Census_Tracts_2020_SHAPE_UTM/Census_Tracts_2020_UTM.shp')
print(geodf)

geodf = geodf.to_crs("WGS84")

fig = go.Figure(go.Choroplethmapbox(geojson = json.loads(geodf.to_json())
))

fig.update_layout(mapbox_style="open-street-map",
                        height = 1000,
                        autosize=True,
                        margin={"r":0,"t":0,"l":0,"b":0},
                        paper_bgcolor='#303030',
                        plot_bgcolor='#303030',
                        mapbox=dict(center=dict(lat=39.1699, lon=-104.9384),zoom=9),
                        )


fig


if __name__ == '__main__':
    app.run_server(port=8000,debug=True)