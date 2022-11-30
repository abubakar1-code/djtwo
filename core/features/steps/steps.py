from behave import given, when, then
from helper import *
import time, datetime
import selenium.webdriver.support.ui as ui


# ------ Given -----------------------------the test
@given('The user is logged into Django Admin')
def step(context):
    login_to_django_admin(context)

@given('The test employee is logged into Django Admin')
def step(context):
    login_to_spotlit_test_employee(context)


@given('The test employee logs into Django Admin and creates a request')
def step(context):
    login_to_spotlit_test_employee(context)
    create_hr_individual_request(context)
    spotlit_logout(context)

@given('The manager logs into Django Admin and assigns the request to analyst1')
def step(context):
    login_to_spotlit_manager(context)
    assigns_individual_request(context)
    spotlit_logout(context)

@given('The analyst1 logs into Django Admin and completes request')
def step(context):
    login_to_spotlit_analyst(context)
    completes_individual_request(context)
    spotlit_logout(context)

@given('The admin has selected an individual report type')
def step(context):
    login_to_django_admin(context)
    select_and_save_individual_report(context)
    django_admin_logout(context)


@given('The admin has selected a corporate report type')
def step(context):
    login_to_django_admin(context)
    select_and_save_corporate_report(context)
    django_admin_logout(context)


# ------ WHEN -----------------------------

@when('The user goes to a companies dashboard')
def step(context):
    context.browser.find_element_by_xpath("//a[@href='/admin_console/core/company/']").click()
    context.browser.find_element_by_xpath("//*[contains(text(),'Selenium Company')]").click()

@when('The manager completes the request and accesses the Archived reports menu')
def step(context):
    login_to_spotlit_manager(context)
    complete_individual_request(context)
    time.sleep(5)

@when('The manager views archived reports')
def step(context):
    login_to_spotlit_manager(context)
    view_archived_reports(context)


@when('The manager accesses the Archived reports menu')
def step(context):
    context.browser.find_element_by_xpath("//a[@id='archiveReportsMenu']").click()
    time.sleep(15)
    wait = ui.WebDriverWait(context.browser,10)
    wait.until(lambda driver: driver.find_element_by_name('archived_reports_length'))
    context.browser.find_element_by_xpath("//select[@name='archived_reports_length']/option[text()='1000']").click()


# ------ Then -----------------------------
@then('The user should be able to select individual report types')
def step(context):
    web_element = Select(context.browser.find_element_by_id('id_individual_template'))
    web_element.select_by_visible_text('hr_report.html')
    context.browser.find_element_by_name('_continue').click()


@then('The user should be able to select corporate report types')
def step(context):
    web_element = Select(context.browser.find_element_by_id('id_corporate_template'))
    web_element.select_by_visible_text('hr_report.html')
    context.browser.find_element_by_name('_continue').click()


@then('The request should have been archived')
def step(context):
    formatted_date = datetime.datetime.today().strftime("%m/%d/%Y")
    obj1 = context.browser\
        .find_element_by_xpath("//*[contains(text(),'Selenium Company')]")

    obj2 = context.browser\
        .find_element_by_xpath("//*[contains(text(),'" + formatted_date + "')]")

    assert True, obj1
    assert True, obj2

@then('The request should have a report template type')
def step(context):
    report_template_name = 'hr_report.html'

    request_report_template_name = context.browser\
        .find_element_by_xpath("//*[contains(text(),'" + report_template_name + "')]")

    assert True, request_report_template_name
