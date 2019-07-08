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
         , '14 ST-UNION SQ'
         # , '23 ST'
         ]

top_9 = ['34 ST-PENN STA'
         , 'GRD CNTRL-42 ST'
         , '34 ST-HERALD SQ'
         , 'TIMES SQ-42 ST'
         , '14 ST-UNION SQ'
         , '23 ST'
         , '86 ST'
         , 'FULTON ST'
         , '42 ST-PORT AUTH']

mask = ((turn_cleaned.entries != 0) &
        (turn_cleaned.exits != 0))
turn_cleaned = turn_cleaned[mask]
print(len(turn_cleaned))

data_2019 = turn_cleaned[(turn_cleaned.year==2019) & (turn_cleaned.time=='16:00:00')]
stations_top_5 = data_2019[data_2019.station.isin(top_5)]
stations_top_5.head()

weekly = stations_top_5.groupby(['station', 'day_of_week_num'])
weekly_sum = pd.DataFrame(weekly.agg({'entries_per_timestamp':'median'}))
weekly_sum = weekly_sum.reset_index()
weekly_sum.groupby('day_of_week_num').agg({'entries_per_timestamp': 'median'})

sns.lineplot(data=weekly_sum, hue='station', x='day_of_week_num', y='entries_per_timestamp');

#====================================================================================
# CHALLEGE 4
# Daily time series for a turnstile
# groupby turnstile and time. Get 1 group
turnstiles_daily = turn_cleaned.groupby(["c/a", "unit", "scp","station", "date"])

one_day = ("A002", "R051", "02-00-00", "59 ST", datetime(2016,4,2,0,0,0))

turnstiles_daily_1d = turnstiles_daily.get_group(one_day)

sns.lineplot(data=turnstiles_daily_1d, x='time', \
  y='entries_and_exits_timestamp');

# aggregated turnstile data
# daily_entries_exits = pd.DataFrame(turnstiles_daily.agg({'entries_and_exits_timestamp': 'median'})).reset_index()

top_5 = ['34 ST-PENN STA', 'TIMES SQ-42 ST', '42 ST-PORT AUTH', '86 ST', '34 ST-HERALD SQ']
top_5_sta_only = turn_cleaned[(turn_cleaned.station.isin(top_5)) & (turn_cleaned.date>datetime(2019,1,1,0,0,0))]
len(top_5_sta_only)

t5_one_day = ("A021", "R032", "01-00-00", "TIMES SQ-42 ST", datetime(2019,5,7,0,0,0)) # 5/3, 5/6

t5_turn_daily = top_5_sta_only.groupby(["c/a", "unit", "scp","station", "date"])
t5_turnstiles_daily_1d = turnstiles_daily.get_group(t5_one_day)

sns.lineplot(data=t5_turnstiles_daily_1d, x='time', \
  y='entries_per_timestamp');

top_5_sta_only.head()
#====================================================================================
# CHALLEGE 8
turn_cleaned['week'] = turn_cleaned.date.dt.to_period("W").astype(str)
turn_cleaned.head(20)
one_turnstile = ["c/a", "unit", "scp", "station", 'week']


one_turnstile_example = ["A002", "R051", "02-00-00", "59 ST"]
one_turnstile_example.append('2016-04-04/2016-04-10')
one_turnstile_example
weekly_groups = turn_cleaned.groupby(one_turnstile)

one_turnstile_weekly = weekly_groups.get_group(tuple(one_turnstile_example))
one_turnstile_weekly.agg({})

sns.lineplot(data=one_turnstile_weekly, x='day_of_week_num', \
y='entries_per_timestamp');

# to iterate through groupby object
# for name, group in weekly_groups[:4]:
one_turnstile_notime = ["c/a", "unit", "scp", "station"]
one_turnstile_example_no_time = ["A002", "R051", "02-00-00", "59 ST"]

weekly_one_turnstile = turn_cleaned.groupby(one_turnstile_notime)
one_turnstile_all_wks = weekly_one_turnstile.get_group(tuple(one_turnstile_example_no_time))

one_turnstile_all_wks

for name, group in one_turnstile_all_wks.groupby('week'):
    # plt.figure()
    sns.lineplot(data=group, x='day_of_week_num', \
    y='entries_per_timestamp');
