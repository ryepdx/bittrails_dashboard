import buffs.utils
import charts
import itertools

class CorrelationBuffCharts(object):
    def __init__(self, user, correlations, chart_prefix = "chart",
    colors = ['steelblue', 'tomato']):
        self.current_id = 0
        self.colors = itertools.cycle(colors)
        self.correlations = correlations
        self.user = user
        self.chart_prefix = chart_prefix
        
    def __iter__(self):
        return self
        
    def next(self):
        if self.current_id >= len(self.correlations):
            raise StopIteration
        else:
            correlation = self.correlations[self.current_id]
            template = buffs.utils.get_template_for(correlation)
            chart_data = charts.utils.json_for_correlation(
                self.user, correlation, color = self.colors.next())
            self.current_id += 1
            
            return {
                'text': template.render_using(correlation),
                'chart_data': chart_data,
                'chart_id': self.chart_prefix + str(self.current_id),
                'buff_id': correlation['_id'],
                'state': correlation['state'],
                'start': correlation['start'],
                'end': correlation['end'],
                'correlation': correlation['correlation'],
                'paths': correlation['paths']
            }
