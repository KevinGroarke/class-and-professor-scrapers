from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import scrapy
import re
import time

class RMPSpider(scrapy.Spider):
    name = 'rmpSpider'
    start_urls = ['http://www.ratemyprofessors.com/search.jsp?query=*&queryoption=HEADER&stateselect=&country=&dept=&queryBy=teacherName&facetSearch=true&schoolName=&offset=0&max=50%27']

    def __init__(self):
        self.driver = webdriver.phantomjs.webdriver.WebDriver('/usr/local/lib/node_modules/phantomjs/bin/phantomjs', 0, {})
        self.driver.set_window_size(1124,850)
        self.data = open('./data', 'w+')

    def parse(self, response):
        self.driver.get(response.url)
        self.driver.find_element_by_xpath('//*[@id="cookie_notice"]/a[1]').click()
        self.driver.execute_script("x = document.getElementsByName('schoolName')[2]; x.options[0].value = 'university of california san diego'; x.options[0].id = 'loopy'")
        select = Select(self.driver.find_element_by_xpath("//select[@id='schoolName']"))
        for option in select.options:
            self.data.write("stuff: " + option.text.encode('utf-8'))

        while True:
            sel = scrapy.Selector(text=self.driver.page_source.encode('utf-8'))
            links = sel.xpath('//*[@id="searchResultsBox"]/div[2]/ul/li/a/@href').extract()
            links = map(lambda link: response.urljoin(link.encode('utf-8')), links)
            
            for link in links:
                yield scrapy.Request(link, callback=self.parse_review)
            try: 
                WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, '#searchResultsBox > div.toppager > div.toppager-left > div.result-pager.hidden-md > a.nextLink'))
                    )
                self.driver.find_element_by_css_selector('#searchResultsBox > div.toppager > div.toppager-left > div.result-pager.hidden-md > a.nextLink').click()
            except ValueError:
                break

    def parse_review(self, response):
        first_name = re.sub('[^a-zA-Z]+', "", response.xpath('//*[@id="mainContent"]/div[2]/div[1]/div[2]/div[1]/span[1]/text()').extract_first(default='undefined').encode('utf-8'))
        last_name = re.sub('[^a-zA-Z]+', "", response.xpath('//*[@id="mainContent"]/div[2]/div[1]/div[2]/div[1]/span[3]/text()').extract_first(default='undefined').encode('utf-8'))
        rating = response.xpath('//*[@id="mainContent"]/div[2]/div[2]/div[1]/div[1]/div[1]/div/text()').extract_first(default='undefined').encode('utf-8')        
        letter_grade = response.xpath('//*[@id="mainContent"]/div[2]/div[2]/div[1]/div[1]/div[2]/div/text()').extract_first(default='undefined').encode('utf-8')
        helpfulness = response.xpath('//*[@id="mainContent"]/div[2]/div[2]/div[1]/div[2]/div[1]/div[2]/text()').extract_first(default='undefined').encode('utf-8')
        clarity = response.xpath('//*[@id="mainContent"]/div[2]/div[2]/div[1]/div[2]/div[2]/div[2]/text()').extract_first(default='undefined').encode('utf-8')
        easiness = response.xpath('//*[@id="mainContent"]/div[2]/div[2]/div[1]/div[2]/div[3]/div[2]/text()').extract_first(default='undefined').encode('utf-8')
        university = response.xpath('//*[@id="mainContent"]/div[2]/div[1]/div[2]/div[2]/a/text()').extract_first(default='undefined').encode('utf-8')
        if (first_name != 'undefined'):
            self.data.write('Professor: ' + first_name + ', ' + last_name + '\n')
            self.data.write('University: ' + university + '\n')
            self.data.write('Rating: ' + rating + '\n')
            self.data.write('Grade: ' + letter_grade + '\n')
            self.data.write('helpfulness: ' + helpfulness + '\n')
            self.data.write('clarity: ' + clarity + '\n')
            self.data.write('easiness: ' + easiness + '\n')
