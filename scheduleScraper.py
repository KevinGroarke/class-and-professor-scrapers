from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import scrapy
import time

class ScheduleSpider(scrapy.Spider):
    name = 'scheduleSpider'
    start_urls = ['https://act.ucsd.edu/scheduleOfClasses/scheduleOfClassesStudent.htm']

    def __init__(self):
        self.driver = webdriver.Firefox()
        self.data = open('./data', 'w+')

    def parse(self, response):
        self.driver.get(response.url)
        select = Select(self.driver.find_element_by_xpath('//*[@id="selectedSubjects"]'))
        num_options = len(select.options)

        for i in range(num_options):
            self.driver.get(response.url)
            Select(self.driver.find_element_by_xpath('//*[@id="selectedSubjects"]')).select_by_index(i)
            self.data.write(Select(self.driver.find_element_by_xpath('//*[@id="selectedSubjects"]')).options[i].text + '\n')
            self.data.write('----------------------------------\n')
            self.driver.find_element_by_xpath('//*[@id="socFacSubmit"]').click()

            try:
                total_page_number = self.driver.find_element_by_xpath('//*[@id="socDisplayCVO"]/div[2]/table/tbody/tr/td[3]').text
                total_page_number = int(total_page_number[(total_page_number.index('f') + 2):total_page_number.index(')')])
            except:
                total_page_number = 0
            
            self.data.write('Total page number is ' + str(total_page_number) + '\n')

            for j in range(1, total_page_number + 1):
                self.data.write('In loop\n')
                self.driver.execute_script('window.location.href = \"https://act.ucsd.edu/scheduleOfClasses/scheduleOfClassesStudentResult.htm?page=' + str(j) + '\"')
                result_selector = scrapy.Selector(text=self.driver.page_source.encode('utf-8'))
                table = result_selector.xpath('//*[@id="socDisplayCVO"]/table/tbody/tr')
                course_selectors = result_selector.xpath('//*[@id="socDisplayCVO"]/table/tbody/tr/td[3]/a/span')
                courses = []

                for selector in course_selectors:
                    self.data.write(selector.xpath('.//text()').extract_first(default='Course name not found').encode('utf-8'))
                    self.data.write(selector.xpath('.//ancestor::tr[1]//following-sibling::tr[1]/td/a/text()').extract_first(default='Instructor not found').encode('utf-8'))
                    self.data.write('\n\n')
