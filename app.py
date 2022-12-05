import os
import time
from textwrap import dedent

import dash
from dash import dcc, html
from dash.dependencies import Input, Output

import dask

import holoviews as hv
import datashader as ds
from holoviews.plotting.plotly.dash import to_dash
from holoviews.operation.datashader import datashade
from plotly.colors import sequential

from datashader.colors import inferno, Hot

import datashader.transfer_functions as tf

import numpy as np
import pandas as pd
from distributed import Client


from pyproj import Transformer, Proj
import utm

from utils import (
    # compute_range_created_radio_hist,
    epsg_4326_to_3857,
    get_dataset,
    scheduler_url,
)

# Global initialization
client = None

def init_client():
    """
    This function must be called before any of the functions that require a client.
    """
    global client
    # Init client
    print(f"Connecting to cluster at {scheduler_url} ... ", end="")
    client = Client(scheduler_url)
    print("done")

# Colors
bgcolor = "#f3f3f1"  # mapbox light map land color

# Figure template
row_heights = [150, 500, 300]
template = {"layout": {"paper_bgcolor": bgcolor, "plot_bgcolor": bgcolor}}

def blank_fig(height):
    """
    Build blank figure with the requested height
    """
    return {
        "data": [],
        "layout": {
            "height": height,
            "template": template,
            "xaxis": {"visible": False},
            "yaxis": {"visible": False},
        },
    }

# Load mapbox token
mapbox_access_token = open(".mapbox_token").read()

def build_modal_info_overlay(id, side, content):
    """
    Build div representing the info overlay for a plot panel
    """
    div = html.Div(
        [  # modal div
            html.Div(
                [  # content div
                    html.Div(
                        [
                            html.H4(
                                [
                                    "Info",
                                    html.Img(
                                        id=f"close-{id}-modal",
                                        src="assets/times-circle-solid.svg",
                                        n_clicks=0,
                                        className="info-icon",
                                        style={"margin": 0},
                                    ),
                                ],
                                className="container_title",
                                style={"color": "white"},
                            ),
                            dcc.Markdown(content),
                        ]
                    )
                ],
                className=f"modal-content {side}",
            ),
            html.Div(className="modal"),
        ],
        id=f"{id}-modal",
        style={"display": "none"},
    )

    return div


# Build Dash layout
app = dash.Dash(__name__)

app.layout = html.Div([
    html.Div([
        html.H4("Covid-19 Testing")
    ],
        className = 'row'
    ),
    html.Div([
        build_modal_info_overlay(
            "indicator",
            "bottom",
            dedent(
                """
                Words
                """
            ),
        ),
    ]),
    html.Div([
        build_modal_info_overlay(
            "placeholder",
            "bottom",
            dedent(
                """
                Words
                """
            ),
        ),
    ]),
    html.Div([
        build_modal_info_overlay(
            "map",
            "bottom",
            dedent(
                """
                Words
                """
            ),
        ),
    ]),
    html.Div([
        html.Div([
            html.H4([
                "Selected Tests",
                html.Img(
                    id="show-indicator-modal",
                    src="assets/question-circle-solid.svg",
                    n_clicks=0,
                    className="info-icon",
                ),
            ]),
        ],
            className="container_title",
        ),
        dcc.Loading(
            dcc.Graph(
                id="indicator-graph",
                figure=blank_fig(row_heights[0]),
                config={"displayModeBar": False},
            ),
            className="svg-container",
            style={"height": 150},
        ),
        html.Div(
            children=[
                html.Button(
                    "Reset All",
                    id="clear-all",
                    className="reset-button",
                ),
            ]
        ),
    ],
        className="six columns pretty_container",
        id="indicator-div",
    ),
    html.Div([
        html.Div([
            html.H4([
                "Placeholder",
                html.Img(
                    id="show-placeholder-modal",
                    src="assets/question-circle-solid.svg",
                    n_clicks=0,
                    className="info-icon",
                ),
            ]),
        ],
            className="container_title",
        ),
        dcc.Loading(
            dcc.Graph(
                id="placeholder-graph",
                figure=blank_fig(row_heights[0]),
                config={"displayModeBar": False},
            ),
            className="svg-container",
            style={"height": 150},
        ),
        html.Div(
            children=[
                html.Button(
                    "Reset All",
                    id="clear-placeholder",
                    className="reset-button",
                ),
            ]
        ),
    ],
        className="six columns pretty_container",
        id="placeholder-div",
    ),
    html.Div([
        html.H4([
            "Locations",
            html.Img(
                id="show-map-modal",
                src="assets/question-circle-solid.svg",
                className="info-icon",
            ),
        ],
            className="container_title",
        ),
        dcc.Graph(
            id="map-graph",
            figure=blank_fig(row_heights[1]),
            config={"displayModeBar": False},
        ),
        html.Button(
            "Reset View", id="reset-map", className="reset-button"
        ),
    ],
        className="twelve columns pretty_container",
        style={
            "width": "98%",
            "margin-right": "0",
        },
        id="map-div",
    )
])

# Create show/hide callbacks for each info modal
for id in ["indicator", "placeholder", "map"]:

    @app.callback(
        [Output(f"{id}-modal", "style"), Output(f"{id}-div", "style")],
        [Input(f"show-{id}-modal", "n_clicks"), Input(f"close-{id}-modal", "n_clicks")],
    )
    def toggle_modal(n_show, n_close):
        ctx = dash.callback_context
        if ctx.triggered and ctx.triggered[0]["prop_id"].startswith("show-"):
            return {"display": "block"}, {"zIndex": 1003}
        else:
            return {"display": "none"}, {"zIndex": 0}


# Create clear/reset button callbacks
@app.callback(
    Output("map-graph", "relayoutData"),
    [Input("reset-map", "n_clicks"), Input("clear-all", "n_clicks")],
)
def reset_map(*args):
    return None

@app.callback(
    Output("indicator-graph", "figure"),
    Output("map-graph", "figure"),
    Input("map-graph", "relayoutData"))
def update_plots(relayout_data):

    # test_df = get_dataset(client, "cell_towers_ddf")
    df = pd.read_csv('/Users/jamesswank/Desktop/TestingData_coordinates.csv')
    df["tests"] = 1

    trans = Transformer.from_crs(
        "epsg:4326",
        "+proj=utm +zone=13N +ellps=WGS84",
        always_xy=True,
    )
    

    x_3857,  y_3857 = trans.transform(df.geolongitude.values, df.geolatitude.values)
    df = df.assign(x_3857=x_3857, y_3857=y_3857)
  

    coordinates_4326 = relayout_data and relayout_data.get("mapbox._derived", {}).get(
        "coordinates", None
    )
    # print("coords_4326 = {}".format(coordinates_4326))

    data_3857 = [[df['y_3857'].min(), df['x_3857'].min()],
                [df['y_3857'].max(), df['x_3857'].max()]]
    # print("d3857={}".format(data_3857))
    

    data_center_3857 = [
            (data_3857[0][0] + data_3857[1][0]) / 2.0,
            (data_3857[0][1] + data_3857[1][1]) / 2.0,
    ]
    # print("dc3857={}".format(data_center_3857))
    # print(data_3857[0][0])

    data_4326 = utm.to_latlon(data_3857[0][1], data_3857[0][0], 13, 'S'), utm.to_latlon(data_3857[1][1], data_3857[1][0],13, 'S')
    
    # print("DATA 4326 = {}".format(data_4326))
    # print("this is {}".format(data_3857[0]))
    # print("that is {}".format(data_3857[1]))
    data_center_4326 = [utm.to_latlon(data_center_3857[1], data_center_3857[0], 13, 'S')]
    # data_center_4326 = [
    #     [
    #         (data_4326[0][0] + data_4326[1][0]) / 2.0,
    #         (data_4326[0][1] + data_4326[1][1]) / 2.0,
    #     ]
    # ]
    # print("data 4326 - {}".format(data_4326))
    # print(data_center_4326)

    if coordinates_4326:
        lons, lats = zip(*coordinates_4326)
        # print("lons-{}".format(lons))
        # print("lats-{}".format(lats))
        # print("data_4326 0 0 = {}".format(data_4326[0][0]))
        lon0, lon1 = max(min(lons), data_4326[0][1]), min(max(lons), data_4326[1][1])
        lat0, lat1 = max(min(lats), data_4326[0][0]), min(max(lats), data_4326[1][0])
        # print("lon0 = {} lat0 = {}".format(lon0, lat0))
        coordinates_4326 = [
            [lon0, lat0],
            [lon1, lat1],
        ]
        # print(coordinates_4326)
        # coordinates_3857 = epsg_4326_to_3857(coordinates_4326)
        coordinates_3857 = utm.from_latlon(coordinates_4326[0][1], coordinates_4326[0][0]), utm.from_latlon(coordinates_4326[1][1], coordinates_4326[1][0])
        coordinates_3857 = [[coordinates_3857[0][1], coordinates_3857[0][0]], [coordinates_3857[1][1], coordinates_3857[1][0]]]
        # print("Right Here = {}".format(coordinates_3857))

        # position = {}
        position = {
            "zoom": relayout_data.get("mapbox.zoom", None),
            # "zoom": 8,
            "center": relayout_data.get("mapbox.center", None),
            # "center": data_center_3857,
        }
    else:
        position = {
            "zoom": 8,
            "pitch": 0,
            "bearing": 0,
            "center": {"lon": data_center_4326[0][1], "lat": data_center_4326[0][0]},
        }
        coordinates_3857 = data_3857
        coordinates_4326 = data_4326
        # print("both-{}".format(coordinates_4326))
        # print("lat-{}".format(coordinates_4326[0][0]))
        # print("lon-{}".format(coordinates_4326[0][1]))

    new_coordinates = [
        [coordinates_4326[0][0], coordinates_4326[1][1]],
        [coordinates_4326[1][0], coordinates_4326[1][1]],
        [coordinates_4326[1][0], coordinates_4326[0][1]],
        [coordinates_4326[0][0], coordinates_4326[0][1]],
    ]

    # print("new = {}".format(new_coordinates))
    # print("C_3857 = {}".format(coordinates_3857))
    y_range, x_range = zip(*coordinates_3857)
    x0, x1 = x_range
    y0, y1 = y_range
    # print("x_range = {}".format(x_range))
    # print("y_range = {}".format(y_range))

    # Build query expressions
    query_expr_xy = (
        f"(x_3857 >= {x0}) & (x_3857 <= {x1}) & (y_3857 >= {y0}) & (y_3857 <= {y1})"
    )
    # print(query_expr_xy)
    query_expr_range_created_parts = []

    # Build dataframe containing rows that satisfy the range and created selections
    if query_expr_range_created_parts:
        query_expr_range_created = " & ".join(query_expr_range_created_parts)
        ddf_selected_range_created = df.query(query_expr_range_created)
    else:
        ddf_selected_range_created = df

    # Build dataframe containing rows of towers within the map viewport
    df_xy = df.query(query_expr_xy) if query_expr_xy else df
    # (print("df_xy = {}".format(df_xy.head())))

    cvs = ds.Canvas(plot_width=700, plot_height=400, x_range=x_range, y_range=y_range)
    agg = cvs.points(
        ddf_selected_range_created, x="x_3857", y="y_3857", agg=ds.count("tests")
    )

    # Count the number of selected towers
    n_selected = int(agg.sum())

    # Build indicator figure
    n_selected_indicator = {
        "data": [
            {
                "type": "indicator",
                "value": n_selected,
                "number": {"font": {"color": "#263238"}},
            }
        ],
        "layout": {
            "template": template,
            "height": 150,
            "margin": {"l": 10, "r": 10, "t": 10, "b": 10},
        },
    }
  

    if n_selected == 0:
        # Nothing to display
        lat = []
        lon = []
        customdata = [None]
        marker = {}
        layers = []
    elif n_selected < 2000:
        print(n_selected)
        lat = df_xy['geolatitude']
        lon = df_xy['geolongitude']
        marker = {
            "color": "red",
            "size": 2,
            # "cmin": 0,
            # "cmax": 3
        }
        layers = []
    else:
        lat = df_xy['geolatitude']
        lon = df_xy['geolongitude']
        marker = {
            "color": "green",
            "size": 3
        }
        layers = []
    
    print(lat)
    map_graph = {
        "data": [
            {
                "type": "scattermapbox",
                "lat": lat,
                "lon": lon,
                # "customdata": customdata,
                "marker": marker
                # "hovertemplate": (
                #     "<b>%{customdata[2]}</b><br>"
                #     "MCC: %{customdata[3]}<br>"
                #     "MNC: %{customdata[4]}<br>"
                #     "radio: %{customdata[0]}<br>"
                #     "range: %{customdata[1]:,} m<br>"
                #     "created: %{customdata[5]}<br>"
                #     "status: %{customdata[6]}<br>"
                #     "longitude: %{lon:.3f}&deg;<br>"
                #     "latitude: %{lat:.3f}&deg;<br>"
                #     "<extra></extra>"
                # ),
            }
        ],
        "layout": {
            "template": template,
            "uirevision": True,
            "mapbox": {
                "style": "light",
                "accesstoken": mapbox_access_token,
                "layers": layers,
            },
            "margin": {"r": 0, "t": 0, "l": 0, "b": 0},
            "height": 500,
            "shapes": [
                {
                    "type": "rect",
                    "xref": "paper",
                    "yref": "paper",
                    "x0": 0,
                    "y0": 0,
                    "x1": 1,
                    "y1": 1,
                    "line": {
                        "width": 2,
                        "color": "#B0BEC5",
                    },
                }
            ],
        },
    }
    
    map_graph["layout"]["mapbox"].update(position)





    return n_selected_indicator, map_graph

if __name__ == '__main__':
    app.run_server(port=8000,debug=True)