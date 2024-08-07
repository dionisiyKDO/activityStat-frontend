import pandas as pd

def spent_time(df_og: pd.DataFrame, start_date: str = None, end_date: str = None, separate_buckets: bool = False) -> pd.DataFrame:
    '''Calculates the total time spent on each application'''
    # TODO use 'start_date' and 'end_date' to filter buckets
    
    df_events = df_og
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

    # return df_result.to_json(orient='records')
    return df_result