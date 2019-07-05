import pandas as pd
import numpy as np
import datetime as dt
from datetime import datetime
import seaborn as sns
import censusgeocode as cg
#=================================================================================================
# GET RAW DATA
def get_data(week_nums):
    url = "http://web.mta.info/developers/data/nyct/turnstile/turnstile_{}.txt"
    dfs = []
    for week_num in week_nums:
        file_url = url.format(week_num)
        dfs.append(pd.read_csv(file_url))
    return pd.concat(dfs)

week_nums = [190406, 190413, 190420, 190427, 190504, 190511, 190518
            , 180407, 180414, 180421, 180428, 180505, 180512, 180519
            , 170408, 170415, 170422, 170429, 170506, 170513, 170520
            , 160409, 160416, 160423, 160430, 160507, 160514, 160521]
turnstiles_df = get_data(week_nums)

working_directory = '.../MTA-Project/'

turnstiles_df.to_csv(working_directory+'turnstile_data_raw.csv')
#=================================================================================================
def map_day_of_week(value):
    if value == 0:
        return 'M'
    elif value == 1:
        return 'Tu'
    elif value == 2:
        return 'W'
    elif value == 3:
        return 'Th'
    elif value == 4:
        return 'F'
    elif value == 5:
        return 'Sa'
    elif value == 6:
        return 'Su'

# Read in raw data file
turnstiles_df = pd.read_csv(working_directory+'turnstile_data_raw.csv')

print(turnstiles_df.shape)
turnstiles_df.head()

turnstiles_df.columns = turnstiles_df.columns.str.strip().str.lower()
turnstiles_df.head()

turnstiles_df['date_time'] = turnstiles_df.date + ' ' + turnstiles_df.time
turnstiles_df['date_time'] = pd.to_datetime(turnstiles_df.date_time)
turnstiles_df['date'] = pd.to_datetime(turnstiles_df.date)

turnstiles_df.desc.value_counts()

turnstiles_reg = turnstiles_df[turnstiles_df.desc == 'REGULAR']

# write some time consuming data steps to csv
turnstiles_reg.to_csv(working_directory+'turnstile_data_reg_dt_format.csv', date_format= '%Y-%m-%d %H:%M:%S', index=False)
#=================================================================================================
# To read in csv and parse dates at same time, include argument parse_dates=[col]
turnstiles_reg = pd.read_csv(working_directory+'turnstile_data_reg_dt_format.csv', parse_dates=['date', 'date_time'])
turnstiles_reg.head(10)

turnstiles_reg = turnstiles_reg.sort_values(["c/a", "unit", "scp", "station", "date_time"], ascending=True)
turnstiles_reg['day_of_week'] = turnstiles_reg.date.dt.dayofweek.apply(map_day_of_week)
turnstiles_reg.head()

# sanity check
(turnstiles_reg
 .groupby(["c/a", "unit", "scp", "station", "date_time"])
 .entries.count()
 .reset_index()
 .sort_values("entries", ascending=False)).head(5)

 turnstiles_reg[["prev_date", "prev_entries", 'prev_exits']] = (turnstiles_reg
                                                        .groupby(["c/a", "unit", "scp", "station", 'date'])["date_time", "entries", 'exits']
                                                        .transform(lambda grp: grp.shift(1)))
 turnstiles_reg.head(20)

 turnstiles_reg.to_csv(working_directory+'turnstile_shifted_all_asc.csv', index=False)
#=================================================================================================
# Read in dataset with shifted entries and exits
turn_shifted = pd.read_csv(working_directory+'turnstile_shifted_all_asc.csv', parse_dates=['date', 'date_time'])
turn_shifted.head(10)
print(len(turn_shifted))

# remove null prev_entries/prev_exits because they will not give us a count for that timestamp
turn_shifted = turn_shifted[turn_shifted.prev_entries.notnull()]
print(len(turn_shifted))

def get_counts_per_timestamp(row, max_counter, col1, col2):
    counter = row[col1] - row[col2]
    if counter < 0:
        counter = -counter
    if counter > max_counter:
        return 0
    return counter

turn_shifted['entries_per_timestamp'] = turn_shifted.apply(get_counts_per_timestamp, \
                                max_counter=1000000, col1='entries', col2='prev_entries', axis=1)
turn_shifted['exits_per_timestamp'] = turn_shifted.apply(get_counts_per_timestamp, \
                                max_counter=1000000, col1='exits', col2='prev_exits', axis=1)

turn_shifted.head()

turn_shifted.describe()
# What is the deal with 0 entries and 0 exits? Counter resetting?

# Need decision: what to do with these cols?
print(len(turn_shifted[turn_shifted.entries == 0]))
print(len(turn_shifted[turn_shifted.exits == 0]))
# Number of records we'd have if we exclude times when entries and exits = 0
mask = ((turn_shifted.entries != 0) &
        (turn_shifted.exits != 0))
print(len(turn_shifted[mask]))

turn_shifted[turn_shifted.exits == 0].head(10)

turn_shifted.entries_per_timestamp.max()
turn_shifted.exits_per_timestamp.max()

turn_cleaned = turn_shifted.drop(columns=['prev_date', 'prev_entries', 'prev_exits'])
turn_cleaned.to_csv(working_directory+'turnstiles_cleaned.csv', index=False)
#=================================================================================================
turn_cleaned = pd.read_csv(working_directory+'turnstiles_cleaned.csv', parse_dates=['date', 'date_time'])

# Combine other useful datasets
lat_long = pd.read_csv(working_directory+'NYC_Transit_Subway_Entrance_And_Exit_Data.csv')
lat_long.columns = lat_long.columns.str.lower().str.strip()
lat_long = lat_long.rename(columns={'station name': 'station_name'
                                    , 'station latitude': 'station_latitude'
                                    , 'station longitude': 'station_longitude'})
lat_long.head(2)

lat_long.shape
lat_long = lat_long.iloc[:,:5]
lat_long.head(2)
lat_long.station_name.nunique()

lat_long = lat_long.sort_values(by='station_name')
lat_long = lat_long.drop_duplicates(subset='station_name', keep='first')
print(len(lat_long))
turn_cleaned.station.nunique()


census = pd.read_csv(working_directory+'censustract-medianhouseholdincome2018.csv')
census.columns = census.columns.str.lower().str.strip()
census = census.rename(columns={'census tract': 'census_tract'})
print(len(census))
census[census.census_tract==36061018900]

#=================================================================================================
# Get census tract ID for each station lat and long
census_dict = {}
for idx, row in lat_long.iterrows():
    census_info = cg.coordinates(y=row.station_latitude, x=row.station_longitude)
    tract = census_info['Census Tracts'][0]['GEOID']
    census_dict[tract] = [row.station_latitude, row.station_longitude]

census_coord = pd.DataFrame(census_dict).T
census_coord = census_coord.reset_index()
census_coord = census_coord.rename(columns={'index': 'census_tract'
                                            , 0: 'station_latitude'
                                            , 1: 'station_longitude'})
census_coord.shape
census_coord.to_csv(working_directory+'census_tract_lat_long.csv', index=False)
#=================================================================================================

census_coord['census_tract'] = census_coord.census_tract.astype(int)
census_coord.head()

census.head(2)
census = census.rename(columns={'2013-2017': 'med_income_2017'})
census = census[['census_tract', 'med_income_2017']]
census.head(2)

income_lat_long = pd.merge(census, census_coord, on='census_tract', how='inner')
income_lat_long.shape

income_lat_long = income_lat_long.drop(columns='census_tract')
income_lat_long.head(2)

income_stations = pd.merge(lat_long, income_lat_long, on=['station_latitude', 'station_longitude'], how='left')
income_stations.shape
income_stations.head()

income_stations = income_stations.drop(columns=['division', 'line'])
income_stations.to_csv(working_directory+'stations_with_coord_and_income.csv', index=False)
#=================================================================================================

income_stations.head(3)

income_stations['station'] = income_stations.station_name.str.strip().str.upper()
income_stations.head()
income_stations.station.unique()

#TODO need to work on this!
def add_th(s):
    if any(i in s for i in '0123456789'):
        # for char in s:

    # if i == '1':
    #     suffix = 'ST'
    # elif i == '2':
    #     suffix = 'ND'
    # elif i == '3':
    #     suffix = 'RD'
    # else:
    #     suffix = 'TH'

    return any(i in s for i in '0123456789')



turn_cleaned['station'] = turn_cleaned.station.str.strip()

turn_cleaned.station.unique()
