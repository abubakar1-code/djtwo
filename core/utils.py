from __future__ import absolute_import

from django.contrib.auth.models import User, Group
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from .models import SpotLitStaff, CompanyEmployee, Request, CorporateRequest, CorporateRequestServiceStatus, \
    CompanyDueDiligenceTypeSelection, CompanyServiceSelection, SPOTLIT_MANAGER_GROUP, SPOTLIT_ANALYST_GROUP, \
    COMPANY_EMPLOYEE_GROUP,REGISTERED_CUSTOMER_GROUP,UNVERIFIED_USER_GROUP, Company, DynamicRequestForm, DynamicRequestFormFields, CustomRequest, CustomRequestFields,\
    LayoutGroupSections, REVIEWER, RequestServiceStatus, Status, CustomRequestServiceStatus,CompanyDisabledPackage

from .pdf_generator import generate_report_pdf_file

import os

import datetime

from django.db.models import Case, When


def get_template_type(request):
    if request.request_type.company is None:
        template = 'reports/comply_hr_report.html'
    else:
        if isinstance(request, CorporateRequest):
            print "request:",request.request_type
            if request.request_type.company.corporate_template is None or not request.request_type.company.corporate_template:
                template = 'reports/comply_third_party_reg_bus_report.html'
                if request.request_type.due_diligence_type.name == "Human Resources":
                    template = 'reports/comply_hr_report.html'
            else:
                head, tail = os.path.split(request.request_type.company.corporate_template)
                template = 'reports/' + tail

        else:
            print(request.request_type.company.individual_template)
            if request.request_type.company.individual_template is None or not request.request_type.company.individual_template:
                if request.request_type.due_diligence_type.name == "Human Resources":
                    template = 'reports/comply_hr_report.html'
                else:
                    template = 'reports/comply_third_party_reg_bus_report.html'
            else:
                head, tail = os.path.split(request.request_type.company.individual_template)
                template = 'reports/' + tail
    return template


def is_analyst(current_user):
    user_groups = current_user.groups.all()
    analyst_group = filter(lambda group: group.name == SPOTLIT_ANALYST_GROUP, user_groups)
    if (analyst_group):
        return True
    else:
        return False


def get_company_employee(current_user):
    employee = CompanyEmployee.objects.filter(user=current_user).first()
    return employee

def get_company_employees(company):
    company_employees = CompanyEmployee.objects.filter(company__name=company)
    return company_employees


def is_company_supervisor_mixin_check(user):
    potential_supervisor = get_company_employee(user)
    if potential_supervisor.supervisor:
        return True
    else:
        return False

def is_company_supervisor(user):
    if user.supervisor:
        return True
    else:
        return False


def is_company_employee(current_user):
    user_groups = current_user.groups.all()
    employee_group = filter(lambda group: group.name == COMPANY_EMPLOYEE_GROUP, user_groups)
    if (employee_group):
        return True
    else:
        return False

def is_registered_customer(current_user):
    user_groups = current_user.groups.all()
    registered_customer_group = filter(lambda group: group.name == REGISTERED_CUSTOMER_GROUP, user_groups)
    if (registered_customer_group):
        return True
    else:
        return False

def is_unverified_user(current_user):
    user_groups = current_user.groups.all()
    unverified_user_group = filter(lambda group: group.name == UNVERIFIED_USER_GROUP, user_groups)
    if (unverified_user_group):
        return True
    else:
        return False


def is_corporate_company_employee(current_user):
    try:
        employee = CompanyEmployee.objects.filter(company__is_corporate=True).filter(user=current_user).first()
        if employee:
            return True
        else:
            return False
    except:
        return False


def get_user_group(current_user):
    group = current_user.groups.filter(
        name__in=[SPOTLIT_ANALYST_GROUP, SPOTLIT_MANAGER_GROUP, COMPANY_EMPLOYEE_GROUP, REVIEWER,REGISTERED_CUSTOMER_GROUP,UNVERIFIED_USER_GROUP]).first()
    return group


def is_manager(current_user):
    user_groups = current_user.groups.all()

    manager_group = filter(lambda group: group.name == SPOTLIT_MANAGER_GROUP, user_groups)
    if (manager_group):
        return True
    else:
        return False

def is_reviewer(current_user):
    user_groups = current_user.groups.all()
    reviewer_group = filter(lambda group: group.name == REVIEWER, user_groups)
    if reviewer_group:
        return True
    else:
        return False


def get_company_employee_group():
    employee_group = Group.objects.filter(name=COMPANY_EMPLOYEE_GROUP).first()
    return employee_group

def get_registered_customer_group():
    registered_customer_group = Group.objects.filter(name=REGISTERED_CUSTOMER_GROUP).first()
    return registered_customer_group

def get_unverified_user_group():
    unverified_user_group = Group.objects.filter(name=UNVERIFIED_USER_GROUP).first()
    return unverified_user_group

def get_company_selections_in_dict(company):
    type_selection = CompanyDueDiligenceTypeSelection.objects.filter(company=company,is_public=False)

    selection_dict = {}
    for dd_type in type_selection:
        services = CompanyServiceSelection.objects.filter(dd_type=dd_type)
        service_dict = {}
        for service in services:
            service_dict[service] = []

        selection_dict[dd_type] = service_dict

    return selection_dict

def get_public_selections_in_dict():
    type_selection = CompanyDueDiligenceTypeSelection.get_public_packages()

    selection_dict = {}
    for dd_type in type_selection:
        services = CompanyServiceSelection.objects.filter(dd_type=dd_type)
        service_dict = {}
        for service in services:
            service_dict[service] = []

        selection_dict[dd_type] = service_dict

    return selection_dict

def get_public_packages_with_company_disabled_status(company):
    public_packages = CompanyDueDiligenceTypeSelection.get_public_packages()
    company_disabled_public_packages = list(map(lambda x:x.package,CompanyDisabledPackage.objects.filter(company=company)))
    package_dict = {}
    for package in public_packages:
        package_dict[package]=package in company_disabled_public_packages
    
    return package_dict


def request_is_valid(pk):
    try:
        int(pk)
        try:
            request = Request.objects.get(pk=pk)
            return True
        except Request.DoesNotExist:
            return False
    except ValueError:
        return False


def corporate_request_is_valid(pk):
    try:
        int(pk)
        try:
            request = CorporateRequest.objects.get(pk=pk)
            return True
        except CorporateRequest.DoesNotExist:
            return False
    except ValueError:
        return False


def custom_request_is_valid(pk):
    try:
        int(pk)
        try:
            request = CustomRequest.objects.get(pk=pk)
            return True
        except CustomRequest.DoesNotExist:
            return False
    except ValueError:
        return False


def employee_is_valid(pk):
    try:
        int(pk)
        try:
            employee = CompanyEmployee.objects.get(pk=pk)
            return True
        except CompanyEmployee.DoesNotExist:
            return False
    except ValueError:
        return False


def dynamic_request_form_is_valid(pk):
    try:
        int(pk)
        try:
            dynamic_request_form = DynamicRequestForm.objects.get(pk=pk)
            return True
        except DynamicRequestForm.DoesNotExist:
            return False
    except ValueError:
        return False


def dynamic_request_form_field_is_valid(pk):
    try:
        int(pk)
        try:
            field = DynamicRequestFormFields.objects.get(pk=pk)
            return True
        except DynamicRequestFormFields.DoesNotExist:
            return False
    except ValueError:
        return False


def are_there_custom_requests_using_dynamic_request_form(pk):
    try:
        int(pk)
        dynamic_request_form = DynamicRequestForm.objects.get(pk=pk)
        if len(CustomRequest.objects.filter(dynamic_request_form=dynamic_request_form)) > 0:
            return True
        else:
            return False
    except ValueError:
        return False


def are_there_custom_request_fields_using_dynamic_request_form_field(pk):
    try:
        int(pk)
        field= DynamicRequestFormFields.objects.get(pk=pk)
        if len(CustomRequestFields.objects.filter(form_field=field)) > 0:
            return True
        else:
            return False
    except ValueError:
        return False


def dd_type_is_valid(pk):
    try:
        int(pk)
        try:
            dd_type_selection = CompanyDueDiligenceTypeSelection.objects.get(pk=pk)
            return True
        except CompanyDueDiligenceTypeSelection.DoesNotExist:
            return False
    except ValueError:
        return False

def public_dd_type_is_valid(pk):
    try:
        int(pk)
        try:
            dd_type_selection = CompanyDueDiligenceTypeSelection.objects.get(pk=pk,is_public=True)
            return True
        except CompanyDueDiligenceTypeSelection.DoesNotExist:
            return False
    except ValueError:
        return False


def company_is_valid(pk):
    try:
        int(pk)
        try:
            company = Company.objects.get(pk=pk)
            return True
        except Company.DoesNotExist:
            return False
    except ValueError:
        return False


def employee_has_access_to_request(current_user, request_id):
    try:
        request = Request.objects.get(pk=request_id)
        if (request.created_by.user == current_user):
            return True
    except Request.DoesNotExist:
        return False
    return False


def employee_has_access_to_request_for_corporate(current_user, request_id):
    try:
        request = CorporateRequest.objects.get(pk=request_id)
        if (request.created_by.user == current_user):
            return True
    except CorporateRequest.DoesNotExist:
        return False
    return False


def employee_has_access_to_custom_request(current_user, request_id):
    try:
        request = CustomRequest.objects.get(pk=request_id)
        if (request.created_by.user == current_user):
            return True
    except CustomRequest.DoesNotExist:
        return False
    return False


def analyst_has_access_to_request(current_user, request_id):
    try:
        request = Request.objects.get(pk=request_id)
        if (request.assignment is not None and request.assignment.user == current_user):
            return True
    except Request.DoesNotExist:
        return False
    return False


def analyst_has_access_to_request_for_corporate(current_user, request_id):
    try:
        request = CorporateRequest.objects.get(pk=request_id)
        if (request.assignment is not None and request.assignment.user == current_user):
            return True
    except CorporateRequest.DoesNotExist:
        return False
    return False


def analyst_has_access_to_request_for_custom(current_user, request_id):
    try:
        request = CustomRequest.objects.get(pk=request_id)
        if (request.assignment is not None and request.assignment.user == current_user):
            return True
    except CustomRequest.DoesNotExist:
        return False
    return False


def check_for_contact_form_fields(fields, update):
    for field in fields:
        if update:
            if field.form_field.group.group_name == LayoutGroupSections.CONTACT_INFO:
                return True

        else:
            if field.group.group_name == LayoutGroupSections.CONTACT_INFO:
                return True

    return False


def generate_custom_pdf_file(company_date_id):
    cheese = company_date_id.split("_")
    index = len(cheese) - 1
    request_display_id = cheese[index]
    try:
        custom_request = CustomRequest.objects.get(display_id=request_display_id)
    except CustomRequest.DoesNotExist:
        print "Could not find CustomRequest for display_id = {}".format(request_display_id)
        return None

    try:
        fields = CustomRequestFields.objects.filter(custom_request=custom_request)
    except CustomRequestFields.DoesNotExist:
        print "Could not retrieve CustomRequestFields for CustomRequest = {}".format(custom_request.id)
        return None


    service_statuses = CustomRequestServiceStatus.objects.filter(request=custom_request).order_by(
        'service__service__display_order')

    start_date = ""
    submit_date = ""

    try:
        start_date = \
            Status.objects.filter(custom_request=custom_request, status=Status.IN_PROGRESS_STATUS).values('datetime', 'id').order_by('id').first()['datetime']
    except Status.DoesNotExist:
        print "Could not start_date for CustomRequest = {}".format(custom_request.id)

    try:
        submit_date = \
            Status.objects.filter(custom_request=custom_request).filter(status=Status.SUBMITTED_STATUS).values('datetime').first()['datetime']
    except Status.DoesNotExist:
        print "Could not submit_date for CustomRequest = {}".format(custom_request.id)

    template = get_template_type(custom_request)
    if not template:
        template = 'reports/comply_third_party_reg_bus_report.html'

    try:
        company = CompanyEmployee.objects.get(user=custom_request.created_by.user).company
    except CompanyEmployee.DoesNotExist:
        print "Could not find CompanyEmployee for CustomRequest = {}".format(custom_request.id)

    report_logo = None
    try:
        report_logo = company.report_logo
    except:
        pass

    report_logo = settings.MEDIA_URL + str(report_logo)
    report_logo_active = company.report_logo_active

    return generate_report_pdf_file(template,
                        {'logo': settings.COMPLY_LOGO_FOR_PDF, 'ashtree_logo': settings.ASHTREE_LOGO_FOR_PDF,
                         'report_logo_active': report_logo_active, 'report_logo': report_logo,
                         'watermark_ashtree': settings.WATERMARK_ASHTREE, 'line': settings.HORIZONTAL_LINE,
                         'green_line': settings.HORIZONTAL_LINE_ASHTREE,
                         'last_page': settings.LAST_PAGE, 'last_page_ashtree': settings.LAST_PAGE_ASHTREE,
                         'last_page_client': settings.LAST_PAGE_CLIENT,
                         'flag': settings.FLAG, 'yellow_flag':settings.YELLOW_FLAG,
                         'request': custom_request, "start_date": start_date, "submit_date": submit_date,
                         "service_statuses": service_statuses, "font_url": settings.FONT_DIR,
                         "bullet": settings.BULLET, "bullet_ashtree": settings.BULLET_ASHTREE, 'x': settings.X,
                         'prescient': settings.PRESCIENT, 'no_red_flag': settings.NO_RED_FLAG, 'fields': fields})


def generate_individual_pdf_file(company_date_id):
    cheese = company_date_id.split("_")
    index = len(cheese) - 1
    request_display_id = cheese[index]

    try:
        request_object = Request.objects.get(display_id=request_display_id)
    except Request.DoesNotExist:
        print "Could not find CustomRequest for display_id = {}".format(request_display_id)
        return None

    try:
        service_statuses = RequestServiceStatus.objects.filter(request=request_object).order_by(
            'service__service__display_order')
    except RequestServiceStatus.DoesNotExist:
        print "Could not find request service statuses for Request = {}".format(request_object.id)

    start_date = ""
    submit_date = ""

    try:
        start_date = \
            Status.objects.filter(request=request_object).filter(status=Status.NEW_STATUS).values(
                'datetime').first()['datetime']
        submit_date = \
            Status.objects.filter(request=request_object).filter(status=Status.SUBMITTED_STATUS).values(
                'datetime').first()['datetime']
    except Exception, e:
        print "Error generating dates."


    template = get_template_type(request_object)
    if not template:
        template = 'reports/comply_third_party_reg_bus_report.html'

    try:
        company = CompanyEmployee.objects.get(user=request_object.created_by.user).company
    except CompanyEmployee.DoesNotExist:
        print "Could not find CompanyEmployee for CustomRequest = {}".format(request_object.id)



    report_logo = None
    try:
        report_logo = company.report_logo
    except:
        pass

    report_logo = settings.MEDIA_URL + str(report_logo)
    report_logo_active = company.report_logo_active




    return generate_report_pdf_file(template,
                        {'logo': settings.COMPLY_LOGO_FOR_PDF, 'ashtree_logo': settings.ASHTREE_LOGO_FOR_PDF,
                         'report_logo_active': report_logo_active, 'report_logo': report_logo,
                         'watermark': settings.WATERMARK,
                         'watermark_ashtree': settings.WATERMARK_ASHTREE, 'line': settings.COMPLY_GREY_BAR,
                         'green_line': settings.HORIZONTAL_LINE_ASHTREE,
                         'last_page': settings.LAST_PAGE, 'last_page_ashtree': settings.LAST_PAGE_ASHTREE,
                         'last_page_client': settings.LAST_PAGE_CLIENT,
                         'flag': settings.FLAG, 'yellow_flag':settings.YELLOW_FLAG,
                         'request': request_object, "start_date": start_date, "submit_date": submit_date,
                         "service_statuses": service_statuses, "font_url": settings.FONT_DIR,
                         "bullet": settings.BULLET, "bullet_ashtree": settings.BULLET_ASHTREE, 'x': settings.X,
                         'prescient': settings.PRESCIENT, 'no_red_flag': settings.NO_RED_FLAG})


def generate_corporate_pdf_file(company_date_id):
    split = company_date_id.split("_")
    index = len(split) - 1
    request_display_id = split[index]
    try:
        request_object = CorporateRequest.objects.get(display_id=request_display_id)
    except CorporateRequest.DoesNotExist:
        print "Could not find CorporateRequest with display_id = {}".format(request_display_id)
        return None

    service_statuses = CorporateRequestServiceStatus.objects.filter(request=request_object).order_by(
        'service__service__display_order')

    start_date = "Unknown"
    submit_date = "Unknown"

    try:
        start_date = Status.objects.filter(corporate_request=request_object).filter(
            status=Status.NEW_STATUS).values('datetime').first()['datetime']
        submit_date = Status.objects.filter(corporate_request=request_object).filter(
            status=Status.SUBMITTED_STATUS).values('datetime').first()['datetime']
    except Exception, e:
        print "Error generating dates."

    template = 'reports/third-party-reg-business_report.html'
    template = get_template_type(request_object)
    company = CompanyEmployee.objects.get(user=request_object.created_by.user).company

    report_logo = None
    try:
        report_logo = company.report_logo
    except:
        pass

    report_logo = settings.MEDIA_URL + str(report_logo)
    report_logo_active = company.report_logo_active


    return generate_report_pdf_file(template,
                        {'logo': settings.COMPLY_LOGO_FOR_PDF, 'ashtree_logo': settings.ASHTREE_LOGO_FOR_PDF,
                         'report_logo_active': report_logo_active, 'report_logo': report_logo,
                         'watermark': settings.WATERMARK,
                         'watermark_ashtree': settings.WATERMARK_ASHTREE, 'line': settings.HORIZONTAL_LINE,
                         'green_line': settings.HORIZONTAL_LINE_ASHTREE,
                         'last_page': settings.LAST_PAGE, 'last_page_ashtree': settings.LAST_PAGE_ASHTREE,
                         'last_page_client': settings.LAST_PAGE_CLIENT,
                         'flag': settings.FLAG, 'yellow_flag':settings.YELLOW_FLAG,
                         'request': request_object, "start_date": start_date, "submit_date": submit_date,
                         "service_statuses": service_statuses, "font_url": settings.FONT_DIR,
                         "bullet": settings.BULLET, "bullet_ashtree": settings.BULLET_ASHTREE, 'x': settings.X,
                         'prescient': settings.PRESCIENT, 'no_red_flag': settings.NO_RED_FLAG})



def fix_end(end):
    if len(end) < 2:
        end = datetime.datetime.now() + datetime.timedelta(days=1)
    else:
        end = datetime.datetime.strptime(str(end), '%Y-%m-%d') + datetime.timedelta(days=1)
    return end


def fix_start(start):
    if len(start) < 2:
        start = '2014-06-01'
    else:
        end = datetime.datetime.strptime(str(start), '%Y-%m-%d') - datetime.timedelta(days=1)
    return start


def sort_statuses(statuses,sort_direction):
    reordered_statuses_preference = [
        Status.NEW_STATUS,
        Status.AWAITING_DATA_FORM_APPROVAL,
        Status.ASSIGNED_STATUS,
        Status.IN_PROGRESS_STATUS,
        Status.REVIEW_STATUS,
        Status.NEW_RETURNED_STATUS,
        Status.COMPLETED_STATUS,
        Status.SUBMITTED_STATUS,
        Status.REJECTED_STATUS,
        Status.INCOMPLETE_STATUS,
        Status.DELETED_STATUS
    ]

    if sort_direction == "desc":
        reordered_statuses_preference = reordered_statuses_preference[::-1]
    # statuses= [status for status in statuses for reordered in reordered_statuses_preference if status.status == reordered]
    reordered_statuses_ids = []
    for reordered in reordered_statuses_preference:
        for status in statuses:
            if status.status == reordered:
                reordered_statuses_ids.append(status.id)
    preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(reordered_statuses_ids)])
    statuses = Status.objects.filter(id__in=reordered_statuses_ids).order_by(preserved)
    return statuses
    