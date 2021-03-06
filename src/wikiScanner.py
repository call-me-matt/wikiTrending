#!/usr/bin/python
# -*- coding: utf-8 -*-

import threading
import time
import logging
import subprocess
import string
import wikipedia
from datetime import date,timedelta
import pandas as pd

import databaseHandler

logging.basicConfig(format='[%(levelname)s] %(name)s: %(message)s',level=logging.INFO)
logger = logging.getLogger("wiki-scanner")

WEBSITE_CHECK_INTERVAL_HOURS = 8
EXCLUDED_TRENDS = ["Main_Page","Hauptseite"]

class wikiScanner (threading.Thread):

    def __init__(self):
        logger.info('starting wiki scanner')
        threading.Thread.__init__(self)

    def run(self):
        global WATCHDOG_INTERVAL_MIN
        while True:
            self.check()
            time.sleep(WEBSITE_CHECK_INTERVAL_HOURS*60*60)

        # never reached
        logger.info("exiting wiki scanner")

    def check(self):
        yesterday = (date.today() - timedelta(days = 1)).strftime("%Y/%m/%d")
        languages = databaseHandler.getLanguages()

        for language in languages:

            logger.debug('checking language ' + str(language))

            previouslyTrending = databaseHandler.getTrends(language, 1000)
            nowTrending = self.crawl(language, yesterday)
            if (len(nowTrending) == 0):
                continue
            logger.debug('Now trending (' + str(language) + "): " + str(nowTrending))
            newTrends = set(nowTrending) - set(previouslyTrending)
            if (len(newTrends) == 0):
                continue
            logger.info('New trends for ' + str(language) + ": " + str(newTrends))

            # save new trends in database
            for trend in newTrends:
                summary = self.getSummary(str(trend), str(language))
                if (summary != None):
                    databaseHandler.addTrend(str(language), str(trend), str(yesterday), str(summary))

    def crawl(self, language, queryDate):
        global EXCLUDED_TRENDS
        try:
            logger.debug ("checking wikipedia-" + str(language))

            url = "https://wikimedia.org/api/rest_v1/metrics/pageviews/top/" + str(language) + ".wikipedia/all-access/" + str(queryDate)
            wikiData = pd.read_json(url)
            articles = pd.json_normalize(data=wikiData['items'][0]['articles'])
            # filter out special pages
            articles = articles[~articles['article'].str.contains(":")]
            articles = articles[~articles['article'].isin(EXCLUDED_TRENDS)]
            # take top 3
            articles = articles.sort_values(by=['rank'])[:3]
            return (articles['article'].values)

        except:
            logger.warning ("could not get trends for " + str(language) + " (" + str(queryDate) + ")")
            return []

    def getSummary(self, title, language):
        wikipedia.set_lang(str(language))
        try:
            return (wikipedia.WikipediaPage(str(title)).summary)
        except:
            logger.warning("could not retrieve summary for " + str(title))
            return None

