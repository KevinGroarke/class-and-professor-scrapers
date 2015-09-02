from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementNotVisibleException
import scrapy
import time
import json


class CapeSpider(scrapy.Spider):
    name = 'capeSpider'
    start_urls = ['http://www.ratemyprofessors.com/search.jsp?queryBy=schoolId&schoolName=University+of+California+San+Diego&schoolID=1079&queryoption=TEACHER']

    def __init__(self):
        self.driver = webdriver.Firefox()
        self.data = open('./data', 'w+')

    def parse(self, response):
        self.driver.get(response.url)
        self.driver.find_element_by_xpath('//*[@id="cookie_notice"]/a[1]').click()

        # While the 'load more' button is still there keep loading more professors and ratings
        while True:
            try:
                self.driver.find_element_by_xpath('//*[@id="mainContent"]/div[1]/div/div[5]/div/div[1]').click()
            except ElementNotVisibleException:
                break
        sel = scrapy.Selector(text=self.driver.page_source.encode('utf-8'))

        professor_names = map(lambda name: name.encode('utf-8'),
                              sel.xpath('//*[@id="mainContent"]/div[1]/div/div[5]/ul/li/a/span[3]/text()').extract())
        professor_ratings = map(lambda rating: rating.encode('utf-8'),
                                sel.xpath('//*[@id="mainContent"]/div[1]/div/div[5]/ul/li/a/span[2]/text()').extract())
        professor_infos = zip(professor_names, professor_ratings)

        json_data = []

        for professor_info in professor_infos:
           json_data.append({
               'professorName': professor_info[0],
               'rmpRating': professor_info[1]
           })

        self.data.write(unicode(json.dumps(json_data, indent=4)))
