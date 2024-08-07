import pandas as pd
import numpy as np
import re

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
pd.options.mode.chained_assignment = None
pd.options.display.precision = 8
path = 'app/aw-buckets-export.json'


def get_df(path=path) -> pd.DataFrame:
    df = pd.read_json(path_or_buf=path)
    return df

def __extract_window_events(df_og: pd.DataFrame) -> pd.DataFrame:
    '''Extracts 'timestamp', 'duration', 'app', 'title' from a bucket DataFrame containing event data'''

    # Using regex find all 'window' buckets
    regex_pattern = r'aw-watcher-window_DESKTOP-[A-Za-z0-9]+'
    parse_buckets_id = []
    for ind in df_og.index:
        if re.match(regex_pattern, ind):
            parse_buckets_id.append(ind)

    timestamp_arr = []
    duration_arr = []
    app_arr = []
    title_arr = []

    # main loop
    for bucket_id in parse_buckets_id:
        df_bucket = pd.DataFrame(df_og['buckets'][bucket_id])

        for ind in df_bucket.index:
            event = df_bucket['events'][ind]

            timestamp_arr.append(event['timestamp'])
            duration_arr.append(event['duration'])
            app_arr.append(event['data']['app'])
            title_arr.append(event['data']['title'])
    
    return pd.DataFrame({'timestamp': timestamp_arr, 'duration': duration_arr, 'app': app_arr, 'title': title_arr,})

def total_spent_time(df_og: pd.DataFrame, separate_buckets: bool = False) -> pd.DataFrame:
    '''Calculates the total time spent on each application'''
    df_events = __extract_window_events(df_og)
    df_result = pd.DataFrame(columns=['app', 'duration'])
    
    # group by 'app' aggregating 'duration' by summing its values
    df_events = df_events.groupby(['app'], as_index=False).agg({'duration': 'sum'})
    df_events['duration'] = df_events['duration'] / 60.0 / 60.0 # seconds to hours
    df_events.sort_values('duration', ascending=False, inplace=True)
    
    df_result = pd.concat([df_result, df_events])
    
    if not separate_buckets:
        df_result = df_result.groupby(['app'], as_index=False).agg({'duration': 'sum'})
    
    df_result.sort_values('duration', ascending=False, inplace=True)
    df_result = df_result[df_result['duration'] >= 10]

    return df_result.to_json(orient='records')

if __name__ == '__main__':
    df = get_df('aw-buckets-export.json')
    print(total_spent_time(df))