import pandas as pd
import numpy as np
import re, os, json
from modules.spent_time import spent_time 
from modules.daily_app_usage import daily_app_usage 

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
pd.options.mode.chained_assignment = None
pd.options.display.precision = 2

data_path = os.path.join('data', 'aw-buckets-export.json')
cache_path = os.path.join('data', 'cache')

def __get_df(path=data_path) -> pd.DataFrame:
    try:
        df = pd.read_json(path_or_buf=path)
        df = __extract_window_events(df)
        return df
    except ValueError as e:
        print(f"Error reading JSON data from {path}: {e}")
        return pd.DataFrame()
    except Exception as e:
        print(f"Unexpected error: {e}")
        return pd.DataFrame()

def __extract_window_events(df_og: pd.DataFrame) -> pd.DataFrame:
    '''Extracts 'timestamp', 'duration', 'app', 'title' from a bucket DataFrame containing event data'''

    regex_pattern = r'aw-watcher-window_DESKTOP-[A-Za-z0-9]+'
    parse_buckets_id = [ind for ind in df_og.index if re.match(regex_pattern, ind)]

    timestamp_arr, duration_arr, app_arr, title_arr = [], [], [], []

    for bucket_id in parse_buckets_id:
        df_data = df_og['buckets'].get(bucket_id, {}) # i think it's safer to use get() because it will return an empty dict if the key is not found
        df_data.pop('data', None) # remove 'data' key with empty dict (for some fucking reason it is here), so it wouldnt cause an error - "ValueError: Mixing dicts with non-Series may lead to ambiguous ordering."
        df_bucket = pd.DataFrame(df_data)

        for ind in df_bucket.index:
            event = df_bucket['events'][ind]
            try:
                timestamp_arr.append(event['timestamp'])
                duration_arr.append(event['duration'])
                app_arr.append(event['data']['app'])
                title_arr.append(event['data']['title'])
            except KeyError as e:
                print(f"Missing key in event data: {e}")

    return pd.DataFrame({'timestamp': timestamp_arr, 'duration': duration_arr, 'app': app_arr, 'title': title_arr})

def __save_cache(data, file_path):
    full_path = os.path.join(cache_path, file_path)
    try:
        os.makedirs(os.path.dirname(full_path), exist_ok=True)  # Ensure the directory exists
        with open(full_path, 'w') as f:
            json.dump(data.to_json(orient='records'), f)
    except IOError as e:
        print(f"Error saving cache to {full_path}: {e}")

def __load_cache(file_path):
    # TODO: check empty file
    full_path = os.path.join(cache_path, file_path)
    try:
        with open(full_path, 'r') as f:
            return pd.read_json(json.loads(f.read()))
    except ValueError as e:
        print(f"Error reading cache from {full_path}: {e}")
        return pd.DataFrame()
    except Exception as e:
        print(f"Unexpected error: {e}")
        return pd.DataFrame()

def __is_cache_valid(file_path):
    full_path = os.path.join(cache_path, file_path)
    try:
        if not os.path.exists(full_path):
            return False
        
        if os.path.getsize(full_path) == 0:
            print(f"Cache file {full_path} is empty.")
            return False

        source_mtime = os.path.getmtime(data_path)
        cache_mtime = os.path.getmtime(full_path)

        return cache_mtime > source_mtime
    except OSError as e:
        print(f"Error checking cache validity: {e}")
        return False

def get_spent_time():
    # TODO: different result with different hyperparameters, take this into account when saving cache
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
    
    file_path = os.path.join('daily_app_usage', f'daily_app_usage_{app_name}.json')
    if __is_cache_valid(file_path):
        result = __load_cache(file_path)
        return result.to_json(orient='records')
    else:
        df = __get_df()
        result = daily_app_usage(df, app_name)
        __save_cache(data=result, file_path=file_path)
        return result.to_json(orient='records')
