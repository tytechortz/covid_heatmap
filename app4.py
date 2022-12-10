import json
import random
import pandas as pd
import geopandas as gpd
import plotly.graph_objects as go

geodf = gpd.read_file('Census_Tracts_2020_SHAPE_UTM/Census_Tracts_2020_UTM.shp')
print(geodf)