#!/user/bin/env python

from spyre.server import Site, App

from adAnalysisExploration import AdExploration
from adAnalysisAdGroupMetrics import AdGroupMetrics
from adAnalysisTrend import TrendAnalysis


class Index(App):
    def getHTML(self, params):
        return "An Analysis on Ad Campaigns Effectiveness"


#site = Site(Index)

site = Site(AdExploration)

site.addApp(AdGroupMetrics, '/metrics')
site.addApp(TrendAnalysis, '/trend')

site.launch(host='0.0.0.0', port=8080)