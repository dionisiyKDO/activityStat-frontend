import pandas as pd
import numpy as np
import re, os, json
from modules import spent_time

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
pd.options.mode.chained_assignment = None
pd.options.display.precision = 8
data_path = 'aw-buckets-export.json'
cache_path = './cache/'

def __get_df(path=data_path) -> pd.DataFrame:
    df = pd.read_json(path_or_buf=path)
    df = __extract_window_events(df)
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

def __save_cache(data, file_name):
    with open(cache_path + file_name, 'w') as f:
        json.dump(data.to_json(orient='records'), f)

def __load_cache(file_name):
    # TODO check empty file
    with open(cache_path + file_name, 'r') as f:
        return pd.read_json(json.load(f))

def __is_cache_valid(file_name):
    if not os.path.exists(cache_path + file_name):
        return False
    
    source_mtime = os.path.getmtime(data_path)
    cache_mtime = os.path.getmtime(cache_path + file_name)

    return cache_mtime > source_mtime

def get_spent_time():
    file_name = 'spent_time.json'
    if __is_cache_valid(file_name):
        return __load_cache(file_name)
    else:
        df = __get_df()
        result = spent_time.spent_time(df)
        __save_cache(data=result, file_name=file_name)
        return result

if __name__ == '__main__':
    print(get_spent_time())