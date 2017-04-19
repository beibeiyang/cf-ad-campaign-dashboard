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
from bokeh.charts import Bar
from bokeh.charts.attributes import CatAttr

class AdExploration(server.App):
    title = "Explore the Ad Campaign Dataset"

    adgrp_options = [{"label": "-- Ad Group --", "value": "empty"}]
    for n in range(1, 41):
        adgrp = "ad_group_{}".format(n)
        adgrp_options.append({"label": adgrp, "value": adgrp})

    date_options = [{"label": "-- Date --", "value": "empty"}]
    for d in pd.date_range('2015-10-01', '2015-11-22'):
        d = d.strftime('%Y-%m-%d')
        date_options.append({"label": d, "value": d})

    inputs = [{"type": 'dropdown',
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
               },
              {"type": 'dropdown',
               "label": 'Either Select an Ad Group',
               "options": adgrp_options,
               "key": 'ad',
               "action_id": "update_data",
               },
              {
                  "type": 'dropdown',
                  "label": 'or Select a Date',
                  "options": date_options,
                  "key": 'date',
                  "action_id": "update_data",
              },
              ]

    controls = [{"type" : "hidden",
                    "label" : "ad group exploration",
                    "id" : "update_data"
                }]

    outputs = [{"type" : "html",
                    "id" : "html_id",
                    "control_id" : "update_data",
                    "tab" : "Distribution"},
               {"type": "table",
                "id": "table_id",
                "control_id": "update_data",
                "tab": "Table",
                "sortable": True,
                "on_page_load": False}]

    tabs = ["Distribution", "Table"]

    def getData(self, params):
        ad = params['ad']
        date = params['date']
        attribute = params['attribute']

        df = pd.read_csv('ad_table.csv')

        if ad != 'empty':
            # retrieve date, attribute of the chosen ad group
            df = df[df.ad==ad].loc[:, ['date', attribute]]
            return df

        if date != 'empty':
            # retrieve ad, attribute of a specific date
            df = df[df.date == date].loc[:, ['ad', attribute]]

        return df

    def getHTML(self,params):
        ad = params['ad']
        date = params['date']
        attribute = params['attribute']

        if attribute == 'empty':
            return """<p>ACME is a food delivery company. Like pretty much any other site, in order to get customers, they
            have been relying significantly on online ads, such as those you see on Google or Facebook. At the moment,
            they are running 40 different ad campaigns and they want to better understand the performance.</p> <p>Please select
            an attribute from the left menu to explore the data.</p>"""

        if ad != 'empty' and date != 'empty':
            return "Please only select either Ad Group or Date"

        if ad == 'empty' and date == 'empty':
            return "Please select either Ad Group or Date to explore the data"

        df = self.getData(params)  # get data

        print(df.head())

        if date != 'empty':
            p = Bar(df, label=CatAttr(columns=['ad'], sort=False), values=attribute,
                    width=800, plot_height=500,
                    title="{} on {} by Ad Group".format(attribute, date),
                    legend=False)
        if ad != 'empty':
            p = Bar(df, 'date', values=attribute,
                    width=800, plot_height=500,
                    title="{} of {} by date".format(attribute, ad),
                    legend=False)


        script, div = components(p, CDN)
        html = "%s\n%s" % (script, div)
        return html

    def getCustomJS(self):
        return INLINE.js_raw[0]

    def getCustomCSS(self):
        return INLINE.css_raw[0]
#
if __name__ == '__main__':
    ml = AdExploration()
    ml.launch(host='0.0.0.0', port=8080)