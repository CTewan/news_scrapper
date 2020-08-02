import datetime

import requests
from bs4 import BeautifulSoup

from config import SGT
from db import DataBase


class WebScrapper(object):
	def __init__(self, link, site, parser="html.parser"):
		self.site = site
		self.link = link
		self.home_link = self.link.replace("/print-edition", "")
		self.parser = parser
		self.logged_in = False # For future use to scrap premium articles
		self.page = None
		self.html = None
		self.article_links= {}
		self.articles = []

	def _has_page(self):
		if self.page:
			return True

		return False

	def get_page(self):
		page = requests.get(self.link, stream=True, headers={"User-Agent": "Mozilla/5.0"})

		if page.status_code == 200:
			self.page = page

	def parse_page(self):
		if self._has_page():
			html = BeautifulSoup(self.page.content, self.parser)

			self.html = html

	def get_article_links(self):
		if self.site == "straits_times":
			segments = self.html.select("div.panel-pane.pane-views-panes.pane-articles-article-by-category-todays-paper-more.more-stories")
			
			for segment in segments:
				if segment is None:
					continue

				category = segment.select("h2.pane-title")[0].text
				category = category.replace("\n", "")
				category = category.strip()


				if category not in self.article_links.keys():
					self.article_links[category]= []
					self.article_links[category]

				story_segment = segment.select("span.story-headline")

				for story in story_segment:
					premium_article = story.select("div.paid-premium")
					article_link = story.find("a", href=True)
					article_link = self.home_link + article_link["href"]

					if len(premium_article) != 0:
						self.article_links[category].append(("premium", article_link))

					else:
						self.article_links[category].append(article_link)


	def retrieve_article_links(self):
		return self.article_links

	def _get_article_title(self, article_html, link):
		try:
			title = article_html.select("h1.headline.node-title")
			title = title[0].text

			return title
		
		except Exception as e:
			print(e)
			print(link)

	def _get_article_content(self, article_html, link):
		try:
			article = article_html.find("div", class_="odd field-item", itemprop="articleBody")

			if article is None:
				article = article_html.find("div", class_="odd field-item")

			article = article.select("p")
			article = " ".join([para.text for para in article])
			article = article.replace("\n", "")

			return article

		except Exception as e:
			print(e)
			print(link)

	def _get_author(self, article_html, link):
		author = article_html.select("div.field-byline")

		try:
			if len(author) == 0:
				return None, None

			author = author[0]


			author_page = author.find("a", href=True)

			if author_page:
				author_page = author_page["href"]
				author_page = self.home_link + author_page
				author = author.find("a").text

			else:
				author = author.text
				author = author.split("For")[0].strip()
				author_page = None

			return author, author_page
		
		except Exception as e:
			print(e)
			print(link)

	def _get_article_date(self, article_html, link):
		try:
			date = article_html.select("div.story-postdate")[0].text
			date = date.replace("Published", "")
			date = date.replace(" SGT", "")
			date = date.replace(":\xa0", "")

			if "hours" in date:
				hours_ago = date.replace(" hours ago", "")
				hours_ago = int(hours_ago)

				date = datetime.datetime.now() - datetime.timedelta(hours=hours_ago)
				date = date.astimezone(SGT)

			else:
				date = datetime.datetime.strptime(date, "%b %d, %Y, %H:%M %p")

			return date

		except Exception as e:
			print(e)
			print(link)

	def _get_article(self, link):
		article_page = requests.get(link, stream=True, headers={"User-Agent": "Mozilla/5.0"})

		if article_page.status_code == 200:
			article_html = BeautifulSoup(article_page.content, self.parser)
			title = self._get_article_title(article_html=article_html, link=link)
			author, author_page = self._get_author(article_html=article_html, link=link)
			date = self._get_article_date(article_html=article_html, link=link)
			content = self._get_article_content(article_html=article_html, link=link)

		return {"_id": title, "author": author, "author_page": author_page, "date": date, "content": content, "link": link}

	def get_articles(self):
		if self.site == "straits_times":
			for category, links in self.article_links.items():
				for link in links:
					if type(link) == tuple and not self.logged_in:
						continue

					article = self._get_article(link=link)
					article["category"] = category

					self.articles.append(article)










