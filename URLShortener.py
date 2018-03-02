# brotatotes 3/1/2018

from lxml import html
import requests

class TinyURL():
	def __init__(self):
		pass

	def create(self, link):
		tinyurl_link = "https://tinyurl.com/create.php?url=" + link
		page = requests.get(tinyurl_link)
		tree = html.fromstring(page.content)
		tinyurl = tree.xpath("//*[@id='contentcontainer']/div[2]/b")
		if len(tinyurl) != 1:
			return None
		return tinyurl[0].text

