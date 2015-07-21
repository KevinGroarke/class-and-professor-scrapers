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
            self.driver.find_element_by_xpath('//*[@id="ctl00_ContentPlaceHolder1_btnSubmit"]').click()

            time.sleep(5)
            sel = scrapy.Selector(text=self.driver.page_source.encode('utf-8'))
            def encode_text(element): 
                return element.encode('utf-8')
            instructors = map(encode_text, sel.xpath('//*[@id="ctl00_ContentPlaceHolder1_gvCAPEs"]/tbody/tr/td[1]/text()').extract())
            courses = map(encode_text, sel.xpath('//*[@id="ctl00_ContentPlaceHolder1_gvCAPEs"]/tbody/tr/td[2]/a/text()').extract())
            term = map(encode_text, sel.xpath('//*[@id="ctl00_ContentPlaceHolder1_gvCAPEs"]/tbody/tr/td[3]/text()').extract())
            enroll = map(encode_text, sel.xpath('//*[@id="ctl00_ContentPlaceHolder1_gvCAPEs"]/tbody/tr/td[4]/text()').extract())
            evals_made = map(encode_text, sel.xpath('//*[@id="ctl00_ContentPlaceHolder1_gvCAPEs"]/tbody/tr/td[5]/span/text()').extract())
            rcmnd_class = map(encode_text, sel.xpath('//*[@id="ctl00_ContentPlaceHolder1_gvCAPEs"]/tbody/tr/td[6]/span/text()').extract())
            rcmnd_instr = map(encode_text, sel.xpath('//*[@id="ctl00_ContentPlaceHolder1_gvCAPEs"]/tbody/tr/td[7]/span/text()').extract())
            study_hrswk = map(encode_text, sel.xpath('//*[@id="ctl00_ContentPlaceHolder1_gvCAPEs"]/tbody/tr/td[8]/span/text()').extract())
            avg_grade_exp = map(encode_text, sel.xpath('//*[@id="ctl00_ContentPlaceHolder1_gvCAPEs"]/tbody/tr/td[9]/span/text()').extract())
            avg_grade_rec = map(encode_text, sel.xpath('//*[@id="ctl00_ContentPlaceHolder1_gvCAPEs"]/tbody/tr/td[10]/span/text()').extract())

            reports = zip(instructors, courses, term, enroll, evals_made, rcmnd_instr, study_hrswk, avg_grade_exp, avg_grade_rec)
            
            #self.data.write(str(len(instructors)) + ' ' + str(len(courses)) + ' ' + str(len(term)) + ' ' + str(len(enroll)) + ' ' + str(len(evals_made)) + ' ' + str(len(rcmnd_instr)) + ' ' + str(len(study_hrswk)) + ' ' + str(len(avg_grade_exp)) + ' ' + str(len(avg_grade_rec)))
            for instructor in instructors:
                self.data.write(instructor)

            self.data.write('\nCOURSES NOW!')

            for course in courses:
                self.data.write(course)

            self.data.write('\nTERMS NOW!')

            for element in term:
                self.data.write(element)

            self.data.write('\nENROLL NOW!')

            for element in enroll:
                self.data.write(element)

            self.data.write('\nEvals made')

            for element in evals_made:
                self.data.write(element)

            self.data.write('\nrcmnd_class')

            for element in rcmnd_class:
                self.data.write(element)

            self.data.write('\nrcmnd_instr')

            for element in rcmnd_instr:
                self.data.write(element)

            self.data.write('\nstudy_hrswk')

            for element in study_hrswk:
                self.data.write(element)

            self.data.write('\navg_grade_exp')

            for element in avg_grade_exp:
                self.data.write(element)

            self.data.write('\navg_grade_rec')

            for element in avg_grade_rec:
                self.data.write(element)
            
            #for report in reports:
                #self.data.write(report[0] + ' ' + report[1] + ' ' + report[2] + ' ' + report[3] + ' ' + report[4] + ' ' + report[5] + ' ' + report[6] + ' ' + report[7] + ' ' + report[8])

