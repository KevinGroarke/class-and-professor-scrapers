from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementNotVisibleException
from selenium.common.exceptions import TimeoutException
import scrapy
import json
import time

class RMPSpider(scrapy.Spider):
    name = 'RMPSpider'
    start_urls = ['http://www.ratemyprofessors.com/campusRatings.jsp?sid=1079']

    def __init__(self):
        self.driver = webdriver.PhantomJS()
        self.driver.maximize_window()
        self.data = open('./rmpData', 'w+')

    def parse(self, response):
        self.driver.get(response.url)

        WebDriverWait(self.driver, 3).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="cookie_notice"]/a[1]'))
        )
        self.driver.find_element_by_xpath('//*[@id="cookie_notice"]/a[1]').click()

        WebDriverWait(self.driver, 3).until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="mainContent"]/div[1]/div/div[4]/div[3]/a[27]'))
        )
        self.driver.find_element_by_xpath('//*[@id="mainContent"]/div[1]/div/div[4]/div[3]/a[27]').click()

        # While the 'load more' button is still there keep loading more professors and ratings
        # It waits for all ajax connections to close
        # It is supposed to send 20 new elements with each 'load more', but for some reason it
        # sends less at some points (like 18 or 19 elements). 2527 should be loaded...some get lost?
        while True:
            try:
                WebDriverWait(self.driver, 3).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="mainContent"]/div[1]/div/div[5]/div/div[1]'))
                )
                WebDriverWait(self.driver, 3).until(
                    EC.element_to_be_clickable((By.XPATH, '//*[@id="mainContent"]/div[1]/div/div[5]/div/div[1]'))
                )

                self.driver.find_element_by_xpath('//*[@id="mainContent"]/div[1]/div/div[5]/div/div[1]').click()
                self.wait_for_ajax()

                time.sleep(1)  # Seems to be the only kinda reliable way to have it load the data...
            except (ElementNotVisibleException, TimeoutException) as e:
                break

        sel = scrapy.Selector(text=self.driver.page_source.encode('utf-8'))

        def str_to_float(str):
            try:
                return float(str)
            except ValueError:
                return None

        professor_names = map(lambda name: name.encode('utf-8')[:name.index('\n')],
                              sel.xpath('//*[@id="mainContent"]/div[1]/div/div[5]/ul/li/a/span[3]/text()').
                              extract()[::2])
        professor_ratings = map(str_to_float,
                                sel.xpath('//*[@id="mainContent"]/div[1]/div/div[5]/ul/li/a/span[2]/text()').extract())
        professor_infos = zip(professor_names, professor_ratings)

        json_data = []

        for professor_info in professor_infos:
           json_data.append({
               'professorName': professor_info[0],
               'rmpRating': professor_info[1]
           })

        #self.data.write(str(len(sel.xpath('//*[@id="mainContent"]/div[1]/div/div[5]/ul/li'))))
        self.data.write(unicode(json.dumps(json_data, indent=4)))

    def wait_for_ajax(self):
        ajax_done = False

        while not ajax_done:
            ajax_done = self.driver.execute_script('window.testing={timeouts:{},intervals:[]};window._setTimeout=window.setTimeout;window.setTimeout=function(callback,timeout){var handle=_.uniqueId();var timeoutId=window._setTimeout(function(){callback();delete window.testing.timeouts[handle]},timeout);window.testing.timeouts[handle]=timeoutId;return timeoutId};window._clearTimeout=window.clearTimeout;window.clearTimeout=function(timeoutId){var returnValue=window._clearTimeout(timeoutId);var timeoutToClear;_.each(window.testing.timeouts,function(storedTimeoutID,handle){if(storedTimeoutID===timeoutId){timeoutToClear=handle}});delete window.testing.timeouts[timeoutToClear];return returnValue};window._setInterval=window.setInterval;window.setInterval=function(cb,interval){var intervalId=window._setInterval(cb,interval);window.testing.intervals.push(intervalId);return intervalId};window._clearInterval=window.clearInterval;window.clearInterval=function(intervalId){var returnValue=window._clearInterval(intervalId);window.testing.intervals=_.without(window.testing.intervals,intervalId);return returnValue};return jQuery.active===0&&Object.keys(window.testing.timeouts).length===0&&window.testing.intervals.length===0;')