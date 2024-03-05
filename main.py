import pandas as pd
import numpy as np
import plotly.express as px
import re

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
pd.options.mode.chained_assignment = None
pd.options.display.precision = 8
path = 'aw-buckets-export.json'

# TODO


def get_df() -> pd.DataFrame:
    df = pd.read_json(path_or_buf=path)
    return df

def __extract_events(df_bucket: pd.DataFrame) -> pd.DataFrame:
    '''Extracts 'timestamp', 'duration', 'app', 'title' from a bucket DataFrame containing event data'''
    timestamp_arr = []
    duration_arr = []
    app_arr = []
    title_arr = []
    
    for ind in df_bucket.index:
        event = df_bucket['events'][ind]

        timestamp_arr.append(event['timestamp'])
        duration_arr.append(event['duration'])
        app_arr.append(event['data']['app'])
        title_arr.append(event['data']['title'])
    
    return pd.DataFrame({'timestamp': timestamp_arr, 'duration': duration_arr, 'app': app_arr, 'title': title_arr,})


def total_spent_time(df_og: pd.DataFrame, separate_buckets: bool = False) -> dict[str: float]:
    '''Calculates the total time spent on each application'''
    df_result = pd.DataFrame(columns=['app', 'duration'])
    
    # Using regex find all 'window' buckets, since this function only works with them
    regex_pattern = r'aw-watcher-window_DESKTOP-[A-Za-z0-9]+'
    parse_buckets_id = []
    for ind in df_og.index:
        if re.match(regex_pattern, ind):
            parse_buckets_id.append(ind)

    # main loop
    for bucket_id in parse_buckets_id:
        df_bucket = pd.DataFrame(df_og['buckets'][bucket_id])
        df_events = __extract_events(df_bucket)

        # group by 'app' aggrevating 'duration'
        df_events = df_events.groupby(['app'], as_index=False).agg({'duration': 'sum'})
        df_events.sort_values('duration', ascending=False, inplace=True)
        
        # convert seconds to hours
        df_events['duration'] = df_events['duration'] / 60.0 / 60.0
        df_result = pd.concat([df_result, df_events])
    
    if not separate_buckets:
        df_result = df_result.groupby(['app'], as_index=False).agg({'duration': 'sum'})
    
    return df_result



if __name__ == '__main__':
    df_og = get_df()

    df_st = total_spent_time(df_og)
    df_st.sort_values('duration', ascending=False, inplace=True)

    # set lower threshold
    df_st = df_st[df_st['duration'] >= 10]

    fig = px.bar(df_st, x='app', y='duration', text_auto=True)
    fig.show()