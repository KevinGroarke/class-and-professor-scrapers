from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import scrapy
import time


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
        cape_courses = []

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
                course_name = course_selector.xpath('.//td[2]/a/text()').extract_first(default='not found')
                term = course_selector.xpath('.//td[3]/text()').extract_first(default='not found')
                recommend_class = course_selector.xpath('.//td[6]/span/text()').extract_first(default='not found')
                recommend_instructor = course_selector.xpath('.//td[7]/span/text()').extract_first(default='not found')
                study_hours = course_selector.xpath('.//td[8]/span/text()').extract_first(default='not found')
                avg_grade_exp = course_selector.xpath('.//td[9]/span/text()').extract_first(default='not found')
                avg_grade_rec = course_selector.xpath('.//td[10]/span/text()').extract_first(default='not found')

                self.data.write(professor_name + ' ' + course_name + ' ' + term + ' ' + recommend_class + ' ' +
                    recommend_instructor + ' ' + study_hours + ' ' + avg_grade_exp + ' ' + avg_grade_rec + '\n')