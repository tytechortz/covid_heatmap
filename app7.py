import plotly.express as px
import geopandas as gpd

import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State

import pandas as pd 

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

t_gdf = gdf.merge(pop, on='TRACTCE20').set_index('TRACTCE20')


CT_lookup = pd.Series(t_gdf.geometry.values, index=t_gdf.index)

#

def get_highlights(selections, geojson=t_gdf, CT_lookup=CT_lookup):
    # geojson_highlights = dict()
    print(selections)
    geojson_highlights = geojson.loc[selections]
    print(geojson_highlights)
    return geojson_highlights

def get_figure(selections):
    print(selections)
    # Base choropleth layer --------------#
    fig = px.choropleth_mapbox(t_gdf, 
                                geojson=t_gdf.geometry, 
                                color="TOTALPOP",                               
                                locations=t_gdf.index, 
                                # featureidkey="properties.TRACTCE20",
                                opacity=0.5)

  
    # Second layer - Highlights ----------#
    if len(selections) > 0:
        # highlights contain the geojson information for only 
        # the selected districts
        highlights = get_highlights(selections)

        fig.add_trace(
            px.choropleth_mapbox(t_gdf, geojson=highlights, 
                                 color="STATEFP20",
                                 locations=t_gdf.index, 
                                #  featureidkey="properties.TRACTCE20",                                 
                                 opacity=1).data[0]
        )
    #------------------------------------#
    fig.update_layout(mapbox_style="carto-positron", 
                      mapbox_zoom=10.4,
                      mapbox_center={"lat": 39.65, "lon": -104.8},
                      margin={"r":0,"t":0,"l":0,"b":0},
                      uirevision='constant')
    
    return fig




selections = set()
# print(selections)

app.layout = html.Div([    
    dcc.Graph(
        id='choropleth',
    )
])


@app.callback(
    Output('choropleth', 'figure'),
    [Input('choropleth', 'clickData')])
def update_figure(clickData):    
    # print(clickData)
    if clickData is not None:            
        location = clickData['points'][0]['location']
        print(location)
        if location not in selections:
            selections.add(location)
        else:
            selections.remove(location)
        
    return get_figure(selections)




if __name__ == '__main__':
    app.run_server(port=8080,debug=True)