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
        assert chromedriver_path is not None

        if 'headless' in kwargs and kwargs['headless']:
            options = webdriver.ChromeOptions()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--window-size=1200,1000")
            self.driver = webdriver.Chrome(chromedriver_path, options=options)
        else:
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
        assert self.client_id is not None
        assert self.email is not None
        assert self.password is not None

    def login(self):
        self.driver.get(self.JOBCAN_URL)
        self.driver.find_element_by_id("client_id").send_keys(self.client_id)
        self.driver.find_element_by_id("email").send_keys(self.email)
        self.driver.find_element_by_id("password").send_keys(self.password)
        self.driver.find_element_by_css_selector("body > div > div > div.login-block > form > div:nth-child(5) > button").click()
        print("Logged in")

    def is_sidemenu_open(self):
        return self.driver.find_element_by_css_selector('#sidemenu').is_displayed()

    def is_sidemenu_closed(self):
        return self.driver.find_element_by_css_selector('#sidemenu-closed').is_displayed()

    def open_sidemenu(self):
        self.driver.find_element_by_css_selector('#sidemenu-closed > div > button').click()
        print("Opened sidemenu")

    def close_sidemenu(self):
        self.driver.find_element_by_css_selector('#sidemenu > div > button').click()
        print("Closed sidemenu")

    def open_man_hour_manage(self):
        if self.is_sidemenu_closed():  # headlessモードのとき
            print("Sidemenu is closed")
            self.open_sidemenu()
        self.driver.find_element_by_id("menu_man_hour_manage_img").click()
        self.driver.find_element_by_css_selector("#menu_man_hour_manage > a:nth-child(1)").click()
        print("Opened man hour manage")

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

    def get_current_year_and_month(self):
        WebDriverWait(self.driver, self.WAIT).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#search-term")))
        year_select_elm = self.driver.find_element_by_css_selector('#search-term > form > div > div > select[name="year"] > option[selected="1"]')
        year = int(year_select_elm.text)
        month_select_elm = self.driver.find_element_by_css_selector('#search-term > form > div > div > select[name="month"] > option[selected="1"]')
        month = int(month_select_elm.text)
        return year, month

    def set_current_year_and_month(self, year, month):
        WebDriverWait(self.driver, self.WAIT).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#search-term")))
        year_select_elm = self.driver.find_element_by_css_selector('#search-term > form > div > div > select[name="year"]')
        select = Select(year_select_elm)
        select.select_by_visible_text(str(year))
        month_select_elm = self.driver.find_element_by_css_selector('#search-term > form > div > div > select[name="month"]')
        select = Select(month_select_elm)
        select.select_by_visible_text(str(month).zfill(2))

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

    def input_data(self, index, project, task, hour):
        target_elm = self._select_record(index)
        select = Select(target_elm.find_element_by_css_selector("td > select"))
        select.select_by_visible_text(project)

        select = Select(target_elm.find_elements_by_css_selector("td > select")[1])
        select.select_by_visible_text(task)

        target_elm.find_element_by_css_selector("td > input.form-control.jbc-form-control.form-control-sm.man-hour-input").send_keys(hour.zfill(5))

    def remove_record(self, index):
        target_elm = self._select_record(index)
        target_elm.find_element_by_css_selector('td > span[onclick*="removeRecord"]').click()

    def save_data(self):
        WebDriverWait(self.driver, self.WAIT).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#save")))
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
