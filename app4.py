import json
import random
import pandas as pd
import geopandas as gpd
import plotly.graph_objects as go
import plotly.express as px
import json
import numpy as np
import dash
from dash import dcc, html
# import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.express as px
from json import dumps
from geopandas.tools import sjoin
from shapely.geometry import Point



# Load mapbox token
mapbox_access_token = open(".mapbox_token").read()

# Build Dash layout
app = dash.Dash(__name__)


gdf = gpd.read_file('/Users/jamesswank/Python_projects/covid_heatmap/Census_Tracts_2020_SHAPE_WGS/Census_Tracts_2020_WGS.shp')
# print(df)
# print(gdf.crs)
gdf = gdf.to_crs("epsg:4326")
# print(gdf.crs)
# print(type(gdf))

gdf = gdf.set_geometry('geometry')
gdf['centroid'] = gdf['geometry'].centroid
# gdf['id'] = range(1, len(gdf) + 1)
# gdf = gdf.reset_index()
print(gdf)

pop = pd.read_csv('/Users/jamesswank/Python_projects/covid_heatmap/Tract_Data_2020.csv')
pop['TRACTCE20'] = pop['TRACTCE20'].astype(str)
pop['TRACTCE20'] = pop['TRACTCE20'].str.zfill(6)
pop['TOTALPOP'] = pop['TOTALPOP'].astype(int)
pop['POPBIN'] = [1 if x<=3061 else 2 if 3061<x<=3817 else 3 if 3817<x<=5003 else 4 for x in pop['TOTALPOP']]
pop['COLOR'] = ['blue' if x==1 else 'green' if x==2 else 'orange' if x==3 else 'red' for x in pop['POPBIN']]

print(pop)
df_combo = pd.merge(pop, gdf, on='TRACTCE20', how='outer')
print(df_combo.columns)
df_combo.set_geometry('geometry')

print(df_combo.geometry.head)



# df_combo = df_combo.rename(columns={"geometry_y":"geometry"})
# print(df_combo)
df_tests = pd.read_csv('/Users/jamesswank/Python_projects/covid_heatmap/TestingData_coordinates.csv')
df_tests = gpd.GeoDataFrame(df_tests,
    geometry = gpd.points_from_xy(df_tests['geolongitude'], df_tests['geolatitude']))

df_tests.crs = "EPSG:4326"


# print(tests_gdf)
# print(df_combo)
# dfsjoin = gpd.sjoin(df_tests, gdf, how='left')
# tips = dfsjoin.groupby(['id']).size()
# print(tips)
# print(type(tips))
# dfsjoin['tests'] = dfsjoin.groupby(['id']).size()
# dfsjoin['tests'] = dfsjoin['tests'].fillna(0)
# print(dfsjoin.columns)
# print(dfsjoin['geometry'])




# with open('combo.json') as json_file:
#     jdata = json_file.read()
#     topoJSON = json.loads(jdata)

# sources=[]
# for feat in dfsjoin['geometry']: 
#         sources.append({"type": "FeatureCollection", 'features': [feat]})

# print(sources)
# Get centroids 
points = df_combo.centroid
# Define new columns 
pop['lat'] = points.apply(lambda x : x.y if x else np.nan)
pop['lon'] = points.apply(lambda x : x.x if x else np.nan)


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

    fig = px.scatter_mapbox(pop,
                        lat="lat",
                        lon="lon",
                        # hover_name='Geography',
                        # color='graph_housing_str',
                        # title="Census - graph_housing - 2011",
                        # color_discrete_map=color_map,
                        # category_orders={'graph_housing_str':('1','2','3','4')},
                        size='COUNTYFP20', color='COLOR', opacity=.5,zoom=9,
                        center=dict(
                                    lat=39.6,
                                    lon=-104.8
                                )
                       )
#   setting style for plot
    fig.update_layout(mapbox_style="carto-positron")
    return fig

    # fig = px.choropleth_mapbox(gdf, 
    #                         geojson=gdf.__geo_interface__, 
    #                         # locations= gdf.TRACTCE20,
    #                         color_continuous_scale="Viridis",
    #                         # range_color=(0, 200),
    #                         mapbox_style="carto-positron",
    #                         color = 'Shape_Area',
    #                         center = {'lat': 39.5, 'lon': -104.6},
    #                         zoom = 8,
    #                         opacity = 0.5,

    #                     #    scope="usa",
    #                     #    labels={'unemp':'unemployment rate'}
    #                         )
    # fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    # return fig

    # def fill_color():
    #     for k in range(len(sources)):
    #         sources[k]['features'][0]['properties']['COLOR'] = 'lightgreen'
                           
    # fill_color()

    # layers=[dict(sourcetype = 'json',
    #     source =sources[k],
    #     # below="water", 
    #     type = 'fill',
    #     color = sources[k]['features'][0]['properties']['COLOR'],
    #     opacity = 0.1,
    #     width = 10,
    #     ) for k in range(len(sources))] 
    # # print(layers[0])

    # data = [dict(
    #     lat = 39.5,
    #     lon = -104.5,
    #     # text = df_smr['name'],
    #     # hoverinfo = 'text',
    #     type = 'scattermapbox',
    #     # customdata = df['uid'],
    #     mode = 'markers',
    #     marker = dict(size=10, color='red')
    #     # marker = dict(size=df_smr['marker_size'],color='forestgreen',opacity=.5),
    #     )]

    # layout = {
    #     "autosize": True,
    #     "datarevision": 0,
    #     "hovermode": "closest",
    #     "mapbox": {
    #         "accesstoken": mapbox_access_token,
    #         "bearing": 0,
    #         "center": {"lat": 39.65, "lon": -104.8},
    #         "pitch": 0,
    #         # "opacity": 0.2,
    #         "zoom": 10,
    #         "style": "light",
    #         "layers": layers
    #     },
    #     "margin": {"r": 0, "t": 0, "l": 0, "b": 0, "pad": 0},
    # }

    # fig = dict(data=data, layout=layout)
    # return fig






if __name__ == '__main__':
    app.run_server(port=8080,debug=True)