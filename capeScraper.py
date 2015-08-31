from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import scrapy
import time
import json


class CapeSpider(scrapy.Spider):
    name = 'capeSpider'
    start_urls = ['http://cape.ucsd.edu/responses/index.html']

    def __init__(self):
        self.driver = webdriver.Firefox()
        self.data = open('./data', 'w+')

    def parse(self, response):
        self.driver.get(response.url)
        # Navigate to evaluation results
        self.driver.find_element_by_xpath('//*[@id="tdr_2_col_content"]/ul/li[2]/a').click()
        options = self.driver.find_element_by_xpath(
            '//*[@id="ctl00_ContentPlaceHolder1_ddlDepartments"]').find_elements_by_tag_name('option')
        options.pop(0)
        submit = self.driver.find_element_by_xpath('//*[@id="ctl00_ContentPlaceHolder1_btnSubmit"]')
        json_data = []

        # Navigate each subject's capes
        for option in options:
            option.click()

            # Sometimes it gave me an error that the submit button wasn't attached to the DOM...So just till it is
            try:
                WebDriverWait(self.driver, 60).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="ctl00_ContentPlaceHolder1_btnSubmit"]'))
                    )
                WebDriverWait(self.driver, 60).until(
                    EC.element_to_be_clickable((By.XPATH, '//*[@id="ctl00_ContentPlaceHolder1_btnSubmit"]'))
                    )
                # For some annoying reason, even though I got these tests I still gotta wait a sec or I get DOM error
                # 1/2 the time... tests fix it for 1/2 the time...time.sleep fixes for other half
                time.sleep(1)
                self.driver.find_element_by_xpath('//*[@id="ctl00_ContentPlaceHolder1_btnSubmit"]').click()
            except ValueError:
                self.data.write('couldn\'t click an option\n')

            # Wait based on the red spinning thing disappearing (it's loading results)
            time.sleep(1)
            try:
                WebDriverWait(self.driver, 60).until(
                    EC.invisibility_of_element_located((By.XPATH, '//*[@id="ctl00_ContentPlaceHolder1_UpdateProgress1"]/div/div/img'))
                    )
            except ValueError:
                self.data.write('sum error\n')

            sel = scrapy.Selector(text=self.driver.page_source.encode('utf-8'))
            course_selectors = sel.xpath('//*[@id="ctl00_ContentPlaceHolder1_gvCAPEs"]/tbody/tr')

            for course_selector in course_selectors:
                professor_name = course_selector.xpath('.//td[1]/text()').extract_first(default='not found')
                full_course_name = course_selector.xpath('.//td[2]/a/text()').extract_first(default='not found')
                course_subject = full_course_name[:full_course_name.index(' ') ]
                course_number = full_course_name[(full_course_name.index(' ') + 1):(full_course_name.find('-') - 1)]
                course_name = full_course_name[(full_course_name.find('-') + 2):]
                term = course_selector.xpath('.//td[3]/text()').extract_first(default='not found')
                recommend_class = course_selector.xpath('.//td[6]/span/text()').extract_first(default='not found')
                recommend_instructor = course_selector.xpath('.//td[7]/span/text()').extract_first(default='not found')
                study_hours = course_selector.xpath('.//td[8]/span/text()').extract_first(default='not found')
                avg_grade_exp = course_selector.xpath('.//td[9]/span/text()').extract_first(default='not found')
                avg_grade_rec = course_selector.xpath('.//td[10]/span/text()').extract_first(default='not found')

                #self.data.write(course_subject + '' + course_number + '' + course_name + '\n')
                json_data.append({"courseTitle": course_name, "courseNumber": course_number,
                                  "courseSubject": course_subject, "professorName": professor_name,
                                  "cape": {"recommendClass": recommend_class,
                                           "recommendInstructor": recommend_instructor,
                                           "studyHoursAWeek": study_hours,
                                           "averageGradeExpected": avg_grade_exp,
                                           "averageGradeRecieved": avg_grade_rec,
                                           "term": term
                                           }})

        self.data.write(unicode(json.dumps(json_data, indent=4)))
