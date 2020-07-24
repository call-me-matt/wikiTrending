#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging

from datetime import date 
from datetime import timedelta 

import wikipedia

import pandas as pd
from pandas.io.json import json_normalize #package for flattening json in pandas df

logging.basicConfig(format='[%(levelname)s] %(name)s: %(message)s',level=logging.INFO)
logger = logging.getLogger("main")

logger.info('starting wikiTrendsBot')

language = "de"
yesterday = (date.today() - timedelta(days = 1)).strftime("%Y/%m/%d")
url = "https://wikimedia.org/api/rest_v1/metrics/pageviews/top/" + str(language) + ".wikipedia/all-access/" + str(yesterday)
wikiData = pd.read_json(url)
articles = json_normalize(data=wikiData['items'][0]['articles'])
# filter out special pages
articles = articles[~articles['article'].str.contains(":")]
articles = articles[~articles['article'].str.contains("Main_Page")]
# take top 3
articles = articles.sort_values(by=['rank'])[:3]

logger.info('Trends for ' + str(language) + " (" + str(yesterday) + "): " + str(articles['article'].values))

wikipedia.set_lang(str(language))

for i in articles['article'].values:
    images = wikipedia.WikipediaPage(str(i)).images
    for image in images:
        if image.endswith('.svg'):
            continue
        print (str(image))
        break
