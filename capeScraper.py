from selenium import webdriver
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
        self.driver.find_element_by_xpath('//*[@id="tdr_2_col_content"]/ul/li[2]/a').click()
        options = self.driver.find_element_by_xpath('//*[@id="ctl00_ContentPlaceHolder1_ddlDepartments"]').find_elements_by_tag_name('option')
        options.pop(0)
        submit = self.driver.find_element_by_xpath('//*[@id="ctl00_ContentPlaceHolder1_btnSubmit"]')

        for option in options:
            option.click()
            submit.click()
            
            time.sleep(5)
            def Get_Text(element): 
                return element.text
            instructors = map(Get_Text, self.driver.find_elements_by_xpath('//*[@id="ctl00_ContentPlaceHolder1_gvCAPEs"]/tbody/tr/td[1]'))
            courses = map(Get_Text, self.driver.find_elements_by_xpath('//*[@id="ctl00_ContentPlaceHolder1_gvCAPEs"]/tbody/tr/td[2]'))
            term = map(Get_Text, self.driver.find_elements_by_xpath('//*[@id="ctl00_ContentPlaceHolder1_gvCAPEs"]/tbody/tr/td[3]'))
            enroll = map(Get_Text, self.driver.find_elements_by_xpath('//*[@id="ctl00_ContentPlaceHolder1_gvCAPEs"]/tbody/tr/td[4]'))
            evals_made = map(Get_Text, self.driver.find_elements_by_xpath('//*[@id="ctl00_ContentPlaceHolder1_gvCAPEs"]/tbody/tr/td[5]'))
            rcmnd_instr = map(Get_Text, self.driver.find_elements_by_xpath('//*[@id="ctl00_ContentPlaceHolder1_gvCAPEs"]/tbody/tr/td[6]'))
            study_hrswk = map(Get_Text, self.driver.find_elements_by_xpath('//*[@id="ctl00_ContentPlaceHolder1_gvCAPEs"]/tbody/tr/td[7]'))
            avg_grade_exp = map(Get_Text, self.driver.find_elements_by_xpath('//*[@id="ctl00_ContentPlaceHolder1_gvCAPEs"]/tbody/tr/td[8]'))
            avg_grade_rec = map(Get_Text, self.driver.find_elements_by_xpath('//*[@id="ctl00_ContentPlaceHolder1_gvCAPEs"]/tbody/tr/td[9]'))

            reports = zip(instructors, courses, term, enroll, evals_made, rcmnd_instr, study_hrswk, avg_grade_exp, avg_grade_rec)

            for report in reports:
                self.data.write(report[0] + ' ' + report[1] + ' ' + report[2] + ' ' + report[3] + ' ' + report[4] + ' ' + report[5] + ' ' + report[6] + ' ' + report[7] + ' ' + report[8])

