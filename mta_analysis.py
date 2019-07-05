import pandas as pd
import numpy as np
import datetime as dt
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns


working_directory = '.../MTA-Project/'


turn_cleaned = pd.read_csv(working_directory+'turnstiles_cleaned.csv', parse_dates=['date', 'date_time'])
turn_cleaned['station'] = turn_cleaned.station.str.strip()
turn_cleaned['year'] = turn_cleaned.date.dt.year
turn_cleaned['entries_and_exits_timestamp'] = turn_cleaned.entries_per_timestamp + turn_cleaned.exits_per_timestamp
turn_cleaned['day_of_week_num'] = turn_cleaned.date.dt.dayofweek
turn_cleaned.head()

# top stations with greatest ridership with
annual_entries = turn_cleaned.groupby(['station'])
pd.DataFrame(annual_entries.agg({'entries_per_timestamp': 'sum'})) \
        .sort_values('entries_per_timestamp', ascending=False).head()


groups = [2019, 2018, 2017, 2016]

# top stations per year with most entries and exits
for group in groups:
    yr = turn_cleaned.groupby(['year']).get_group(group)
    stations = yr.groupby('station').agg({'entries_and_exits_timestamp': 'sum'})
    stations = stations.sort_values(by='entries_and_exits_timestamp', ascending=False).head(10)
    print(group, stations)

top_5 = ['34 ST-PENN STA'
         , 'GRD CNTRL-42 ST'
         , '34 ST-HERALD SQ'
         , 'TIMES SQ-42 ST'
         , '14 ST-UNION SQ']

top_10 = ['34 ST-PENN STA'
         , 'GRD CNTRL-42 ST'
         , '34 ST-HERALD SQ'
         , 'TIMES SQ-42 ST'
         , '14 ST-UNION SQ'
         , '23 ST'
         , '86 ST'
         , 'FULTON ST'
         , '42 ST-PORT AUTH']

data_2019 = turn_cleaned[turn_cleaned.year==2019]
stations_top_5 = data_2019[data_2019.station.isin(top_5)]

weekly = stations_top_5.groupby('day_of_week')
weekly_sum = pd.DataFrame(weekly.agg({'entries_and_exits_timestamp':'sum'}))
weekly_sum

sns.lineplot(data=stations_top_5, hue='station', x='day_of_week_num', \
  y='entries_and_exits_timestamp');
