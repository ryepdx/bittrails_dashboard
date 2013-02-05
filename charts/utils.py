def format_chart_data(data):
    return sorted([
        {'x': int(x), 'y': y}
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
