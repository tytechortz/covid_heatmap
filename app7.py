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

print(t_gdf['geometry'])
print(t_gdf.columns)

def get_figure():
    # Base choropleth layer --------------#
    fig = px.choropleth_mapbox(t_gdf, 
                                geojson=t_gdf.geometry, 
                                color="TOTALPOP",                               
                                locations=t_gdf.index, 
                                # featureidkey="properties.TRACTCE20",
                                opacity=0.5)

  

    #------------------------------------#
    fig.update_layout(mapbox_style="carto-positron", 
                      mapbox_zoom=10.4,
                      mapbox_center={"lat": 39.65, "lon": -104.8},
                      margin={"r":0,"t":0,"l":0,"b":0},
                      uirevision='constant')
    
    return fig


fig = get_figure()


app.layout = html.Div([    
    dcc.Graph(
        id='choropleth',
        figure=fig
    )
])







if __name__ == '__main__':
    app.run_server(port=8080,debug=True)