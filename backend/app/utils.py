import pandas as pd
import numpy as np
import re, os, json
from modules.spent_time import spent_time 
from modules.daily_app_usage import daily_app_usage 

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
pd.options.mode.chained_assignment = None
pd.options.display.precision = 2
data_path = 'data/aw-buckets-export.json'
cache_path = './data/cache/'

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
        df_data = df_og['buckets'][bucket_id]
        df_data.pop('data', None) # remove 'data' key with empty dict (for some reason fucking reason it is here), so it wouldnt cause an error - "ValueError: Mixing dicts with non-Series may lead to ambiguous ordering."
        df_bucket = pd.DataFrame(df_data)

        for ind in df_bucket.index:
            event = df_bucket['events'][ind]

            timestamp_arr.append(event['timestamp'])
            duration_arr.append(event['duration'])
            app_arr.append(event['data']['app'])
            title_arr.append(event['data']['title'])
    
    return pd.DataFrame({'timestamp': timestamp_arr, 'duration': duration_arr, 'app': app_arr, 'title': title_arr,})

def __save_cache(data, file_path):
    with open(cache_path + file_path, 'w') as f:
        json.dump(data.to_json(orient='records'), f)

def __load_cache(file_path):
    # TODO check empty file
    with open(cache_path + file_path, 'r') as f:
        return pd.read_json(json.load(f))

def __is_cache_valid(file_path):
    if not os.path.exists(cache_path + file_path):
        return False
    
    source_mtime = os.path.getmtime(data_path)
    cache_mtime = os.path.getmtime(cache_path + file_path)

    return cache_mtime > source_mtime


def get_spent_time():
    file_path = 'spent_time.json'
    if __is_cache_valid(file_path):
        result = __load_cache(file_path)
        return result.to_json(orient='records')
    else:
        df = __get_df()
        result = spent_time(df)
        __save_cache(data=result, file_path=file_path)
        return result.to_json(orient='records')

def get_daily_app_usage(app_name: str = 'chrome.exe'):
    '''Calculates the time spent on each application each day'''
    
    file_path = f'daily_app_usage/daily_app_usage_{app_name}.json'
    if __is_cache_valid(file_path):
        result = __load_cache(file_path)
        return result.to_json(orient='records')
    else:
        df = __get_df()
        result = daily_app_usage(df, app_name)
        __save_cache(data=result, file_path=file_path)
        return result.to_json(orient='records')
    
    



if __name__ == '__main__':
    print(get_spent_time())