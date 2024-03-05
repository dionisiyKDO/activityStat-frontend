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
# Add some sort of a markers on a timeline of daily usage

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


def get_df() -> pd.DataFrame:
    df = pd.read_json(path_or_buf=path)
    return df

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
    
    return df_result

def plot_total_spent_time(df_og: pd.DataFrame):
    df_st = total_spent_time(df_og)
    df_st.sort_values('duration', ascending=False, inplace=True)

    # set lower threshold
    df_st = df_st[df_st['duration'] >= 10]
    print(df_st.head(30))

    fig = px.bar(df_st, x='app', y='duration', text_auto=True)
    fig.show()

def daily_app_usage_timeline(df_og: pd.DataFrame, app_name: str = 'chrome.exe'):
    '''Calculates the time spent on each application each day'''
    df_events = __extract_window_events(df_og)
    
    # Parse string date to dateTime type of format Year-Month-Day
    df_events['timestamp'] = pd.to_datetime(df_events['timestamp'], format='ISO8601')
    df_events['timestamp'] = pd.to_datetime(df_events['timestamp'].dt.strftime("%Y-%m-%d"))

    # group by 'app' and 'timestamp' aggregating 'duration' by summing its values
    df_time_sum = df_events.groupby(['timestamp', 'app'], as_index=False).agg({'duration': 'sum'})
    df_events['duration'] = df_events['duration'] / 60.0 / 60.0 # seconds to hours

    # Select specific app
    df_time_sum = df_time_sum[df_time_sum['app'] == app_name]

    # plot
    fig = px.bar(df_time_sum, x='timestamp', y='duration', title=f'Daily usage time of "{app_name}" over time',)
    fig.update_traces(hovertemplate='<b>Date:</b> %{x|%d %b %Y}<br><b>Usage time:</b> %{y}<br>')
    fig.update_layout(bargap=0.05, yaxis_title='Hours [h]', xaxis_title=None)
    fig.show()


if __name__ == '__main__':
    df_og = get_df()

    # total_spent_time
    plot_total_spent_time(df_og)

    # Daily usage time
    daily_app_usage_timeline(df_og, app_name='Risk of Rain 2.exe')
    