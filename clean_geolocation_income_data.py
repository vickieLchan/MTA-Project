import pandas as pd
import numpy as np
import datetime as dt
from datetime import datetime
import seaborn as sns
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import censusgeocode as cg

working_directory = '.../MTA-Project/'

# Read in lat long dataset for stations
lat_long = pd.read_csv(working_directory+'NYC_Transit_Subway_Entrance_And_Exit_Data.csv')
lat_long.columns = lat_long.columns.str.lower().str.strip()
lat_long = lat_long.rename(columns={'station name': 'station_name'
                                    , 'station latitude': 'station_latitude'
                                    , 'station longitude': 'station_longitude'})
lat_long['station_name'] = lat_long.station_name.str.upper()
lat_long.head(2)

lat_long.shape
# GRAB ONLY THE RELEVANT DATA COLUMNS
lat_long = lat_long.iloc[:,2:5]
lat_long.head(2)

# FIND UNIQUE STATION NAMES IN THE DATASET
lat_long.station_name.nunique()
lat_long = lat_long.sort_values(by='station_name')
lat_long = lat_long.drop_duplicates(subset='station_name', keep='first')
print(len(lat_long))

# TOP 9 STATIONS BY RIDERSHIP
top_9 = ['34TH ST-PENN STA'  # Look up lat and long
         , 'GRAND CENTRAL-42ND ST' # Y
         , '34TH ST-HERALD SQ' # Look up lat and long
         , 'TIMES SQUARE-42ND ST' #Y
         , '14TH ST-UNION SQUARE' #Y
         , '23RD ST' #Y
         , '86TH ST' #Y
         , 'FULTON ST' #Y
         , '42ND ST-PORT AUTH'] # Look up lat and long

# CHECK TO SEE HOW MANY OF THESE TOP STATIONS ARE ALREADY IN THE DATASET
top_9_lat_long = lat_long[lat_long.station_name.isin(top_9)].reset_index(drop=True)
top_9_lat_long
# ONLY SIX OF THE 9 TOP STATIONS ARE IN THE LAT AND LONG dataset
# WE NEED TO FIND THE LAT AND LONG INFORMATION FOR THE LAST 3 STATIONS

#=================================================================================================
# GET LAT AND LONG DATA FOR REMAINING 3 STATIONS
station_list = ['PENN STATION'
                , '34TH ST-HERALD SQUARE'
                , 'PORT AUTHORITY BUS TERMINAL']

def get_geolocation_from_address(address_list
                                 , city_state
                                 , api
                                 , address_col_name
                                 , latitude_col_name
                                 , longitude_col_name):

    loc_dict = {}
    geolocator = Nominatim(user_agent = api, format_string= city_state)

    for addy in address_list:
        location = geolocator.geocode(addy, timeout=6)
        loc_dict[addy] = [location.latitude, location.longitude]

    loc_df = pd.DataFrame(loc_dict).T
    loc_df = loc_df.reset_index()
    loc_df = loc_df.rename(columns = {'index': address_col_name
                   , 0: latitude_col_name
                   , 1: longitude_col_name})

    return loc_df

new_station_lat_long = get_geolocation_from_address(address_list=station_list
                                                    , city_state='%s New York, NY'
                                                    , api='https://www.w3.org/TR/geolocation-API/'
                                                    , address_col_name='station_name'
                                                    , latitude_col_name='station_latitude'
                                                    , longitude_col_name='station_longitude'
                                                    )
new_station_lat_long

# APPEND NEW STATIONS TO TOP 9 STATION DF
top_9_lat_long = top_9_lat_long.append(new_station_lat_long).reset_index(drop=True)
top_9_lat_long
# SAVE TOP 9 STATION LIST AS A CSV file
top_9_lat_long.to_csv(working_directory+'top_9_stations_lat_long.csv', index=False)
#=================================================================================================
#=================================================================================================
#=================================================================================================
#=================================================================================================

# READ IN CENSUS DATA
census = pd.read_csv(working_directory+'censustract-medianhouseholdincome2018.csv')
census.columns = census.columns.str.lower().str.strip()
census = census.rename(columns={'census tract': 'census_tract'})
print(len(census))
census.head()

census = census.rename(columns={'2013-2017': 'med_income_2017'})
census = census[['census_tract', 'med_income_2017']]
len(census)
census.head(2)
# INCOME DATA IS NOW IN THE FORMAT THAT WE WANT
census_no_nulls = census[census.med_income_2017.notnull()]
len(census_no_nulls)

# Check distribution of income data
sns.distplot(census_no_nulls.med_income_2017);

# There are no null values or ridiculous values for income data
#=================================================================================================
# Get census tract ID for each station lat and long
top_9_lat_long

def get_census_tract_from_geolocation(df
                                      , latitude_col_name
                                      , longitude_col_name
                                      , tract_col_name):
    census_dict = {}
    for idx, row in df.iterrows():
        census_info = cg.coordinates(y=row[latitude_col_name], x=row[longitude_col_name])
        tract = census_info['Census Tracts'][0]['GEOID']
        census_dict[tract] = [row[latitude_col_name], row[longitude_col_name]]

    census_coord = pd.DataFrame(census_dict).T
    census_coord = census_coord.reset_index()
    census_coord = census_coord.rename(columns={'index': tract_col_name
                                                , 0: latitude_col_name
                                                , 1: longitude_col_name})
    return census_coord

census_tract_lat_long = get_census_tract_from_geolocation(top_9_lat_long
                                                          , latitude_col_name='station_latitude'
                                                          , longitude_col_name='station_longitude'
                                                          , tract_col_name='census_tract')

census_tract_lat_long.shape
census_tract_lat_long

census_tract_lat_long.to_csv(working_directory+'top_9_station_census_tract_lat_long.csv', index=False)
#=================================================================================================
#=================================================================================================
#=================================================================================================
#=================================================================================================

census_tract_lat_long['census_tract'] = census_tract_lat_long.census_tract.astype(int)
census_tract_lat_long.head()

# MERGE CENSUS TRACT INCOME INFO WITH LAT AND LONG
len(census)
len(census_tract_lat_long)
income_lat_long = pd.merge(census, census_tract_lat_long, on='census_tract', how='inner')
len(income_lat_long)

income_lat_long
# Drop census_tract column because it's no longer needed
income_lat_long = income_lat_long.drop(columns='census_tract')
income_lat_long.head(2)

# MERGE INCOME DATA WITH STATION NAMES
income_stations = pd.merge(top_9_lat_long, income_lat_long, on=['station_latitude', 'station_longitude'], how='inner')
income_stations.shape
income_stations

income_stations.to_csv(working_directory+'top_9_stations_with_coord_and_income.csv', index=False)

# Check income distribution around top 9 stations
sns.distplot(income_stations[income_stations.med_income_2017.notnull()].med_income_2017);
#=================================================================================================
#=================================================================================================
#=================================================================================================
#=================================================================================================
