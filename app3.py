import dash
from dash import html
import holoviews as hv
from holoviews.plotting.plotly.dash import to_dash
from holoviews.operation.datashader import datashade
import pandas as pd
import numpy as np
from plotly.data import carshare
import colorcet as cc
from plotly.colors import sequential
from pyproj import Transformer
import utm


# Load mapbox token
mapbox_access_token = open(".mapbox_token").read()


df = pd.read_csv('/Users/jamesswank/Desktop/TestingData_coordinates.csv')

df["easting"], df["northing"] = hv.Tiles.lon_lat_to_easting_northing(
df["geolongitude"], df["geolatitude"]
)


# trans = Transformer.from_crs(
#         "epsg:4326",
#         "+proj=utm +zone=13N +ellps=WGS84",
#         always_xy=True,
#     )
    

# x_3857,  y_3857 = trans.transform(df.geolongitude.values, df.geolatitude.values)
# df = df.assign(x_3857=x_3857, y_3857=y_3857)
# print(df)

# Build Dataset and graphical elements
dataset = hv.Dataset(df)
points = hv.Points(
df, ["easting", "northing"]
).opts(color="crimson")
tiles = hv.Tiles().opts(mapboxstyle="dark", accesstoken=mapbox_access_token)
overlay = tiles * datashade(points, cmap=cc.fire)
overlay.opts(
title="Mapbox Datashader with %d points" % len(df),
width=800,
height=500
)

# Build App
app = dash.Dash(__name__)
components = to_dash(app, [overlay], reset_button=True)

app.layout = html.Div(
components.children
)

if __name__ == '__main__':
    app.run_server(port=8000,debug=True)



