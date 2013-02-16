def format_chart_data(data, aspect):
    # Right now it's a decent heuristic to assume that
    # the aspect ends with the dimension we want.
    # We are only concerned with 2D data for now.
    dimension = aspect.split('_')[-1]
    return sorted([
        {'x': int(x), 'y': y[0][dimension]}
        for x, y in data.items()
    ], key = lambda k: k['x'])



def normalize_chart_series(series):
    numerator = max(series[0]['data'], key = lambda x: x['y'])['y']
    
    for i in range(1, len(series)):
        multiplier = numerator / max(series[i]['data'],
            key = lambda x: x['y'])['y']
        series[i]['data'] = [{'x': row['x'], 'y': row['y'] * multiplier
            } for row in series[i]['data']]
            
    return series
