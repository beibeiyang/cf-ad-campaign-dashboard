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
from bokeh.charts import HeatMap

import numpy as np

class AdGroupMetrics(server.App):
    title = "Ad Campaigns Metrics"

    inputs = [
              {"type": 'dropdown',
               "label": 'Select Attribute for Analysis',
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
              ]

    controls = [{"type" : "hidden",
                    "label" : "ad campaigns metrics",
                    "id" : "update_data"
                }]

    outputs = [{"type" : "html",
                    "id" : "html_id",
                    "control_id" : "update_data",
                    "tab" : "Heatmap"},
               {"type": "table",
                "id": "table_id",
                "control_id": "update_data",
                "tab": "Table",
                "sortable": True,
                "on_page_load": False}]

    tabs = ["Heatmap", "Table"]

    def getData(self, params):
        if params['attribute'] == 'empty':
            return
        attribute = params['attribute']
        df = pd.read_csv('ad_table.csv')
        df = df.loc[:, ['date', 'ad', attribute]]
        return df

    def getHTML(self,params):
        #print ("params['attribute']", params['attribute'])
        if params['attribute']=='empty':
            return

        df = self.getData(params)  # get data

        #print(df.head())

        print ("params['attribute']:", params['attribute'])

        p = HeatMap(df, x='date', y='ad', values=str(params['attribute']), stat=None,
                    sort_dim={'x': False}, width=800, plot_height=500,
                    title='{} per Ad Group'.format(params['attribute']))

        script, div = components(p, CDN)
        html = "%s\n%s" % (script, div)
        return html

    def getCustomJS(self):
        return INLINE.js_raw[0]

    def getCustomCSS(self):
        return INLINE.css_raw[0]

if __name__ == '__main__':
    ml = AdGroupMetrics()
    ml.launch(host='0.0.0.0', port=8080)