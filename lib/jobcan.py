from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import datetime
import calendar
from collections import OrderedDict


class JobcanInput():
    def __init__(self, chromedriver_path, **kwargs):
        self.driver = webdriver.Chrome(chromedriver_path)
        if 'client_id' in kwargs:
            self.client_id = kwargs['client_id']
        else:
            self.client_id = os.environ['JOBCAN_CLIENT_ID']
        if 'email' in kwargs:
            self.email = kwargs['email']
        else:
            self.email = os.environ['JOBCAN_EMAIL']
        if 'password' in kwargs:
            self.password = kwargs['password']
        else:
            self.password = os.environ['JOBCAN_PASSWORD']
        self.JOBCAN_URL = 'https://ssl.jobcan.jp/employee'
        self.WAIT = 30  # sec

    def login(self):
        self.driver.get(self.JOBCAN_URL)
        self.driver.find_element_by_id("client_id").send_keys(self.client_id)
        self.driver.find_element_by_id("email").send_keys(self.email)
        self.driver.find_element_by_id("password").send_keys(self.password)
        self.driver.find_element_by_css_selector("body > div > div > div.login-block > form > div:nth-child(5) > button").click()

    def open_man_hour_manage(self):
        self.driver.find_element_by_id("menu_man_hour_manage_img").click()
        self.driver.find_element_by_css_selector("#menu_man_hour_manage > a:nth-child(1)").click()

    def select_date(self, date=None, open=True):
        if date:
            utime = self._datestr2unixtime(date)
            edit_btn_elm = WebDriverWait(self.driver, self.WAIT).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, f'div[onclick*="{utime}"]')))
        else:
            # first edit button
            edit_btn_elm = WebDriverWait(self.driver, self.WAIT).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '#search-result > table > tbody > tr > td > div[onclick]')))
        parent_elm = edit_btn_elm.find_element_by_xpath('./../..')
        cells = parent_elm.find_elements_by_css_selector("td")
        if open:
            edit_btn_elm.click()
        total_work_time = cells[1].text
        total_man_hour = cells[2].text
        # print(cells[1].text, cells[2].text)
        return total_work_time, total_man_hour

    def add_blank_record(self):
        add_btn_elm = WebDriverWait(self.driver, self.WAIT).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'span[onclick*="addRecord"]')))
        add_btn_elm.click()

        elms = self.driver.find_elements_by_css_selector("tr.daily")
        elms = [el for el in elms if not el.text == '']
        return len(elms)

    def get_unmatch_time(self):
        target_elm = WebDriverWait(self.driver, self.WAIT).until(
            EC.presence_of_element_located((By.ID, 'un-match-time')))
        if target_elm.text:
            un_match_time = target_elm.text.split(' ')[1]
        else:
            un_match_time = None
        # print(un_match_time)
        return un_match_time

    def get_projects_and_tasks(self):
        projects_and_tasks = OrderedDict()
        elms = self.driver.find_elements_by_css_selector("#edit-menu-contents > table > tbody > tr.daily[data-index='1'] > td > select[name='projects[]'] > option")
        projects = [e.text for e in elms if not e.text == '(未選択)']
        target_elm = self.driver.find_element_by_css_selector('#edit-menu-contents > table > tbody > tr.daily[data-index="1"]')
        select = Select(target_elm.find_element_by_css_selector("td > select"))
        for project in projects:
            select.select_by_visible_text(project)
            elms = self.driver.find_elements_by_css_selector("#edit-menu-contents > table > tbody > tr.daily[data-index='1'] > td > select[name='tasks[]'] > option")
            tasks = [e.text for e in elms if not e.text == '(未選択)']
            # print(project, tasks)
            projects_and_tasks[project] = tasks
        # print(projects_and_tasks)
        return projects_and_tasks

    def input_data(self, index, project, task, hour, save=False):
        target_elm = self._select_record(index)
        select = Select(target_elm.find_element_by_css_selector("td > select"))
        select.select_by_visible_text(project)

        select = Select(target_elm.find_elements_by_css_selector("td > select")[1])
        select.select_by_visible_text(task)

        target_elm.find_element_by_css_selector("td > input.form-control.jbc-form-control.form-control-sm.man-hour-input").send_keys(hour)
        if save:
            self.save_data()

    def save_data(self):
        self.driver.find_element_by_id("save").submit()

    def wait_save_completed(self):
        WebDriverWait(self.driver, self.WAIT).until(
            EC.invisibility_of_element_located((By.CSS_SELECTOR, "#man-hour-manage-modal")))

    def close(self):
        self.driver.find_element_by_id("menu-close").click()

    def quit(self):
        self.driver.quit()

    def save_screenshot(self, filename):
        self.driver.save_screenshot(filename)

    def _select_record(self, index=0):
        target_elm = WebDriverWait(self.driver, self.WAIT).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, f'tr.daily[data-index="{index + 1}"]')))
        return target_elm

    def _datestr2unixtime(self, date):
        date = date + " 00:00:00+0900"
        dt = datetime.datetime.strptime(date, "%Y/%m/%d %H:%M:%S%z")
        return calendar.timegm(dt.utctimetuple())
