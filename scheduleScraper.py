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
            self.driver.find_element_by_xpath('//*[@id="socFacSubmit"]').click()

            result_selector = scrapy.Selector(text=self.driver.page_source.encode('utf-8'))
            def encode_text(element): return element.encode('utf-8')

            course_numbers = [num.encode('utf-8') for num in result_selector.xpath('//*[@id="socDisplayCVO"]/table/tbody/tr/td[2]/text()').extract() if len(str(num)) < 5]
            course_names = map(encode_text, result_selector.xpath('//*[@id="socDisplayCVO"]/table/tbody/tr/td[3]/a/span/text()').extract())
            course_instructors = map(encode_text, result_selector.xpath('//*[@id="socDisplayCVO"]/table/tbody/tr/td[10]/a/text()').extract())
            course_times = map(encode_text, result_selector.xpath('//*[@id="socDisplayCVO"]/table/tbody/tr/td[7]/text()').extract())

            courses = zip(course_numbers, course_names, course_instructors, course_times)
            self.data.write(str(len(course_numbers)) + ' ' +str(len(course_names)) + ' ' + str(len(course_instructors)) + ' ' +  str(len(course_times)) + ': ')
            
            all_columns = result_selector.xpath('//*[@id="socDisplayCVO"]/table/tbody/tr').extract()
            class_info = []
            index = 0
            
            self.data.write('before column length \n')
            self.data.write(len(all_columns) + '\n')
            for column in columns: self.data.write(column.encode('utf-8')) 
            
            '''while (index < len(all_columns)):
                self.data.write('shit not found\n')
                if (all_columns[index].css('.sectxt').extract_first(default='not-found').encode('utf-8') == 'not-found' and index > 0):
                    class_info.append([all_columns[index-1]]) # New class object, we added top purple bar element
                    self.data.write('shit class found ' + index + '\n')

                    while (all_columns[index].css('.sectxt').extract_first(default='not-found') != 'not-found' and index > 0):
                       class_info[len(class_info)-1].append(all_columns[index])  # Append class times to each class object
                       self.data.write('adding times shieeeet ' + index + '\n') 
                       index += 1
                index += 1 '''
