import dash
from dash import dcc, html
from datetime import date

import numpy as np
import pandas as pd 
import geopandas as gpd
from geopandas import GeoDataFrame
import plotly.express as px
from dash.dependencies import Input, Output, State

from geopandas.tools import sjoin
import json

from textwrap import dedent

# Load mapbox token
mapbox_access_token = open(".mapbox_token").read()

# Build Dash layout
app = dash.Dash(__name__)


gdf = gpd.read_file('/Users/jamesswank/Python_projects/covid_heatmap/Census_Tracts_2020_SHAPE_WGS/Census_Tracts_2020_WGS.shp')
# gdf = gdf.to_crs("epsg:4326")
# gdf = gdf.set_geometry('geometry')
# gdf['centroid'] = gdf['geometry'].centroid
# gdf = gpd.read_file('gdf.geojson')
gdf = gdf.to_crs("epsg:4326")
gdf = gdf.set_geometry('geometry')
# gdf['centroid'] = gdf['geometry'].representative_point()


# print(gdf.columns)

pop = pd.read_csv('/Users/jamesswank/Python_projects/covid_heatmap/Tract_Data_2020.csv')
pop['TRACTCE20'] = pop['TRACTCE20'].astype(str)
pop['TRACTCE20'] = pop['TRACTCE20'].str.zfill(6)
pop['TOTALPOP'] = pop['TOTALPOP'].astype(int)
pop['POPBIN'] = [1 if x<=3061 else 2 if 3061<x<=3817 else 3 if 3817<x<=5003 else 4 for x in pop['TOTALPOP']]
pop['COLOR'] = ['blue' if x==1 else 'green' if x==2 else 'orange' if x==3 else 'red' for x in pop['POPBIN']]
pop = pop.drop(['COUNTYFP20', 'GEOID20'], axis=1)

gdf['TRACTCE20'].astype(str)

tract_gdf = gdf.merge(pop, on='TRACTCE20')


factor = 0.9
# Colors
bgcolor = "#f3f3f1"  # mapbox light map land color

# Figure template
row_heights = [150, 500, 300]
template = {"layout": {"paper_bgcolor": bgcolor, "plot_bgcolor": bgcolor}}


f = open('/Users/jamesswank/Python_projects/covid_heatmap/tracts.geojson')
geojson=json.load(f)

# print(geojson)



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
    fig = px.choropleth_mapbox(tract_gdf, geojson=geojson, 
                               color="TOTALPOP",                               
                               locations="TRACTCE20", 
                               featureidkey="properties.district",
                               opacity=0.5)

    # Second layer - Highlights ----------#
    if len(selections) > 0:
        # highlights contain the geojson information for only 
        # the selected districts
        highlights = get_highlights(selections)

        fig.add_trace(
            px.choropleth_mapbox(tract_gdf, geojson=highlights, 
                                 color="TOTALPOP",
                                 locations="district", 
                                 featureidkey="properties.district",                                 
                                 opacity=1).data[0]
        )

    #------------------------------------#
    fig.update_layout(mapbox_style="carto-positron", 
                      mapbox_zoom=9,
                      mapbox_center={"lat": 45.5517, "lon": -73.7073},
                      margin={"r":0,"t":0,"l":0,"b":0},
                      uirevision='constant')
    
    return fig


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

app.layout = html.Div([
    html.Div([
        html.H4([
            "Arapahoe County Testing",
            html.Img(
                id="show-title-modal",
                src="assets/question-circle-solid.svg",
                n_clicks=0,
                className="info-icon",
            ),
        ]),
    ],
        className="container_title",
    ),
    html.Div([
        html.Div([
            dcc.Slider(
            id = 'opacity',
            min = 0,
            max = 1,
            value = 1,
            # marks = {i for i in range(2020,2022)}
            ),
        ],
            className = 'three columns'
        ),
        html.Div([
            dcc.DatePickerRange(
            id = 'dates',
            min_date_allowed=date(1995, 8, 5),
            max_date_allowed=date(2023, 1, 1),
            start_date=date(2022, 10, 25),
            initial_visible_month=date(2022, 10, 1),
            end_date=date(2022, 12, 20)
            ),
        ],
            className = 'five columns'
        ),
        html.Div([
            dcc.Slider(
            id = 'zoom',
            min = 8,
            max = 11,
            value = 10.4,
            # marks = {i for i in range(2020,2022)}
            ),
        ],
            className = 'three columns'
        ),
    ],
        className = 'row'
    ),
    # dcc.Graph(id = 'ct'),
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
            id="ct",
            figure=blank_fig(row_heights[1]),
            config={"displayModeBar": False},
        ),
    ],
        className="twelve columns pretty_container",
        style={
            "width": "98%",
            "margin-right": "0",
        },
        id="map-div",
    ),
    html.Div([
        html.Div([
            html.H6([
                "Test Count Selected Date Range",
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
    ],
        className="four columns pretty_container",
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
    ],
        className="four columns pretty_container",
        id="placeholder-div",
    ),
    html.Div([
        html.Div([
            html.H4([
                "Placeholder",
                html.Img(
                    id="show-placeholder-modal-2",
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
                id="placeholder-graph-2",
                figure=blank_fig(row_heights[0]),
                config={"displayModeBar": False},
            ),
            className="svg-container",
            style={"height": 150},
        ),
    ],
        className="four columns pretty_container",
        id="placeholder-div-2",
    ),
    html.Div([
        html.H4([
            "Census Tracts",
            html.Img(
                id="show-map-modal-2",
                src="assets/question-circle-solid.svg",
                className="info-icon",
            ),
        ],
            className="container_title",
        ),
        dcc.Graph(
            id="bubble-graph",
            figure=blank_fig(row_heights[1]),
            config={"displayModeBar": False},
        ),
    ],
        className="twelve columns pretty_container",
        style={
            "width": "98%",
            "margin-right": "0",
        },
        id="bubble-div",
    ),
    dcc.Store(id='tests', storage_type='session'),

])


@app.callback(
    Output('tests', 'data'),
    Input('dates', 'start_date'),
    Input('dates', 'end_date'))
def get_tests(start_date, end_date):
    tests = pd.read_csv('/Users/jamesswank/Python_projects/covid_heatmap/TestingData_coordinates.csv')

    tests['CollectionDate'] = pd.to_datetime(tests['CollectionDate'])
    tests = tests[(tests['CollectionDate'] >= start_date) & (tests['CollectionDate'] < end_date)]
    
    return tests.to_json(date_format='iso')


@app.callback(
    # Output("indicator-graph", "figure"),
    Output("ct", "figure"),
    Input("opacity", "value"),
    Input("zoom", "value"),
    Input("ct", "clickData"),
    Input("tests", "data"))
def update_map(opacity, zoom, clickData, tests):
    print(clickData)

    





    # pop = pd.read_json(pop)
    tests = pd.read_json(tests)
    zoom = zoom

    selections = set()

    if clickData is not None:            
        location = clickData['points'][0]['TRACTCE20']

        if location not in selections:
            selections.add(location)
        else:
            selections.remove(location)
        
    return get_figure(selections)


    # gdf['TRACTCE20'].astype(str)
    # gdf['geometry'] = gdf['geometry'].to_crs('epsg:4326')

   
    # tract_gdf = gdf.merge(pop, on='TRACTCE20')
    # print(tract_gdf.columns)
    
    tests = gpd.GeoDataFrame(tests, 
        geometry = gpd.points_from_xy(tests['geolongitude'], tests['geolatitude']))
    tests = tests.set_crs('epsg:4326')

    tIT = sjoin(tests, tract_gdf, how='left')
    tITs = tIT.groupby('TRACTCE20').size().reset_index(name='count')
    # print(tIT.columns)
    tract_df = tract_gdf.merge(tITs, on='TRACTCE20')
    tract_df['TperCap'] = tract_df['count'] / tract_df['TOTALPOP']
    # print(tract_df)





    fig = px.choropleth_mapbox(tract_df, 
                            geojson=tract_df.__geo_interface__,
                            featureidkey='properties.TRACTCE20',
                            # hover_name='Geography',
                            locations= 'TRACTCE20',
                            color='TperCap',
                            color_continuous_scale = 
                                [[0, 'rgb(166,206,227, 0.5)'],
                                [0.05, 'rgb(31,120,180,0.5)'],
                                [0.2, 'rgb(178,223,138,0.5)'],
                                [0.5, 'rgb(51,160,44,0.5)'],
                                [factor, 'rgb(251,154,153,0.5)'],
                                [factor, 'rgb(227,26,28,0.5)'],
                                [1, 'rgb(227,26,28,0.5)']
                            ],
                            labels = {'TpCap': 'Tests Per Capita'},
                            # color_continuous_scale="Viridis",
                            # title="Census - " + topic,
                            # category_orders={'TOTALPOP':('1','2','3','4')},
                            # color_discrete_map=color_map,
                            opacity=opacity,
                            zoom=zoom,   
                            center=dict(
                                lat=39.65,
                                lon=-104.8
                            ))

    fig.update_layout(mapbox_style="carto-positron",margin={"r":0,"t":0,"l":0,"b":0})

    fig.update_layout(
        mapbox={'layers': [{
            'source': gdf.__geo_interface__,
            'type': "fill", 'below': "traces", 'color': "#dedede",
            'opacity': 0.3
        }]}
    )

   


    return fig

@app.callback(
    Output("indicator-graph", "figure"),
    Input("tests", "data"))
def update_indicator(tests):
    tests = pd.read_json(tests)

    total_tests = tests.shape[0]
    # Build indicator figure
    n_selected_indicator = {
        "data": [
            {
                "type": "indicator",
                "value": total_tests,
                "number": {"valueformat":",d", "font": {"color": "#263238"}},
            }
        ],
        "layout": {
            "template": template,
            "height": 150,
            "margin": {"l": 10, "r": 10, "t": 10, "b": 10},
        },
    }

    return n_selected_indicator

@app.callback(
    Output("bubble-graph", "figure"),
    Input("tests", "data"))
def display_bubble_graph(tests):
    tests = pd.read_json(tests)
    
    gdf['TRACTCE20'].astype(str)
    # print(gdf.columns)
    tract_gdf = gdf.merge(pop, on='TRACTCE20')

    tests = gpd.GeoDataFrame(tests, 
        geometry = gpd.points_from_xy(tests['geolongitude'], tests['geolatitude']))
    tests = tests.set_crs('epsg:4326')
    # print(type(gdf))
    tIT = sjoin(tract_gdf, tests, how='left')

    tIT['test'] = 1
    
    tIT['CollectionDate'] = pd.to_datetime(tIT['CollectionDate'])
    tIT['CollectionDate'] = tIT['CollectionDate'].dt.strftime('%Y-%m-%d')
    # print(tIT.columns)
    tIT = tIT.drop(tIT.columns[[0,1,3,4,5,6,7,8,9,10,11,12,13,14,15,17,18,19,21,22,23,25,26,27,28]], axis=1)

    tIT =tIT.sort_values(['CollectionDate', 'TRACTCE20'])
    tIT['cumsum'] = tIT.groupby('TRACTCE20')['test'].cumsum()
   
    tIT = tIT.sort_values('CollectionDate')
 
    tIT['TperCap'] = tIT['cumsum'] / tIT['TOTALPOP']
   
    animations = {
        'GDP - Scatter': px.scatter(
            tIT, x="cumsum", y="TperCap", animation_frame="CollectionDate", 
            animation_group="TRACTCE20", size="TOTALPOP", color="TRACTCE20", 
            hover_name="TRACTCE20", log_x=True, log_y=True, size_max=55, 
            range_x=[1,8000], range_y=[.005, 1]),
      
    }
   
    return animations['GDP - Scatter']

if __name__ == '__main__':
    app.run_server(port=8080,debug=True)