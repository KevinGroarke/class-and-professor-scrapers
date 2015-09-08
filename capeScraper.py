from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
import scrapy
import time
import json


class CapeInfo:

    def __init__(self, course_name='', course_number='', course_subject='', professor_name='',
               recommend_class=float(), recommend_professor=float(), study_hours=float(),
                 average_grade_expected=float(), average_grade_received=float(), term=''):
        self.course_name = course_name
        self.course_number = course_number
        self.course_subject = course_subject
        self.professor_name = professor_name
        self.capes = []

        cape = {
            "recommendClass": recommend_class,
            "recommendProfessor": recommend_professor,
            "studyHours": study_hours,
            "averageGradeExpected": average_grade_expected,
            "averageGradeReceived": average_grade_received,
            "term": term
        }

        self.capes.append(cape)

    def get_dict(self):
        recommend_class = float()
        recommend_professor = float()
        study_hours = float()
        average_grade_expected = float()
        average_grade_received = float()

        for cape in self.capes:
            recommend_class += cape["recommendClass"]
            recommend_professor += cape["recommendProfessor"]
            study_hours += cape["studyHours"]
            average_grade_expected += cape["averageGradeExpected"]
            average_grade_received += cape["averageGradeReceived"]

        def safe_div(numerator, denominator):
            if denominator > 0:
                return numerator / denominator
            else:
                return 0

        avg = {
            "recommendClass": safe_div(recommend_class, sum(x["recommendClass"] > 0 for x in self.capes)),
            "recommendProfessor": safe_div(recommend_professor, sum(x["recommendProfessor"] > 0 for x in self.capes)),
            "studyHours": safe_div(study_hours, sum(x["studyHours"] > 0 for x in self.capes)),
            "averageGradeExpected": safe_div(average_grade_expected,
                                             sum(x["averageGradeExpected"] > 0 for x in self.capes)),
            "averageGradeReceived": safe_div(average_grade_received,
                                             sum(x["averageGradeReceived"] > 0 for x in self.capes))
        }

        return {
            "professor_name": self.professor_name,
            "courseName": self.course_name,
            "courseNumber": self.course_number,
            "courseSubject": self.course_subject,
            "averageCape": avg,
            "capes": self.capes
        }

    def __hash__(self):
        return hash(str(self.course_name + self.course_subject + self.professor_name + str(self.course_number)))

    def __iadd__(self, other):
        self.data.write(unicode(json.dumps(self.capes, indent=4)))

    def __radd__(self, other):
        self.capes.extend(other.capes)
        return self


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
        cape_dict = {}

        # Navigate each subject's capes
        for option in options:
            option.click()

            # Sometimes it gave me an error that the submit button wasn't attached to the DOM...So loop till it is
            element_is_stale = True
            while element_is_stale:
                try:
                    WebDriverWait(self.driver, 60).until(
                        EC.presence_of_element_located((By.XPATH, '//*[@id="ctl00_ContentPlaceHolder1_btnSubmit"]'))
                        )
                    WebDriverWait(self.driver, 60).until(
                        EC.element_to_be_clickable((By.XPATH, '//*[@id="ctl00_ContentPlaceHolder1_btnSubmit"]'))
                        )

                    self.driver.find_element_by_xpath('//*[@id="ctl00_ContentPlaceHolder1_btnSubmit"]').click()
                    element_is_stale = False
                except StaleElementReferenceException:
                    continue

            # Wait based on the red spinning thing appearing and then disappearing (it's loading results)
            try:
                WebDriverWait(self.driver, 30).until(
                    EC.visibility_of_element_located((By.XPATH, '//*[@id="ctl00_ContentPlaceHolder1_UpdateProgress1"]/div/div/img'))
                    )
                WebDriverWait(self.driver, 60).until(
                    EC.invisibility_of_element_located((By.XPATH, '//*[@id="ctl00_ContentPlaceHolder1_UpdateProgress1"]/div/div/img'))
                    )
            except ValueError:
                self.data.write('sum error\n')

            # Pass the webpage navigated to by Selenium to Scrapy
            sel = scrapy.Selector(text=self.driver.page_source.encode('utf-8'))
            course_selectors = sel.xpath('//*[@id="ctl00_ContentPlaceHolder1_gvCAPEs"]/tbody/tr')

            for course_selector in course_selectors:
                professor_name = course_selector.xpath('.//td[1]/text()').extract_first(default=None)
                full_course_name = course_selector.xpath('.//td[2]/a/text()').extract_first(default=None)
                course_subject = full_course_name[:full_course_name.index(' ') ]
                course_number = full_course_name[(full_course_name.index(' ') + 1):(full_course_name.find('-') - 1)]
                course_name = full_course_name[(full_course_name.find('-') + 2):]
                term = course_selector.xpath('.//td[3]/text()').extract_first(default=None)
                recommend_class = course_selector.xpath('.//td[6]/span/text()').extract_first(default=float())
                recommend_professor = course_selector.xpath('.//td[7]/span/text()').extract_first(default=float())
                study_hours = course_selector.xpath('.//td[8]/span/text()').extract_first(default=float())
                avg_grade_exp = course_selector.xpath('.//td[9]/span/text()').extract_first(default=float())
                avg_grade_rec = course_selector.xpath('.//td[10]/span/text()').extract_first(default=float())

                # Converting strings to numbers
                if study_hours:
                    try:
                        study_hours = float(study_hours)
                    except ValueError:
                        study_hours = float()

                if recommend_class:
                    try:
                        recommend_class = float(recommend_class[:-2])
                    except (IndexError, ValueError) as e:
                        recommend_class = float()

                if recommend_professor:
                    try:
                        recommend_professor = float(recommend_professor[:-2])
                    except (IndexError, ValueError) as e:
                        recommend_professor = float()

                if avg_grade_exp:
                    try:
                        avg_grade_exp = \
                            float(avg_grade_exp[(avg_grade_exp.index('(') + 1):(avg_grade_exp.index(')') - 1)])
                    except (IndexError, ValueError) as e:
                        avg_grade_exp = float()

                if avg_grade_rec:
                    try:
                        avg_grade_rec = \
                            float(avg_grade_rec[(avg_grade_rec.index('(') + 1):(avg_grade_rec.index(')') - 1)])
                    except (IndexError, ValueError) as e:
                        avg_grade_rec = float()

                new_cape_info = CapeInfo(course_name, course_number, course_subject, professor_name, recommend_class,
                         recommend_professor, study_hours, avg_grade_exp, avg_grade_rec, term)

                # String versions of the hash returned are used since it doesn't seem to work otherwise...Too big num?
                if cape_dict.get(str(hash(new_cape_info))):
                    cape_dict[str(hash(new_cape_info))] = cape_dict[str(hash(new_cape_info))] + new_cape_info
                else:
                    cape_dict[str(hash(new_cape_info))] = new_cape_info

        json_data = map(lambda capeObj: capeObj.get_dict(), list(cape_dict.values()))
        self.data.write(unicode(json.dumps(json_data, indent=4)))
