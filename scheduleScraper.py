from selenium import webdriver
from selenium.webdriver.support.ui import Select
import scrapy
import json


class ScheduleSpider(scrapy.Spider):
    name = 'scheduleSpider'
    start_urls = ['https://act.ucsd.edu/scheduleOfClasses/scheduleOfClassesStudent.htm']

    def __init__(self):
        self.driver = webdriver.PhantomJS()
        self.driver.set_window_size(1124, 850)
        self.data = open('./scheduleData', 'w+')

    def parse(self, response):
        self.driver.get(response.url)
        select = Select(self.driver.find_element_by_xpath('//*[@id="selectedSubjects"]'))
        num_options = len(select.options)
        json_data = []

        # Iterate over each subject listed in the combobox
        for i in range(num_options - 1):
            self.driver.get(response.url)
            Select(self.driver.find_element_by_xpath('//*[@id="selectedSubjects"]')).select_by_index(i)

            subject_selection = Select(self.driver.find_element_by_xpath('//*[@id="selectedSubjects"]')).options[i].text
            subject = subject_selection[(subject_selection.index('-') + 2):]
            subject_short = subject_selection[:(subject_selection.index('-') - 1)]

            self.driver.find_element_by_xpath('//*[@id="socFacSubmit"]').click()

            # Try to get the number of pages for this subject
            try:
                total_page_number = self.driver.find_element_by_xpath(
                    '//*[@id="socDisplayCVO"]/div[2]/table/tbody/tr/td[3]').text
                total_page_number = int(
                    total_page_number[(total_page_number.index('f') + 2):total_page_number.index(')')])
            except:
                total_page_number = 0

            # Iterate over each page in for the results of this subject
            for j in range(1, total_page_number + 1):
                self.driver.execute_script(
                    'window.location.href = \"https://act.ucsd.edu/scheduleOfClasses/scheduleOfClassesStudentResult'
                    '.htm?page=' + str(
                        j) + '\"')
                result_selector = scrapy.Selector(text=self.driver.page_source.encode('utf-8'))
                course_selectors = result_selector.xpath('//*[@id="socDisplayCVO"]/table/tbody/tr/td[3]/a/span')

                # Iterate over each course selector. Its neighbor element will give the professor name (cant get any
                # other way)
                for selector in course_selectors:
                    course_title = selector.xpath('.//text()').extract_first(default='null').encode('utf-8')
                    course_number = selector.xpath('.//ancestor::td[1]/preceding-sibling::td[1]/text()').extract_first(
                        'null').encode('utf-8')
                    professor_name = selector.xpath(
                        './/ancestor::tr[1]//following-sibling::tr[1]/td/a/text()').extract_first(
                        default='null').encode('utf-8')
                    json_data.append(
                        {"courseSubjectShort": subject_short, "courseSubject": subject, "courseTitle": course_title,
                         "courseNumber": course_number,
                         "professor": {"name": professor_name, }})

        self.data.write(unicode(json.dumps(json_data, indent=4)))
