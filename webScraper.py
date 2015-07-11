from selenium import webdriver
import scrapy
import re

class RMPSpider(scrapy.Spider):
    name = 'rmpSpider'
    start_urls = ['http://www.ratemyprofessors.com/search.jsp?query=*&queryoption=HEADER&stateselect=&country=&dept=&queryBy=teacherName&facetSearch=true&schoolName=&offset=0&max=50%27']

    def __init__(self):
        self.driver = webdriver.Firefox()
        self.data = open('./data', 'w+')

    def parse(self, response):
        self.driver.get(response.url)
        self.driver.find_element_by_xpath('//*[@id="cookie_notice"]/a[1]').click()
        
        while True:
            sel = scrapy.Selector(text=self.driver.page_source.encode('utf-8'))
            links = sel.xpath('//*[@id="searchResultsBox"]/div[2]/ul/li/a/@href').extract()
            links = map(lambda link: response.urljoin(link.encode('utf-8')), links)
            
            for link in links:
                yield scrapy.Request(link, callback=self.parse_review)

            self.driver.find_element_by_css_selector('#searchResultsBox > div.toppager > div.toppager-left > div.result-pager.hidden-md > a.nextLink').click()

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
