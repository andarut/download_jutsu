#!.venv/bin/python3.11

import os
import json
from bs4 import BeautifulSoup
import time

from enum import StrEnum

import re

import undetected_chromedriver as uc

from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementNotInteractableException

URLS_PATH = "urls.txt"

class Colors(StrEnum):
	HEADER = '\033[95m'
	BLUE = '\033[94m'
	CYAN = '\033[96m'
	GREEN = '\033[92m'
	YELLOW = '\033[93m'
	RED = '\033[91m'
	END = '\033[0m'
	BOLD = '\033[1m'
	UNDERLINE = '\033[4m'


class Logger:

	@staticmethod
	def print(text: str, color: str):
		print("[" + inspect.stack()[2].function.lower() + "]: " + color + text + Colors.END)

	@staticmethod
	def log(text):
		Logger.print(text, Colors.CYAN)

	@staticmethod
	def ok(text):
		Logger.print(text, Colors.GREEN)

	@staticmethod
	def error(text):
		Logger.print(text, Colors.RED)

	@staticmethod
	def warning(text):
		Logger.print(text, Colors.YELLOW)


class Element:

	def __init__(self, name: str|None, xpath: str|None):
		self.name = name
		self.xpath = xpath
		self.selenium_element: WebElement = WebElement(None, None)

	def text(self):
		return self.selenium_element.text

	def clear(self):
		self.selenium_element.clear()

	def type(self, text: str, clear=False, enter=False):
		# clear field
		if clear: self.clear()

		# type text
		self.selenium_element.send_keys(text)

		# hit enter
		if enter: self.selenium_element.send_keys(Keys.ENTER)

	def get(self, attr: str) -> str:
		res = self.selenium_element.get_attribute(attr)
		if res is None:
			Logger.error(f"{self.name} do not have attribute {attr}")
			return ""
		return res

	@staticmethod
	def none():
		return Element(None, None)

	def is_none(self):
		return self.name == None and self.xpath == None


class Engine:

	ACTION_TIMEOUT = 5
	STARTUP_TIMEOUT = 5

	def __init__(self, url: str, debug = os.environ.get('DEBUG', False)):
		self.url = url
		self.service = Service(executable_path='./driver')
		self.options = uc.ChromeOptions()
		self.options.add_argument("--mute-audio")
		self.DEBUG = debug
		self.driver = uc.Chrome(options=self.options, service=self.service)
		self.driver.maximize_window()
		self.driver.set_page_load_timeout(300)
		while True:
			try:
				self.driver.get(self.url)
				break
			except TimeoutException:
				Logger.warning(f"Driver timeout for {self.url}, trying again")
		time.sleep(self.STARTUP_TIMEOUT)

	def zoom(self, zoom):
		self.driver.execute_script(f"document.body.style.zoom='{zoom}%'")
		time.sleep(self.ACTION_TIMEOUT)

	def find_element(self, name: str, xpath: str) -> Element:
		element = Element(name, xpath)

		try:
			element.selenium_element = self.driver.find_element(By.XPATH, element.xpath)
		except NoSuchElementException:
			if self.DEBUG:
				Logger.error(f"{element.name} not found")
			return Element.none()

		if self.DEBUG:
			Logger.log(f"{element.name} found")

		return element

	def find_elements(self, name: str, class_name: str) -> list[Element]:
		elements = []

		try:
			for el in self.driver.find_elements(By.CLASS_NAME, class_name):
				element = Element(name, "")
				element.selenium_element = el
				elements.append(element)
		except NoSuchElementException:
			if self.DEBUG:
				Logger.error(f"{name} not found")
			return []

		if self.DEBUG:
			Logger.log(f"{name} found {len(elements)} times")

		return elements

	def click(self, element: Element):
		self.driver.execute_script("arguments[0].click();", element.selenium_element)
		if self.DEBUG:
			Logger.log(f"{element.name} clicked")
		time.sleep(self.ACTION_TIMEOUT)

	def type(self, element: Element, text: str, clear=False, enter=False) -> bool:
		try:
			element.type(text, clear, enter)
		except ElementNotInteractableException:
			return False
		if self.DEBUG:
			Logger.log(f"{element.name} typed {text} with clear={clear}, enter={enter}")
		time.sleep(self.ACTION_TIMEOUT)
		return True

	def quit(self):
		self.driver.quit()

class Downloader:

	@staticmethod
	def download_url(url, path):
		print(url, path)
		os.system(f"""
		curl '{url}' \
  --retry 10 \
  -H 'Accept: */*' \
  -H 'Accept-Language: ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7' \
  -H 'Connection: keep-alive' \
  -H 'Range: bytes=0-' \
  -H 'Referer: https://jut.su/' \
  -H 'Sec-Fetch-Dest: video' \
  -H 'Sec-Fetch-Mode: no-cors' \
  -H 'Sec-Fetch-Site: cross-site' \
  -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36' \
  -H 'sec-ch-ua: "Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "macOS"' \
  --output "{path}"
""")

	# TODO: support films
	@staticmethod
	def download(URL, DIR):
		engine = Engine(URL)
		soup = BeautifulSoup(engine.driver.page_source, features="html.parser")
		urls = []
		for a in soup.find_all('a', href=True):
			href = a['href']
			if ("episode" in href) and "html" in href and href not in urls:
				urls.append(f"https://jut.su{href}")
			# DEMO
			if len(urls) == 3: break

		print(f"FOUND {len(urls)} episods")
		for url in urls:
			print(url)

		video_urls = []
		for url in urls:
			engine.driver.get(url)
			path = os.path.basename(url)
			soup = BeautifulSoup(engine.driver.page_source, features="html.parser")
			video_urls.append(soup.find_all('source')[0]['src'])
		engine.quit()

		i = 1
		for video_url in video_urls:
			path = f"./episode_{i}.mp4"
			print(video_url, path)
			Downloader.download_url(video_url, path)
			i += 1



#  TODO: check for banned content and auto enable vpn
LIST = [

	# onepiece
	{
		"URL": "https://jut.su/oneepiece/"
	},

]

DIR = "."
for anime in list(LIST):
	Downloader.download(anime['URL'], DIR)
