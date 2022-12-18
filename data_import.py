# import shapefile
from json import dumps
import pandas as pd
import json
from pandas import json_normalize
import geopandas as gpd

# df = gpd.read_file('/Users/jamesswank/Python_projects/covid_heatmap/Census_Tracts_2020_SHAPE_WGS/Census_Tracts_2020_WGS.shp')
# print(df)
# print(type(df))
# df = df.set_geometry('geometry')
# print(df.shape)

# pop = gpd.read_file('/Users/jamesswank/Python_projects/covid_heatmap/Tract_Data_2020.csv')
# pop['TRACTCE20'] = pop['TRACTCE20'].astype(str)
# pop['TRACTCE20'] = pop['TRACTCE20'].str.zfill(6)
# pop['TOTALPOP'] = pop['TOTALPOP'].astype(int)
# pop['POPBIN'] = [1 if x<=3061 else 2 if 3061<x<=3817 else 3 if 3817<x<=5003 else 4 for x in pop['TOTALPOP']]
# pop['COLOR'] = ['blue' if x==1 else 'green' if x==2 else 'orange' if x==3 else 'red' for x in pop['POPBIN']]

# print(pop)
# df_combo = pd.merge(pop, df, on='TRACTCE20', how='inner')
# print(type(df_combo))

gdf = gpd.read_file('/Users/jamesswank/Python_projects/covid_heatmap/Census_Tracts_2020_SHAPE_WGS/Census_Tracts_2020_WGS.shp')
gdf = gdf.to_crs("epsg:4326")
gdf = gdf.set_geometry('geometry')
# gdf['centroid'] = gdf['geometry'].representative_point()
print(gdf)
gdf.to_file("gdf.geojson", driver='GeoJSON')

# reader = shapefile.Reader('County_Boundary_SHAPE_WGS/County_Boundary_WGS.shp')
# fields = reader.fields[1:]
# field_names = [field[0] for field in fields]
# buffer = []
# for sr in reader.shapeRecords():
#     atr = dict(zip(field_names, sr.record))
#     geom = sr.shape.__geo_interface__
#     buffer.append(dict(type="Feature", \
#     geometry=geom, properties=atr)) 

#     # write the GeoJSON file

# geojson = open("county_outline.json", "w")
# geojson.write(dumps({"type": "FeatureCollection", "features": buffer}, indent=2) + "\n")
# geojson.close()

# pop_color_cats = []

# with open('pyshp-demo.json', 'r') as jsonFile:
#     for d in data:
#         d['COLOR'] = ''

# with open('pyshp-demo.json', 'w') as jsonFile:
#     json.dump()

# df_tract = pd.read_json('pyshp-demo.json')
# pop = pd.read_csv('/Users/jamesswank/Python_projects/covid_heatmap/Tract_Data_2020.csv')
# pop['TRACTCE20'] = pop['TRACTCE20'].astype(str)
# pop['TRACTCE20'] = pop['TRACTCE20'].str.zfill(6)
# print(pop)
# def get_json_data(file_name):
#     """
#     Read json data file and return list
#     """
#     with open(file_name) as f:
#         data = json.load(f)
    
#     return data

# file_path = '/Users/jamesswank/Python_projects/covid_heatmap/pyshp-demo.json'

# data = get_json_data(file_path) # Read json file and return list
# print(type(data))
# # print(data)
# tracts = pd.json_normalize(data['features'])
# # tracts = pd.DataFrame(data)
# # print(type(tracts))
# tracts.rename(columns={'properties.TRACTCE20': 'TRACTCE20'}, inplace=True)
# print(tracts)
# df_combo = pd.merge(pop, tracts, on='TRACTCE20', how='inner')

# df_combo['POPBIN'] = [1 if x<=3061 else 2 if 3061<x<=3817 else 3 if 3817<x<=5003 else 4 for x in df_combo['TOTALPOP']]
# df_combo['COLOR'] = ['blue' if x==1 else 'green' if x==2 else 'orange' if x==3 else 'red' for x in df_combo['POPBIN']]

# # df_combo.to_csv("combo.csv")
# # d = df_combo.to_dict(orient='records')
# df_combo.to_json('combo_json', orient='records')
# # j = json.dumps(d)

# with open('/Users/jamesswank/Python_projects/covid_heatmap/combo.json', 'w', encoding='utf-8') as f:
    # json.dump(j, f)
# pops = json.loads(combo_json)
# print(pops[0]['TOTALPOP'])






