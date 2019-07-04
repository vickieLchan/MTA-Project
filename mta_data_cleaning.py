import pandas as pd
import datetime as dt
from datetime import datetime

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

 turnstiles_reg.to_csv(working_directory+'turnstile_shifted_all_desc.csv', index=False)
