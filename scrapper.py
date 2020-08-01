import requests
from bs4 import BeautifulSoup

from config import NEWS_WEBSITE_LINK

STRAITS_TIMES_HOME = NEWS_WEBSITE_LINK["straits_times"]


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
		self.articles = {}

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

	def _get_article_title(self, article_html):
		title = article_html.select("h1.headline.node-title")
		title = title[0].text

		return title

	def _get_article_content(self, article_html):
		article = article_html.find("div", class_="odd field-item", itemprop="articleBody")
		article = article.select("p")
		article = " ".join([para.text for para in article])
		article = article.replace("\n", "")
		#article = article.replace("\\", "")

		return article

	def _get_author(self, article_html):
		author = article_html.select("div.field-byline")

		if len(author) == 0:
			return None, None

		author = author[0]

		author_page = author.find("a", href=True)["href"]
		author = author.find("a").text

		return author, author_page

	def _get_article_date(self, article_html):
		date = article_html.select("div.story-postdate")[0].text
		date = date.replace("Published", "")

		return date

	def _get_article(self, link):
		article_page = requests.get(link, stream=True, headers={"User-Agent": "Mozilla/5.0"})

		if article_page.status_code == 200:
			article_html = BeautifulSoup(article_page.content, self.parser)
			title = self._get_article_title(article_html=article_html)
			author, author_page = self._get_author(article_html=article_html)
			date = self._get_article_date(article_html=article_html)
			content = self._get_article_content(article_html=article_html)

		return {"title": title, "author": author, "author_page": author_page, "date": date, "content": content, "link": link}

	def get_articles(self):
		if self.site == "straits_times":
			for category, links in self.article_links.items():
				for link in links:
					if type(link) == tuple and not self.logged_in:
						continue

					article = self._get_article(link=link)
					article["category"] = category

					title = article["title"]
					self.articles[title] = article

straits_times_scrapper = WebScrapper(link=STRAITS_TIMES_HOME, site="straits_times", parser="html.parser")
straits_times_scrapper.get_page()
straits_times_scrapper.parse_page()
straits_times_scrapper.get_article_links()
straits_times_scrapper.get_articles()


print(straits_times_scrapper.articles)








