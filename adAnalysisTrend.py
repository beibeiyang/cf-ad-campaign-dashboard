# tested with python2.7 and 3.4
from spyre import server

import pandas as pd
try:
    import urllib.request as urllib2
except ImportError:
    import urllib2

from bokeh.resources import INLINE
from bokeh.resources import CDN
from bokeh.embed import components

from bokeh.plotting import figure
from bokeh.palettes import Set2
import numpy as np

class HoltWinter:
    forecast = []
    def __init__(self, series, slen, alpha, beta, gamma, n_preds):
        self.forecast = self.triple_exponential_smoothing(series, slen, alpha, beta, gamma, n_preds)

    def initial_trend(self, series, slen):
        sum = 0.0
        for i in range(slen):
            sum += float(series[i + slen] - series[i]) / slen
        return sum / slen

    def initial_seasonal_components(self, series, slen):
        seasonals = {}
        season_averages = []
        n_seasons = int(len(series) / slen)
        # compute season averages
        for j in range(n_seasons):
            season_averages.append(sum(series[slen * j:slen * j + slen]) / float(slen))
        # compute initial values
        for i in range(slen):
            sum_of_vals_over_avg = 0.0
            for j in range(n_seasons):
                sum_of_vals_over_avg += series[slen * j + i] - season_averages[j]
            seasonals[i] = sum_of_vals_over_avg / n_seasons
        return seasonals

    def triple_exponential_smoothing(self, series, slen, alpha, beta, gamma, n_preds):
        result = []
        smooth = 0.0
        trend = 0.0
        seasonals = self.initial_seasonal_components(series, slen)
        for i in range(len(series) + n_preds):
            if i == 0:  # initial values
                smooth = series[0]
                trend = self.initial_trend(series, slen)
                result.append(series[0])
                continue
            if i >= len(series):  # we are forecasting
                m = i - len(series) + 1
                result.append((smooth + m * trend) + seasonals[i % slen])
            else:
                val = series[i]
                last_smooth, smooth = smooth, alpha * (val - seasonals[i % slen]) + (1 - alpha) * (smooth + trend)
                trend = beta * (smooth - last_smooth) + (1 - beta) * trend
                seasonals[i % slen] = gamma * (val - smooth) + (1 - gamma) * seasonals[i % slen]
                result.append(smooth + trend + seasonals[i % slen])
        return result

class TrendAnalysis(server.App):
    title = "Trend Analysis"

    adgrp_options = [{"label": "-- Ad Group --", "value":"empty"}]
    for n in range(1, 41):
        adgrp = "ad_group_{}".format(n)
        adgrp_options.append({"label": adgrp, "value": adgrp})

    inputs = [{"type":'dropdown',
               "label": 'Select Ad Group',
               "options" : adgrp_options,
               "key": 'ad',
               "action_id": "update_data",
               # "linked_key": 'attribute',
               # "linked_type": 'dropdown',
              },
              {"type": 'dropdown',
               "label": 'Select Attribute for Trend Analysis',
               "options": [{"label": "-- Attribute --", "value":"empty"},
                           {"label": "Shown", "value": "shown"},
                           {"label": "Clicked", "value": "clicked"},
                           {"label": "Conversions", "value": "converted"},
                           {"label": "Average Cost per Click", "value": "avg_cost_per_click"},
                           {"label": "Total Revenue", "value": "total_revenue"},
                           ],
               "key": 'attribute',
               "action_id": "update_data",
               }
            # {	"type":'text',
            #     "label": 'or enter a ticker symbol',
            #     "key": 'custom_ticker',
            #     "action_id": "update_data",
            #     "linked_key":'ticker',
            #     "linked_type":'dropdown',
            #     "linked_value":'empty' }
              ]

    controls = [{"type" : "hidden",
                    "label" : "trend analysis",
                    "id" : "update_data"
                }]

    outputs = [{"type" : "html",
                    "id" : "html_id",
                    "control_id" : "update_data",
                    "tab" : "Trend"},
               {"type": "table",
                "id": "table_id",
                "control_id": "update_data",
                "tab": "Table",
                "sortable": True,
                "on_page_load": False}]

    tabs = ["Trend", "Table"]

    def getData(self, params):
        ad = params['ad']
        attribute = params['attribute']
        df = pd.read_csv('ad_table.csv')
        # df = df[df.ad==ad].loc[:, ['date', attribute]]
        # series = pd.Series(df[df.ad == ad].loc[:, attribute].tolist(), index=df[df.ad == ad].date)
        # series.index = pd.to_datetime(series.index, format='%Y-%m-%d')
        # return series

        df = pd.DataFrame(df[df.ad == ad].loc[:, ['date', attribute]])
        df.date = pd.to_datetime(df.date, format='%Y-%m-%d')
        return df

    # def getPlot(self, params):
    #     df = self.getData(params)
    #     plt_obj = df.set_index('Date').drop(['volume'],axis=1).plot()
    #     plt_obj.set_ylabel("Price")
    #     plt_obj.set_title(self.company_name)
    #     fig = plt_obj.get_figure()
    #     return fig

    def getHTML(self,params):

        if params['attribute']=='empty' or params['ad']=='empty':
            return

        df = self.getData(params)  # get data

        ts = pd.Series(df.loc[:, params['attribute']].tolist(), index=df.date)

        forecast = HoltWinter(ts, 12, 0.716, 0.029, 0.993, 23).forecast

        p = figure(plot_width=800, plot_height=500, x_axis_type="datetime",
                   title="Trend Forecast with Holt Winters on {} of {}".format(params['attribute'], params['ad']),
                   x_axis_label="date", y_axis_label=params['attribute'])

        # p.left[0].formatter.use_scientific = False

        p.line(ts.index,
               ts.as_matrix().astype(np.int),
               line_color=Set2[3][0], line_width=2, alpha=0.5,
               legend=params['attribute'])

        from datetime import date
        a = [0, max(ts)]
        b = [date(2015, 11, 22), date(2015, 11, 22)]
        p.line(b, a, line_color="gray", line_dash=(4, 4))

        p.line(ts.index.union(pd.date_range('2015-11-23', '2015-12-15')),
               forecast,
               line_color=Set2[3][1], line_width=2, alpha=0.7,
               legend="forecast")

        # print("Forecast {}'s shown on 2015-12-15: {}".format(params['ad'], int(round(forecast[-1]))))
        p.legend.location = "bottom_left"

        script, div = components(p, CDN)
        html = "%s\n%s" % (script, div)
        return html

    def getCustomJS(self):
        return INLINE.js_raw[0]

    def getCustomCSS(self):
        return INLINE.css_raw[0]

if __name__ == '__main__':
    ml = TrendAnalysis()
    ml.launch(host='0.0.0.0', port=8080)