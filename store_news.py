from config import NEWS_WEBSITE_LINK

from scrapper import WebScrapper
from db import DataBase

STRAITS_TIMES_HOME = NEWS_WEBSITE_LINK["straits_times"]

straits_times_scrapper = WebScrapper(link=STRAITS_TIMES_HOME, site="straits_times", parser="html.parser")
straits_times_scrapper.get_page()
straits_times_scrapper.parse_page()
straits_times_scrapper.get_article_links()
straits_times_scrapper.get_articles()

articles = straits_times_scrapper.articles

news_db = DataBase()
news_db.connection()
news_db.get_db()
collection = news_db.get_collection(site="straits_times")
news_db.insert_data(collection=collection, data=articles)
