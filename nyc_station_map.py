import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import geopandas as gpd
import descartes
from shapely.geometry import Point, Polygon

working_directory = '.../MTA-Project/'

top_9_income_stations = pd.read_csv(working_directory+'top_9_stations_with_coord_and_income.csv')
top_9_income_stations
sns.distplot(top_9_income_stations[top_9_income_stations.med_income_2017.notnull()].med_income_2017);
top_9_income_stations.describe()

# GET A BASE MAP OF NYC WITH STREET LINES, FOCUS ON MANHATTAN
base_map = gpd.read_file(working_directory+'NYC Street Centerline (CSCL).geojson')

fig, ax = plt.subplots(figsize=(15,15))
plt.xlim(-74.05, -73.9)
plt.ylim(40.68, 40.82)
base_map.plot(ax=ax, alpha=0.4, color='grey');

new_station_list = ['PENN STATION'
                , '34TH ST-HERALD SQUARE'
                , 'PORT AUTHORITY BUS TERMINAL'
                ]
new_stations = top_9_income_stations[top_9_income_stations.station_name.isin(new_station_list)]
len(new_stations)
new_stations

#=================================================================================================
#=================================================================================================
#=================================================================================================
# ALL STATIONS WITH MEDIAN INCOME PLOTTED
all_stations_income = pd.read_csv(working_directory+'stations_with_coord_and_income.csv')\
all_stations_income['station_name'] = all_stations_income.station_name.str.strip().str.upper()
len(all_stations_income)
all_stations_income[all_stations_income.station_name.str.contains('TIMES')]

all_stations_income = all_stations_income.append(new_stations)
len(all_stations_income)

len(all_stations_income[all_stations_income.med_income_2017.isnull()])
54/356
sns.distplot(all_stations_income[all_stations_income.med_income_2017.notnull()].med_income_2017);

def get_med_income_bins(value):
    if value <= 50000:
        return '<= 50K'
    elif value <= 100000:
        return '50K <= 100K'
    elif value <= 150000:
        return '100K <= 150K'
    elif value > 150000:
        return '> 150K'
    else:
        return 'No data'

all_stations_income['med_income_bins'] = all_stations_income.med_income_2017.apply(get_med_income_bins)
all_stations_income.med_income_bins.value_counts()

def label_top_5_stations(row):
    if row.station_name in ['PENN STATION'
                      , '34TH ST-HERALD SQUARE'
                      , 'PORT AUTHORITY BUS TERMINAL'
                      , 'TIMES SQUARE-42ND ST'
                      , '86TH ST']:
        return 'Top 5'
    else:
        return 'Not Top'

all_stations_income['top_5_label'] = all_stations_income.apply(label_top_5_stations, axis=1)
all_stations_income.top_5_label.value_counts()

all_stations_income.info()


all_stations_income.head()
# Plot income bins on the base map
points = [Point(xy) for xy in zip(all_stations_income.station_longitude, all_stations_income.station_latitude)]
crs = {'init': 'epsg:4326'}
geo_df = gpd.GeoDataFrame(all_stations_income, crs=crs, geometry=points)
geo_df.columns

fig, ax = plt.subplots(figsize=(15,15))
plt.xlim(-74.03, -73.92)
plt.ylim(40.70, 40.82)
base_map.plot(ax=ax, alpha=0.4, color='grey');
geo_df[geo_df.med_income_bins=='<= 50K'].plot(ax=ax, markersize=20, color='black', marker='^', label='50K or less')
geo_df[geo_df.med_income_bins=='50K <= 100K'].plot(ax=ax, markersize=25, color='green', marker='o', label='between 50K and 100K')
geo_df[geo_df.med_income_bins=='100K <= 150K'].plot(ax=ax, markersize=40, color='red', marker='o', label='between 100K and 150K')
geo_df[geo_df.med_income_bins=='> 150K'].plot(ax=ax, markersize=50, color='blue', marker='o', label='over 150K')
plt.legend(prop={'size':15}, title='Median Income', title_fontsize='20')
plt.savefig(working_directory+'top_5_map_zoomed_all_sta.png', bbox_inches='tight')
#=================================================================================================
#=================================================================================================
#=================================================================================================
# NEW MAP JUST WITH SUBWAY STATIONS

fig, ax = plt.subplots(figsize=(15,15))
plt.xlim(-74.03, -73.92)
plt.ylim(40.70, 40.82)
base_map.plot(ax=ax, alpha=0.4, color='grey');
geo_df[geo_df.top_5_label=='Top 5'].plot(ax=ax, markersize=100, color='blue', marker='o', label='Top 5 Stations')
plt.legend(prop={'size':20}, loc='upper left')
plt.savefig(working_directory+'top_5_only_map.png', bbox_inches='tight')
