import pandas as pd

def daily_app_usage(df_events: pd.DataFrame, app_name: str = 'chrome.exe'):
    """Calculates the time spent on a specified application each day."""
    # Ensure the necessary columns are present
    required_columns = {'timestamp', 'app', 'duration'}
    if not required_columns.issubset(df_events.columns):
        raise ValueError(f"Input DataFrame must contain the following columns: {required_columns}")
    
    # Check if the app_name is present in the DataFrame
    if app_name not in df_events['app'].unique():
        raise ValueError(f"The app_name '{app_name}' is not present in the DataFrame.")
    
    # Convert 'timestamp' to datetime and extract date part
    df_events['timestamp'] = pd.to_datetime(df_events['timestamp'], format='ISO8601').dt.date
    
    # Group by 'timestamp' and 'app' and sum the 'duration'
    df_time_sum = df_events.groupby(['timestamp', 'app'], as_index=False).agg({'duration': 'sum'})
    
    # Convert duration from seconds to hours
    df_time_sum['duration'] = df_time_sum['duration'] / 3600.0 # seconds to hours
    
    # Filter for the specific app
    df_time_sum = df_time_sum[df_time_sum['app'] == app_name]
    
    return df_time_sum