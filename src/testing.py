import wikipedia
import pandas as pd
import sys

language = "de"
if len(sys.argv) == 2:
	queryDate = sys.argv[1]
else:
	queryDate = "2020/07/27"
EXCLUDED_TRENDS = ["Main_Page","Hauptseite","Pornhub"]

url = "https://wikimedia.org/api/rest_v1/metrics/pageviews/top/" + str(language) + ".wikipedia/all-access/" + str(queryDate)
wikiData = pd.read_json(url)
articles = pd.io.json.json_normalize(data=wikiData['items'][0]['articles']) # pd.json_normalize in latest version!
# filter out special pages
articles = articles[~articles['article'].str.contains(":")]
articles = articles[~articles['article'].isin(EXCLUDED_TRENDS)]
# take top 3
articles = articles.sort_values(by=['rank'])[:3]
print (articles['article'].values)
