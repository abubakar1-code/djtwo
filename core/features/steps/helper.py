# Helper methods used to keep steps.py clean
import string, random, time
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import Select


def login_to_django_admin(context):
    context.browser.get('http://localhost:8000/admin_console')
    context.browser.find_element_by_id('id_username').send_keys('admin')
    context.browser.find_element_by_id('id_password').send_keys('admin')
    context.browser.find_element_by_xpath("//input[@type='submit']").click()

def spotlight_login(context):
    context.browser.get('http://localhost:8000/')
    check_exists_by_id_and_click(context, "djHideToolBarButton")

def login_to_spotlit(context):
    spotlight_login(context)
    context.browser.find_element_by_id('id_username').send_keys('admin')
    context.browser.find_element_by_id('id_password').send_keys('admin')
    context.browser.find_element_by_id("login").click()


def login_to_spotlit_manager(context):
    spotlight_login(context)
    context.browser.find_element_by_id('id_username').send_keys('manager')
    context.browser.find_element_by_id('id_password').send_keys('manager')
    context.browser.find_element_by_id("login").click()


def login_to_spotlit_analyst(context):
    spotlight_login(context)
    context.browser.find_element_by_id('id_username').send_keys('analyst1')
    context.browser.find_element_by_id('id_password').send_keys('analyst1')
    context.browser.find_element_by_id("login").click()


def login_to_spotlit_test_employee(context):
    spotlight_login(context)
    context.browser.find_element_by_id('id_username').send_keys('test')
    context.browser.find_element_by_id('id_password').send_keys('test')
    context.browser.find_element_by_id("login").click()


def create_hr_individual_request(context):
    context.browser.find_element_by_id('createRequest').click()
    context.browser.find_element_by_id('individualRequest').click()
    context.browser.find_element_by_xpath(
        "//select[@id='id_request_type']/option[text()='Human Resources - Essential']").click()
    context.browser.find_element_by_id('id_first_name').send_keys(string_generator())
    context.browser.find_element_by_id('submit-id-create_request').click()


def assigns_individual_request(context):
    view_individual_request(context, 'new_table', 1)
    context.browser.find_element_by_id('assignAnalyst').click()
    time.sleep(2)
    context.browser.find_element_by_xpath("//select[@id='analysts']/option[text()='analyst1, analyst1']").click()
    context.browser.find_element_by_id('assign').click()


def completes_individual_request(context):
    view_individual_request(context, 'new_table', 1)
    context.browser.find_element_by_id('begin').click()
    context.browser.find_element_by_id('id_executive_summary').send_keys(string_generator())
    context.browser.find_element_by_id('id_selection_10_2').click()
    context.browser.find_element_by_id('id_selection_11_2').click()
    context.browser.find_element_by_id('id_selection_12_2').click()
    context.browser.find_element_by_id('submit-id-submit_request').click()


def complete_individual_request(context):
    context.browser.find_element_by_xpath("//a[@href='#completed']").click()
    view_individual_request(context, 'completed_table', 1)
    context.browser.find_element_by_id('completeRequest').click()
    context.browser.find_element_by_id('submitted_comments').send_keys(string_generator())
    context.browser.find_element_by_id('submit').click()



def select_and_save_individual_report(context):
    context.browser.find_element_by_xpath("//a[@href='/admin_console/core/company/']").click()
    context.browser.find_element_by_xpath("//a[@href='/admin_console/core/company/1/']").click()
    web_element = Select(context.browser.find_element_by_id('id_individual_template'))
    web_element.select_by_visible_text('ashtree.html')
    context.browser.find_element_by_class_name('default').click()


def select_and_save_corporate_report(context):
    context.browser.find_element_by_xpath("//a[@href='/admin_console/core/company/']").click()
    context.browser.find_element_by_xpath("//a[@href='/admin_console/core/company/1/']").click()
    web_element = Select(context.browser.find_element_by_id('id_corporate_template'))
    web_element.select_by_visible_text('ashtree.html')
    context.browser.find_element_by_class_name('default').click()


def view_archived_reports(context):
    context.browser.find_element_by_id('archiveReportsMenu').click()
    web_element = Select(context.browser.find_element_by_name('archived_reports_length'))
    web_element.select_by_visible_text('100')





# Util


def spotlit_logout(context):
    logout_obj = context.browser.find_element_by_id('logoutDropdown')
    hover = ActionChains(context.browser).move_to_element(logout_obj)
    hover.perform()

    context.browser.find_element_by_id('logout').click()
    time.sleep(5)

def django_admin_logout(context):
    context.browser.find_element_by_xpath("//a[@href='/admin_console/logout/']").click()


def view_individual_request(context, table_name, row):
    context.browser.find_element_by_xpath(
        "//table[@id='" + table_name + "']/tbody/tr[" + str(row) + "]/td[1]/a").click()


def string_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def check_exists_by_id_and_click(context, id):
    try:
        context.browser.find_element_by_id(id).click()
    except NoSuchElementException:
        return False
    return True