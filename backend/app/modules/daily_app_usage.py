import pandas as pd

def daily_app_usage(df_events: pd.DataFrame, app_name: str = 'chrome.exe'):
    '''Calculates the time spent on each application each day'''
    # Parse string date to dateTime type of format Year-Month-Day
    df_events['timestamp'] = pd.to_datetime(df_events['timestamp'], format='ISO8601')
    df_events['timestamp'] = pd.to_datetime(df_events['timestamp'].dt.strftime("%Y-%m-%d"))

    # group by 'app' and 'timestamp' aggregating 'duration' by summing its values
    df_time_sum = df_events.groupby(['timestamp', 'app'], as_index=False).agg({'duration': 'sum'})
    df_events['duration'] = df_events['duration'] / 60.0 / 60.0 # seconds to hours

    # Select specific app
    df_time_sum = df_time_sum[df_time_sum['app'] == app_name]

    return df_time_sum