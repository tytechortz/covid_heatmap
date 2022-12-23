import plotly.express as px
import geopandas as gpd

import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State

import pandas as pd 

from datetime import date

from geopandas.tools import sjoin

# Colors
bgcolor = "#f3f3f1"  # mapbox light map land color

# Figure template
row_heights = [150, 500, 300]
template = {"layout": {"paper_bgcolor": bgcolor, "plot_bgcolor": bgcolor}}

# Build Dash layout
app = dash.Dash(__name__)

gdf = gpd.read_file('/Users/jamesswank/Python_projects/covid_heatmap/Census_Tracts_2020_SHAPE_WGS/Census_Tracts_2020_WGS.shp')
gdf = gdf.to_crs("epsg:4326")
gdf = gdf.set_geometry('geometry')




pop = pd.read_csv('/Users/jamesswank/Python_projects/covid_heatmap/Tract_Data_2020.csv')
pop['TRACTCE20'] = pop['TRACTCE20'].astype(str)
pop['TRACTCE20'] = pop['TRACTCE20'].str.zfill(6)
pop['TOTALPOP'] = pop['TOTALPOP'].astype(int)
pop['POPBIN'] = [1 if x<=3061 else 2 if 3061<x<=3817 else 3 if 3817<x<=5003 else 4 for x in pop['TOTALPOP']]
pop['COLOR'] = ['blue' if x==1 else 'green' if x==2 else 'orange' if x==3 else 'red' for x in pop['POPBIN']]
pop = pop.drop(['COUNTYFP20', 'GEOID20'], axis=1)

gdf['TRACTCE20'].astype(str)

t_gdf = gdf.merge(pop, on='TRACTCE20')
print(t_gdf.columns)

CT_lookup = pd.Series(t_gdf.geometry.values, index=t_gdf.index)

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

def get_highlights(selections, geojson=t_gdf, CT_lookup=CT_lookup):
    # geojson_highlights = dict()
    # print(selections)
    geojson_highlights = geojson.loc[selections]
    print(geojson_highlights)
    return geojson_highlights

# @app.callback(
#     Output('')
#     Input('tests', 'data'),

# )


def get_figure(selections, zoom, tests):

    # print(selections)

    tests = gpd.GeoDataFrame(tests, 
        geometry = gpd.points_from_xy(tests['geolongitude'], tests['geolatitude']))
    tests = tests.set_crs('epsg:4326')

    tIT = sjoin(tests, t_gdf, how='left')
    # print(tIT.columns)
    # print(t_gdf.columns)
    tITs = tIT.groupby('TRACTCE20').size().reset_index(name='count')
   
    tract_df = t_gdf.merge(tITs, on='TRACTCE20')
    tract_df['TperCap'] = tract_df['count'] / tract_df['TOTALPOP']
    # print(tract_df)
    
    # Base choropleth layer --------------#
    fig = px.choropleth_mapbox(tract_df, 
                                geojson=tract_df.geometry, 
                                color="TperCap",                               
                                locations=tract_df.index, 
                                # featureidkey="properties.TRACTCE20",
                                opacity=0.5)

  
    # Second layer - Highlights ----------#
    if len(selections) > 0:
        # highlights contain the geojson information for only 
        # the selected districts
        highlights = get_highlights(selections)
        print(highlights)
        fig.add_trace(
            px.choropleth_mapbox(t_gdf, geojson=highlights, 
                                 color="STATEFP20",
                                 locations=t_gdf.index, 
                                #  featureidkey="properties.TRACTCE20",                                 
                                 opacity=1).data[0]
        )
    #------------------------------------#
    fig.update_layout(mapbox_style="carto-positron", 
                      mapbox_zoom=zoom,
                      mapbox_center={"lat": 39.65, "lon": -104.8},
                      margin={"r":0,"t":0,"l":0,"b":0},
                      uirevision='constant')
    
    return fig

def get_histogram(selections, zoom, tests):

    
    
    print(tests)
    tests = gpd.GeoDataFrame(tests, 
        geometry = gpd.points_from_xy(tests['geolongitude'], tests['geolatitude']))
    tests = tests.set_crs('epsg:4326')
    tIT = sjoin(tests, t_gdf, how='left')
    # print(len(tIT))
    # print(tIT.columns)
    # print(t_gdf.columns)
    # tITs = tIT.groupby(['TRACTCE20', 'CollectionDate']).size().reset_index(name='count')
    # print(tITs.columns)
    # print(len(tITs))
    # tract_df = t_gdf.merge(tIT, on='TRACTCE20')
    # # tract_df['TperCap'] = tract_df['count'] / tract_df['TOTALPOP']
    # print(tract_df)
    if len(selections) == 0:

        fig = px.histogram(tIT, x='CollectionDate')
  
    # Second layer - Highlights ----------#
    else:
        df3 = tIT.loc[selections]
        print(df3)
        # highlights contain the geojson information for only 
        # the selected districts
        highlights = get_highlights(selections)
        print(highlights)
        tIT = tIT
        fig = px.histogram(tIT, x='CollectionDate')
      
    #------------------------------------#
    fig.update_layout(bargap=0.2)
    
    return fig




selections = set()
# print(selections)



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
            initial_visible_month=date(2022, 11, 14),
            end_date=date(2022, 11, 15)
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
                figure=blank_fig(row_heights[1]),
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
        # html.Div([
        #     html.H4([
        #         "Tests Selected Tracts",
        #         # html.Img(
        #         #     id="show-placeholder-modal",
        #         #     src="assets/question-circle-solid.svg",
        #         #     n_clicks=0,
        #         #     className="info-icon",
        #         # ),
        #     ]),
        # ],
        #     className="container_title",
        # ),
        dcc.Loading(
            dcc.Graph(
                id="test-graph",
                figure=blank_fig(row_heights[1]),
                config={"displayModeBar": False},
            ),
            className="svg-container",
            style={"height": 350},
        ),
    ],
        className="eight columns pretty_container",
        id="placeholder-div",
    ),
    # html.Div([
    #     html.Div([
    #         html.H4([
    #             "Placeholder",
    #             html.Img(
    #                 id="show-placeholder-modal-2",
    #                 src="assets/question-circle-solid.svg",
    #                 n_clicks=0,
    #                 className="info-icon",
    #             ),
    #         ]),
    #     ],
    #         className="container_title",
    #     ),
    #     dcc.Loading(
    #         dcc.Graph(
    #             id="placeholder-graph-2",
    #             figure=blank_fig(row_heights[0]),
    #             config={"displayModeBar": False},
    #         ),
    #         className="svg-container",
    #         style={"height": 150},
    #     ),
    # ],
    #     className="four columns pretty_container",
    #     id="placeholder-div-2",
    # ),
    
    dcc.Store(id='tests', storage_type='session'),
])

@app.callback(
    Output('tests', 'data'),
    Input('dates', 'start_date'),
    Input('dates', 'end_date'))
def get_tests(start_date, end_date):
    tests = pd.read_csv('/Users/jamesswank/Python_projects/covid_heatmap/TestingData_coordinates.csv')
    # print(start_date)
    tests['CollectionDate'] = pd.to_datetime(tests['CollectionDate'])
    tests = tests[(tests['CollectionDate'] >= start_date) & (tests['CollectionDate'] < end_date)]
    # print(tests)
    return tests.to_json(date_format='iso')


@app.callback(
    Output('ct', 'figure'),
    Output('test-graph', 'figure'),
    Input('ct', 'clickData'),
    Input('tests', 'data'),
    Input('zoom', 'value'))
def update_figure(clickData, tests, zoom):    
    tests = pd.read_json(tests)
  
    tests['CollectionDate'] = pd.to_datetime(tests['CollectionDate'])
    # tests = tests[(tests['CollectionDate'] >= start_date) & (tests['CollectionDate'] < end_date)]
    # print(tests)

    
    # print(clickData)
    if clickData is not None:            
        location = clickData['points'][0]['location']
        # print(location)
        if location not in selections:
            selections.add(location)
        else:
            selections.remove(location)
        
    return get_figure(selections, zoom, tests), get_histogram(selections, zoom, tests)


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

# @app.callback(
#     Output("test-graph", "figure"),
#     Input("tests", "data"))
# def update_indicator(tests, selections):
#     tests = pd.read_json(tests)
#     print(tests)
#     # total_tests = tests.shape[0]
    
#     fig = px.histogram(tests, x='CollectionDate')

#     fig.update_layout(bargap=0.2)



#     return fig




if __name__ == '__main__':
    app.run_server(port=8080,debug=True)