import pyRserve

def frequency_counts(frequencies):
    """
    Takes a 2-dimensional array of dates in YYYY-mm-dd H:i:s format.
    Turns it into a 2-dimensional array of counts by hour.
    """
    
    # Find the max and min dates and times.
