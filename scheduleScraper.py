from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import scrapy
import json
import re


class ScheduleSpider(scrapy.Spider):
    name = 'scheduleSpider'
    start_urls = ['https://act.ucsd.edu/scheduleOfClasses/scheduleOfClassesStudent.htm']

    def __init__(self):
        self.driver = webdriver.PhantomJS()
        self.driver = webdriver.Firefox()
        self.driver.maximize_window()
        self.data = open('./scheduleData', 'w+')

    def parse(self, response):
        self.driver.get(response.url)
        select = Select(self.driver.find_element_by_xpath('//*[@id="selectedSubjects"]'))
        num_options = len(select.options)
        json_data = []

        # Iterate over each subject listed in the combobox
        for i in range(num_options - 1):
            self.driver.get(response.url)

            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="selectedSubjects"]'))
            )

            Select(self.driver.find_element_by_xpath('//*[@id="selectedSubjects"]')).select_by_index(i)

            subject_selection = Select(self.driver.find_element_by_xpath('//*[@id="selectedSubjects"]')).options[i].text
            course_subject_long = subject_selection[(subject_selection.index('-') + 2):]
            course_subject = subject_selection[:(subject_selection.index('-') - 1)]

            self.driver.find_element_by_xpath('//*[@id="socFacSubmit"]').click()

            # Try to get the number of pages for this subject
            try:
                total_page_number = scrapy.Selector(text=unicode(self.driver.page_source)).xpath(
                    '//*[@id="socDisplayCVO"]/div[2]/table/tbody/tr/td[3]/text()[1]').extract_first(default='f 0)')
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
                    course_title = unicode(selector.xpath('.//text()').extract_first(default=''))

                    if '  ' in course_title:
                        course_title = course_title[:course_title.index('  ')]

                    course_number = unicode(selector.xpath('.//ancestor::td[1]/preceding-sibling::td[1]/text()').extract_first(
                        ''))
                    professor_name = selector.xpath(
                        './/ancestor::tr[1]//following-sibling::tr[1]/td/a/text()').extract_first(
                        default=None)

                    # Get non-linked version of name... TODO: not working
                    if not professor_name:
                        professor_name = selector.xpath(
                            './/ancestor::tr[1]//following-sibling::tr[1]/td/text()').extract_first(
                                default=None
                            )
                        if not re.search('[a-zA-z]', professor_name):
                            professor_name = ''

                    professor_name = unicode(professor_name)
                    professor_name = (professor_name[:professor_name.index('  ')] if professor_name else '')
                    json_data.append(
                        {
                            "courseSubject": course_subject,
                            "courseSubjectLong": course_subject_long,
                            "courseName": course_title,
                            "courseNumber": course_number,
                            "professorName": professor_name
                        }
                    )

        self.data.write(unicode(json.dumps(json_data, indent=4)))
