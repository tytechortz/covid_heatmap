import dash
from dash import dcc, html
from dash.dependencies import Input, Output

from pyproj import Transformer
import utm

import pandas as pd

from textwrap import dedent

import holoviews as hv
from holoviews.operation.datashader import datashade
from holoviews.plotting.plotly.dash import to_dash
from holoviews.selection import link_selections

from plotly import colors
from plotly.colors import sequential



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
    # Output("indicator-graph", "figure"),
    Output("map-graph", "figure"),
    Input("map-graph", "relayoutData"))
def update_plots(relayout_data):

    df = pd.read_csv('/Users/jamesswank/Desktop/TestingData_coordinates.csv')
    # print(df)

    trans = Transformer.from_crs(
        "epsg:4326",
        "+proj=utm +zone=13N +ellps=WGS84",
        always_xy=True,
    )
    

    x_3857,  y_3857 = trans.transform(df.geolongitude.values, df.geolatitude.values)
    df = df.assign(x_3857=x_3857, y_3857=y_3857)
    # print(df)

    coordinates_4326 = relayout_data and relayout_data.get("mapbox._derived", {}).get(
        "coordinates", None
    )


    

    data_3857 = [[df['y_3857'].min(), df['x_3857'].min()],
                [df['y_3857'].max(), df['x_3857'].max()]]

    data_4326 = utm.to_latlon(data_3857[0][1], data_3857[0][0], 13, 'N'), utm.to_latlon(data_3857[1][1], data_3857[1][0],13, 'N')

    # print(data_4326)

    data_center_3857 = [
            (data_3857[0][0] + data_3857[1][0]) / 2.0,
            (data_3857[0][1] + data_3857[1][1]) / 2.0,
    ]

    data_center_4326 = [utm.to_latlon(data_center_3857[1], data_center_3857[0], 13, 'N')]

    print(data_center_4326)
    position = {
            "zoom": 8,
            "pitch": 0,
            "bearing": 0,
            "center": {"lon": data_center_4326[0][1], "lat": data_center_4326[0][0]},
        }


    coordinates_3857 = data_3857
    coordinates_4326 = data_4326

   
    


    lat = []
    lon = []

    marker = {
            "color": "red",
            "size": 2,
            # "cmin": 0,
            # "cmax": 3
        }

    dataset = hv.Dataset(df)
    points = hv.Points(
    df, ["geolongitude", "geolatitude"]
    ).opts(color="crimson")
    tiles = hv.Tiles()
    overlay = tiles * datashade(points, cmap=sequential.Plasma)
    components = to_dash(app, [overlay], reset_button=True)
    layers = [components.children]
    
    

    map_graph = {
        "data": [
            {
                "type": "scattermapbox",
                "lat": lat,
                "lon": lon,
                # "customdata": customdata,
                # "marker": marker
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



    return map_graph


if __name__ == '__main__':
    app.run_server(port=8000,debug=True)