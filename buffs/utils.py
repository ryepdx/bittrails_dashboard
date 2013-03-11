from .models import BuffTemplate
from .constants import DEFAULT_TEMPLATE_KEY
import charts.utils

def template_key_from_correlation(correlation):
    key = ",".join(sorted(correlation['paths']))
    
    if correlation['correlation'] > 0.5:
        key = 'positive(%s)' % key
    elif correlation['correlation'] < -0.5:
        key = 'negative(%s)' % key
    else:
        key = 'neutral(%s)' % key

    return key
    
def get_template_for(correlation):
    template = BuffTemplate.find_one(
        {'key': template_key_from_correlation(correlation)}, as_obj = True)
    
    if not template:
        template = BuffTemplate.find_one(
            {'key': DEFAULT_TEMPLATE_KEY}, as_obj = True)

    return template
