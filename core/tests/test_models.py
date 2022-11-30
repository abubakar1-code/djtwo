from django.test import TestCase
from django.core.urlresolvers import reverse
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User, Group
from django.template.defaultfilters import slugify


import datetime

from core.models import Company, CompanyDueDiligenceTypeSelection, CompanyEmployee, CorporateRequest, CustomRequest,\
    CustomRequestFields, DueDiligenceType, DynamicRequestForm, DynamicRequestFormFields, LayoutGroupSections, Request,\
    RequestFormFieldTypes, Status, SpotLitStaff


class ModelsTest(TestCase):

    ###########################
    #
    # Helpers
    #
    ###########################

    def create_company_due_diligence_selection(self, company, dd_type):
        selection = CompanyDueDiligenceTypeSelection(company=company, due_diligence_type=dd_type)
        selection.save()
        return selection

    def create_due_diligence_type(self, dd_type):
        dd_type = DueDiligenceType(name=dd_type)
        dd_type.save()
        return dd_type

    def create_request(self, company_employee):
        first_name = "Bob"
        middle_name = "Robert"
        last_name = "Smith"
        ssn = "567893456"
        birthdate = "1983-05-06"
        phone_number = "1234566789"
        email = "bob@smith.com"

        request_type = DueDiligenceType(name="Human Resources")
        request_type.save()
        request_type_selection = CompanyDueDiligenceTypeSelection(company=company_employee.company,
                                                                  due_diligence_type=request_type,
                                                                  name="test", comments="", level=1)
        request_type_selection.save()

        created_by = company_employee

        request = Request(first_name=first_name, middle_name=middle_name,
                          last_name=last_name, ssn=ssn, birthdate=birthdate, phone_number=phone_number,
                          email=email, request_type=request_type_selection, created_by=created_by)
        request.save()
        return request

    def create_corporate_request(self, company_employee):
        company_name = "Acme"
        duns_number = '123456789'
        comp_reg_num = '123456'

        request_type = DueDiligenceType(name="Human Resources")
        request_type.save()
        request_type_selection = CompanyDueDiligenceTypeSelection(company=company_employee.company,
                                                                  due_diligence_type=request_type,
                                                                  name="test", comments="", level=1)
        request_type_selection.save()
        created_by = company_employee
        corporate_request = CorporateRequest(company_name=company_name,
                                             request_type=request_type_selection,
                                             duns=duns_number,
                                             registration=comp_reg_num,
                                             created_by=created_by)
        corporate_request.save()

        return corporate_request

    def create_custom_request(self, employee):
        dynamic_request_form = DynamicRequestForm(
            company=employee.company,
            name='custom form',
        )
        dynamic_request_form.save()

        field_type = RequestFormFieldTypes(type=RequestFormFieldTypes.TEXT)
        field_type.save()

        group_section = LayoutGroupSections(group_name=LayoutGroupSections.REQUEST_INFO)
        group_section.save()

        form_field = DynamicRequestFormFields(
            dynamic_request_form=dynamic_request_form,
            type=field_type,
            label='name',
            group=group_section,
        )
        form_field.save()

        request_type = self.create_due_diligence_type("HR")
        selection = self.create_company_due_diligence_selection(employee.company, request_type)

        custom_request = CustomRequest(
            dynamic_request_form=dynamic_request_form,
            name='custom request',
            created_by=employee,
            request_type=selection,
        )
        custom_request.save()

        custom_request_field = CustomRequestFields(custom_request=custom_request, form_field=form_field, value='Mark')
        custom_request_field.save()

        return custom_request

    def create_dynamic_request_form(self, employee):
        dynamic_request_form = DynamicRequestForm(
            company=employee.company,
            name='custom form',
        )
        dynamic_request_form.save()

        field_type = RequestFormFieldTypes(type=RequestFormFieldTypes.TEXT)
        field_type.save()

        group_section = LayoutGroupSections(group_name=LayoutGroupSections.REQUEST_INFO)
        group_section.save()

        form_field = DynamicRequestFormFields(
            dynamic_request_form=dynamic_request_form,
            type=field_type,
            label='name',
            group=group_section,
        )
        form_field.save()



        return dynamic_request_form

    def create_custom_request_for_dynamic_form(self, dynamic_request_form, employee, name):
        request_type = self.create_due_diligence_type("Human Resources")
        selection = self.create_company_due_diligence_selection(employee.company, request_type)
        custom_request = CustomRequest(
            dynamic_request_form=dynamic_request_form,
            name=name,
            created_by=employee,
            request_type=selection,
        )
        custom_request.save()
        return custom_request

    def create_company_employee(self, user):
        company = Company(name='company')
        company.save()
        employee = CompanyEmployee(user=user, phone_number='123445667', company=company, position='HR Rep')
        employee.save()
        return employee

    def create_company_employee_for_company(self, user, company):
        company = Company(name=company)
        company.save()
        employee = CompanyEmployee(user=user, phone_number='123445667', company=company, position='HR Rep')
        employee.save()
        return employee

    def create_spotlit_staff(self, user):
        staff = SpotLitStaff(user=user, phone_number="1234567890")
        staff.save()
        return staff

    def create_request_status(self, request, status, datetime):
        request_status = Status(content_object=request, status=status, datetime=datetime, comments='')
        request_status.save()
        return request_status

    def create_group(self, group_name):
        group = Group(name=group_name)
        group.save()
        return group

    def create_user(self, name, email, password):
        user = User.objects.create_user(name, email, password)
        user.save()
        return user


    ###########################
    #
    #   Status Tests
    #
    ###########################

    def test_get_all_current_ids_queryset_for_company(self):
        user_e = self.create_user("employee", "employee@company.com", "employee")
        group_e = self.create_group("CompanyEmployee")
        user_e.groups.add(group_e)

        employee = self.create_company_employee(user_e)
        company = employee.company

        # Null Check
        request_statuses = Status.get_all_current_ids_queryset_for_company(company)
        self.assertEquals(len(request_statuses), 0)

        # add a couple requests for same employee
        ind_request = self.create_request(employee)
        ind_request_status = self.create_request_status(ind_request, 1, "2015-04-29 12:00:00")
        ind_request_status_id = ind_request_status.id

        corp_request = self.create_corporate_request(employee)
        corp_request_status = self.create_request_status(corp_request, 1, "2015-04-29 12:00:00")
        corp_request_status_id = corp_request_status.id

        request_statuses = Status.get_all_current_ids_queryset_for_company(company)

        # check to make sure the length is correct, and both ids are in queryset
        self.assertEquals(len(request_statuses), 2)
        self.assertEquals(ind_request_status_id in request_statuses, True)
        self.assertEquals(corp_request_status_id in request_statuses, True)

        # now lets add some more for dif user, but same company
        user_2 = self.create_user("employee2", "employee2@company.com", "employee2")
        user_2.groups.add(group_e)
        employee2 = self.create_company_employee(user_2)

        # create some requests for the new user
        ind_request2 = self.create_request(employee2)
        ind_request2.save()
        ind_request2_status = self.create_request_status(ind_request2, 1, "2015-04-29 12:00:00")
        ind_request2_status_id = ind_request2_status.id

        # create come requests for the new user
        corp_request2 = self.create_corporate_request(employee2)
        corp_request2.save()
        corp_request2_status = self.create_request_status(corp_request2, 1, "2015-04-29 12:00:00")
        corp_request2_status_id = corp_request2_status.id
        self.assertEquals(len(Status.get_all_current_ids_queryset_for_company(company)), 4)

        # create a new user with a diff company
        user3 = self.create_user("employee3", "employee3@company.com", "employee3")
        employee3 = self.create_company_employee_for_company(user3, 'company2')
        company2 = employee3.company

        # create some requests for the new user
        ind_request3 = self.create_request(employee3)
        ind_request3.save()
        ind_request3_status = self.create_request_status(ind_request3, 1, "2015-04-29 12:00:00")
        ind_request3_status_id = ind_request3_status.id

        # create come requests for the new user
        corp_request3 = self.create_corporate_request(employee3)
        corp_request3.save()
        corp_request3_status = self.create_request_status(corp_request3, 1, "2015-04-29 12:00:00")
        corp_request3_status_id = corp_request3_status.id

        request_statuses = Status.get_all_current_ids_queryset_for_company(company)

        # tests for company 1
        statuses = Status.get_all_current_ids_queryset_for_company(company)
        self.assertEquals(ind_request_status_id in request_statuses, True)
        self.assertEquals(corp_request_status_id in request_statuses, True)
        self.assertEquals(ind_request2_status_id in request_statuses, True)
        self.assertEquals(corp_request2_status_id in request_statuses, True)

        request_statuses = Status.get_all_current_ids_queryset_for_company(company2)
        # tests for company 2
        self.assertEquals(len(request_statuses), 2)
        self.assertEquals(ind_request3_status_id in request_statuses, True)
        self.assertEquals(corp_request3_status_id in request_statuses, True)

        # should only return the most recent status
        corp_request3_status2 = self.create_request_status(corp_request3, 2, "2015-04-29 12:01:00")
        corp_request3_status2_id = corp_request3_status2.id
        request_statuses = Status.get_all_current_ids_queryset_for_company(company2)
        self.assertEquals(corp_request3_status2_id in request_statuses, True)
        self.assertEquals(corp_request3_status in request_statuses, False)

    def test_get_all_request_by_statuses_for_company(self):
        user_e = self.create_user("employee", "employee@company.com", "employee")
        group_e = self.create_group("CompanyEmployee")
        user_e.groups.add(group_e)

        employee = self.create_company_employee(user_e)
        company = employee.company

        # Null Check
        request_statuses = Status.get_all_request_by_statuses_for_company(Status.NEW_STATUS, company)
        self.assertEquals(len(request_statuses), 0)

        # add a couple requests for same employee with different statuses
        ind_request = self.create_request(employee)
        ind_request_status = self.create_request_status(ind_request, 1, "2015-04-29 12:00:00")

        corp_request = self.create_corporate_request(employee)
        corp_request_status = self.create_request_status(corp_request, 2, "2015-04-29 12:00:00")


        # testing new status
        request_statuses_new = Status.get_all_request_by_statuses_for_company([Status.NEW_STATUS], company)
        self.assertEquals(len(request_statuses_new), 1)
        self.assertEquals(ind_request_status in request_statuses_new, True)


        # testing assigned
        request_statuses_assigned = Status.get_all_request_by_statuses_for_company([Status.ASSIGNED_STATUS], company)
        self.assertEquals(len(request_statuses_assigned), 1)
        self.assertEquals(corp_request_status in request_statuses_assigned, True)

        # testing both
        request_statuses_new_assigned = Status.get_all_request_by_statuses_for_company([Status.NEW_STATUS, Status.ASSIGNED_STATUS], company)
        self.assertEquals(len(request_statuses_new_assigned), 2)
        self.assertEquals(corp_request_status in request_statuses_new_assigned, True)
        self.assertEquals(ind_request_status in request_statuses_new_assigned, True)

    def test_get_all_current_ids_queryset_for_user(self):
        user_e = self.create_user("employee", "employee@company.com", "employee")
        group_e = self.create_group("CompanyEmployee")
        user_e.groups.add(group_e)

        employee = self.create_company_employee(user_e)
        company = employee.company

        # Null Check
        request_statuses = Status.get_all_current_ids_queryset_for_user(user_e)
        self.assertEquals(len(request_statuses), 0)

        # add a couple requests for same employee with different statuses
        ind_request = self.create_request(employee)
        ind_request_status = self.create_request_status(ind_request, 1, "2015-04-29 12:00:00")

        corp_request = self.create_corporate_request(employee)
        corp_request_status = self.create_request_status(corp_request, 2, "2015-04-29 12:00:00")

        request_status_ids = Status.get_all_current_ids_queryset_for_user(user_e)

        # make sure we get back the right statuses
        self.assertEquals(len(request_status_ids), 2)
        self.assertEquals(corp_request_status.id in request_status_ids, True)
        self.assertEquals(ind_request_status.id in request_status_ids, True)

        # not lets add another status for the same request, we should get back the newest....
        corp_request_status2 = self.create_request_status(corp_request, 1, "2015-04-29 12:00:01")
        request_status_ids = Status.get_all_current_ids_queryset_for_user(user_e)
        self.assertEquals(len(request_status_ids), 2)
        self.assertEquals(corp_request_status.id in request_status_ids, False)
        self.assertEquals(corp_request_status2.id in request_status_ids, True)
        self.assertEquals(ind_request_status.id in request_status_ids, True)

    def test_get_all_current_ids_queryset(self):
        user_e = self.create_user("employee", "employee@company.com", "employee")
        group_e = self.create_group("CompanyEmployee")
        user_e.groups.add(group_e)

        employee = self.create_company_employee(user_e)
        company = employee.company

        # Null Check
        request_statuses = Status.get_all_current_ids_queryset()
        self.assertEquals(len(request_statuses), 0)


        # add a couple requests for same employee with different statuses
        ind_request = self.create_request(employee)
        ind_request_status = self.create_request_status(ind_request, 1, "2015-04-29 12:00:00")

        corp_request = self.create_corporate_request(employee)
        corp_request_status = self.create_request_status(corp_request, 2, "2015-04-29 12:00:00")

        request_status_ids = Status.get_all_current_ids_queryset()

        self.assertEquals(len(request_status_ids), 2)
        self.assertEquals(ind_request_status.id in request_status_ids, True)
        self.assertEquals(corp_request_status.id in request_status_ids, True)

    def test_get_request_status_for_group(self):

        SPOTLIT_MANAGER_GROUP = "SpotLitManager"
        SPOTLIT_ANALYST_GROUP = "SpotLitAnalyst"
        COMPANY_EMPLOYEE_GROUP = "CompanyEmployee"

        group_e = self.create_group("CompanyEmployee")
        group_m = self.create_group("SpotLitManager")
        group_a = self.create_group("SpotLitAnalyst")

        employee_new = Status.get_request_status_for_group(group_e, Status.NEW_STATUS)
        self.assertEquals(employee_new, 'In Progress')

        employee_assigned = Status.get_request_status_for_group(group_e, Status.ASSIGNED_STATUS)
        self.assertEquals(employee_assigned, 'In Progress')

        employee_in_progress = Status.get_request_status_for_group(group_e, Status.IN_PROGRESS_STATUS)
        self.assertEquals(employee_in_progress, 'In Progress')

        employee_completed = Status.get_request_status_for_group(group_e, Status.COMPLETED_STATUS)
        self.assertEquals(employee_completed, 'In Progress')

        employee_submitted = Status.get_request_status_for_group(group_e, Status.SUBMITTED_STATUS)
        self.assertEquals(employee_submitted, 'Completed')

        employee_rejected = Status.get_request_status_for_group(group_e, Status.REJECTED_STATUS)
        self.assertEquals(employee_rejected, 'In Progress')

        employee_incomplete = Status.get_request_status_for_group(group_e, Status.INCOMPLETE_STATUS)
        self.assertEquals(employee_incomplete, 'Incomplete')

        employee_new_returned = Status.get_request_status_for_group(group_e, Status.NEW_RETURNED_STATUS)
        self.assertEquals(employee_new_returned, 'In Progress')

        employee_deleted = Status.get_request_status_for_group(group_e, Status.DELETED_STATUS)
        self.assertEquals(employee_deleted, 'Deleted')




        analyst_assigned = Status.get_request_status_for_group(group_a, Status.ASSIGNED_STATUS)
        self.assertEquals(analyst_assigned, 'New')

        analyst_in_progress = Status.get_request_status_for_group(group_a, Status.IN_PROGRESS_STATUS)
        self.assertEquals(analyst_in_progress, 'In Progress')

        analyst_completed = Status.get_request_status_for_group(group_a, Status.COMPLETED_STATUS)
        self.assertEquals(analyst_completed, 'Completed')

        analyst_submitted = Status.get_request_status_for_group(group_a, Status.SUBMITTED_STATUS)
        self.assertEquals(analyst_submitted, 'Submitted')

        analyst_rejected = Status.get_request_status_for_group(group_a, Status.REJECTED_STATUS)
        self.assertEquals(analyst_rejected, 'Rejected')

        analyst_incomplete = Status.get_request_status_for_group(group_a, Status.INCOMPLETE_STATUS)
        self.assertEquals(analyst_incomplete, 'Incomplete')

        analyst_new_returned = Status.get_request_status_for_group(group_a, Status.NEW_RETURNED_STATUS)
        self.assertEquals(analyst_new_returned, 'New Returned')

        analyst_deleted = Status.get_request_status_for_group(group_a, Status.DELETED_STATUS)
        self.assertEquals(analyst_deleted, 'Deleted')




        manager_new = Status.get_request_status_for_group(group_m, Status.NEW_STATUS)
        self.assertEquals(manager_new, 'New')

        manager_assigned = Status.get_request_status_for_group(group_m, Status.ASSIGNED_STATUS)
        self.assertEquals(manager_assigned, 'Assigned')

        manager_in_progress = Status.get_request_status_for_group(group_m, Status.IN_PROGRESS_STATUS)
        self.assertEquals(manager_in_progress, 'In Progress')

        manager_completed = Status.get_request_status_for_group(group_m, Status.COMPLETED_STATUS)
        self.assertEquals(manager_completed, 'Completed')

        manager_submitted = Status.get_request_status_for_group(group_m, Status.SUBMITTED_STATUS)
        self.assertEquals(manager_submitted, 'Submitted')

        manager_rejected = Status.get_request_status_for_group(group_m, Status.REJECTED_STATUS)
        self.assertEquals(manager_rejected, 'Rejected')

        manager_incomplete = Status.get_request_status_for_group(group_m, Status.INCOMPLETE_STATUS)
        self.assertEquals(manager_incomplete, 'Incomplete')

        manager_new_returned = Status.get_request_status_for_group(group_m, Status.NEW_RETURNED_STATUS)
        self.assertEquals(manager_new_returned, 'New Returned')

        manager_deleted = Status.get_request_status_for_group(group_m, Status.DELETED_STATUS)
        self.assertEquals(manager_deleted, 'Deleted')

    def test_get_all_requests_by_status(self):
        user_e = self.create_user("employee", "employee@company.com", "employee")
        group_e = self.create_group("CompanyEmployee")
        user_e.groups.add(group_e)

        employee = self.create_company_employee(user_e)
        company = employee.company

        # Null Check
        request_statuses = Status.get_all_requests_by_status(Status.NEW_STATUS)
        self.assertEquals(len(request_statuses), 0)

        # add a mix of requests with all the different statuses
        ind_request_1 = self.create_request(employee)
        new_status = self.create_request_status(ind_request_1, Status.NEW_STATUS, "2015-04-29 12:00:00")
        statuses = Status.get_all_requests_by_status(Status.NEW_STATUS)
        self.assertEquals(len(statuses), 1)
        self.assertEquals(new_status in statuses, True)

        corp_request_2 = self.create_corporate_request(employee)
        assigned_status = self.create_request_status(corp_request_2, Status.ASSIGNED_STATUS, "2015-04-29 12:00:00")
        statuses = Status.get_all_requests_by_status(Status.ASSIGNED_STATUS)
        self.assertEquals(len(statuses), 1)
        self.assertEquals(assigned_status in statuses, True)

        ind_request_3 = self.create_request(employee)
        in_progress_status = self.create_request_status(ind_request_3, Status.IN_PROGRESS_STATUS, "2015-04-29 12:00:00")
        statuses = Status.get_all_requests_by_status(Status.IN_PROGRESS_STATUS)
        self.assertEquals(len(statuses), 1)
        self.assertEquals(in_progress_status in statuses, True)

        corp_request_4 = self.create_corporate_request(employee)
        completed_status = self.create_request_status(corp_request_4, Status.COMPLETED_STATUS, "2015-04-29 12:00:00")
        statuses = Status.get_all_requests_by_status(Status.COMPLETED_STATUS)
        self.assertEquals(len(statuses), 1)
        self.assertEquals(completed_status in statuses, True)

        ind_request_5 = self.create_request(employee)
        submitted_status = self.create_request_status(ind_request_5, Status.SUBMITTED_STATUS, "2015-04-29 12:00:00")
        statuses = Status.get_all_requests_by_status(Status.SUBMITTED_STATUS)
        self.assertEquals(len(statuses), 1)
        self.assertEquals(submitted_status in statuses, True)

        corp_request_6 = self.create_corporate_request(employee)
        rejected_status = self.create_request_status(corp_request_6, Status.REJECTED_STATUS, "2015-04-29 12:00:00")
        statuses = Status.get_all_requests_by_status(Status.REJECTED_STATUS)
        self.assertEquals(len(statuses), 1)
        self.assertEquals(rejected_status in statuses, True)

        ind_request_7 = self.create_request(employee)
        incomplete_status = self.create_request_status(ind_request_7, Status.INCOMPLETE_STATUS, "2015-04-29 12:00:00")
        statuses = Status.get_all_requests_by_status(Status.INCOMPLETE_STATUS)
        self.assertEquals(len(statuses), 1)
        self.assertEquals(incomplete_status in statuses, True)

        corp_request_8 = self.create_corporate_request(employee)
        new_returned_status = self.create_request_status(corp_request_8, Status.NEW_RETURNED_STATUS, "2015-04-29 12:00:00")
        statuses = Status.get_all_requests_by_status(Status.NEW_RETURNED_STATUS)
        self.assertEquals(len(statuses), 1)
        self.assertEquals(new_returned_status in statuses, True)

        ind_request_9 = self.create_request(employee)
        deleted_request_status = self.create_request_status(ind_request_9, Status.DELETED_STATUS, "2015-04-29 12:00:00")
        statuses = Status.get_all_requests_by_status(Status.DELETED_STATUS)
        self.assertEquals(len(statuses), 1)
        self.assertEquals(deleted_request_status in statuses, True)

    def test_get_num_completed_requests_x_days_for_manager(self):
        user_e = self.create_user("employee", "employee@company.com", "employee")
        group_e = self.create_group("CompanyEmployee")
        user_e.groups.add(group_e)

        employee = self.create_company_employee(user_e)
        company = employee.company

        # Null Check
        num_completed = Status.get_num_completed_requests_x_days_for_manager(10)
        self.assertEquals(num_completed, 0)

        # add a couple requests for same employee with different statuses and different dates..
        ind_request = self.create_request(employee)
        seven_days_ago = datetime.datetime.now() - datetime.timedelta(days=7)
        ind_request_status = self.create_request_status(ind_request, Status.COMPLETED_STATUS, seven_days_ago)
        num_completed = Status.get_num_completed_requests_x_days_for_manager(8)
        self.assertEquals(num_completed, 1)


        corp_request = self.create_corporate_request(employee)
        five_days_ago = datetime.datetime.now() - datetime.timedelta(days=5)
        corp_request_status = self.create_request_status(corp_request, Status.COMPLETED_STATUS, five_days_ago)
        num_completed = Status.get_num_completed_requests_x_days_for_manager(8)
        self.assertEquals(num_completed, 2)
        num_completed = Status.get_num_completed_requests_x_days_for_manager(6)
        self.assertEquals(num_completed, 1)


        ind_request2 = self.create_request(employee)
        three_days_ago = datetime.datetime.now() - datetime.timedelta(days=3)
        request = self.create_request_status(ind_request2, Status.COMPLETED_STATUS, three_days_ago)

        num_completed = Status.get_num_completed_requests_x_days_for_manager(4)
        self.assertEquals(num_completed, 1)
        num_completed = Status.get_num_completed_requests_x_days_for_manager(6)
        self.assertEquals(num_completed, 2)
        num_completed = Status.get_num_completed_requests_x_days_for_manager(8)
        self.assertEquals(num_completed, 3)

    def test_get_num_rejected_requests_x_days_for_manager(self):
        user_e = self.create_user("employee", "employee@company.com", "employee")
        group_e = self.create_group("CompanyEmployee")
        user_e.groups.add(group_e)

        employee = self.create_company_employee(user_e)
        company = employee.company

        # Null Check
        num_completed = Status.get_num_rejected_requests_x_days_for_manager(10)
        self.assertEquals(num_completed, 0)

        # add a couple requests for same employee with different statuses and different dates..
        ind_request = self.create_request(employee)
        seven_days_ago = datetime.datetime.now() - datetime.timedelta(days=7)
        ind_request_status = self.create_request_status(ind_request, Status.REJECTED_STATUS, seven_days_ago)
        num_completed = Status.get_num_rejected_requests_x_days_for_manager(8)
        self.assertEquals(num_completed, 1)


        corp_request = self.create_corporate_request(employee)
        five_days_ago = datetime.datetime.now() - datetime.timedelta(days=5)
        corp_request_status = self.create_request_status(corp_request, Status.REJECTED_STATUS, five_days_ago)
        num_completed = Status.get_num_rejected_requests_x_days_for_manager(8)
        self.assertEquals(num_completed, 2)
        num_completed = Status.get_num_rejected_requests_x_days_for_manager(6)
        self.assertEquals(num_completed, 1)


        ind_request2 = self.create_request(employee)
        three_days_ago = datetime.datetime.now() - datetime.timedelta(days=3)
        request = self.create_request_status(ind_request2, Status.REJECTED_STATUS, three_days_ago)

        num_completed = Status.get_num_rejected_requests_x_days_for_manager(4)
        self.assertEquals(num_completed, 1)
        num_completed = Status.get_num_rejected_requests_x_days_for_manager(6)
        self.assertEquals(num_completed, 2)
        num_completed = Status.get_num_rejected_requests_x_days_for_manager(8)
        self.assertEquals(num_completed, 3)

    def test_get_num_new_requests_x_days_for_manager(self):
        user_e = self.create_user("employee", "employee@company.com", "employee")
        group_e = self.create_group("CompanyEmployee")
        user_e.groups.add(group_e)

        employee = self.create_company_employee(user_e)
        company = employee.company

        # Null Check
        num_completed = Status.get_num_rejected_requests_x_days_for_manager(10)
        self.assertEquals(num_completed, 0)

        # add a couple requests for same employee with different statuses and different dates..
        ind_request = self.create_request(employee)
        seven_days_ago = datetime.datetime.now() - datetime.timedelta(days=7)
        ind_request_status = self.create_request_status(ind_request, Status.NEW_STATUS, seven_days_ago)
        num_completed = Status.get_num_new_requests_x_days_for_manager(8)
        self.assertEquals(num_completed, 1)


        corp_request = self.create_corporate_request(employee)
        five_days_ago = datetime.datetime.now() - datetime.timedelta(days=5)
        corp_request_status = self.create_request_status(corp_request, Status.NEW_STATUS, five_days_ago)
        num_completed = Status.get_num_new_requests_x_days_for_manager(8)
        self.assertEquals(num_completed, 2)
        num_completed = Status.get_num_new_requests_x_days_for_manager(6)
        self.assertEquals(num_completed, 1)


        ind_request2 = self.create_request(employee)
        three_days_ago = datetime.datetime.now() - datetime.timedelta(days=3)
        request = self.create_request_status(ind_request2, Status.NEW_STATUS, three_days_ago)

        num_completed = Status.get_num_new_requests_x_days_for_manager(4)
        self.assertEquals(num_completed, 1)
        num_completed = Status.get_num_new_requests_x_days_for_manager(6)
        self.assertEquals(num_completed, 2)
        num_completed = Status.get_num_new_requests_x_days_for_manager(8)
        self.assertEquals(num_completed, 3)

    def test_get_all_current_ids_queryset_for_analyst(self):
        # create an employee to create some requests
        user_e = self.create_user("employee", "employee@company.com", "employee")
        group_e = self.create_group("CompanyEmployee")
        user_e.groups.add(group_e)
        employee = self.create_company_employee(user_e)
        company = employee.company

        # create an analyst to assign those requests to..
        analyst = self.create_user("analyst", "analyst@analyst.com", "analyst")
        group_a = self.create_group("SpotLitAnalyst")
        analyst.groups.add(group_a)
        spotlit_staff = self.create_spotlit_staff(analyst)

        # create some requests and assign to analyst
        ind_request_1 = self.create_request(employee)
        ind_request_1.assignment = spotlit_staff
        ind_request_1.save()
        ind_request_status = self.create_request_status(ind_request_1, Status.ASSIGNED_STATUS, "2015-04-29 12:00:00")


        corp_request_2 = self.create_corporate_request(employee)
        corp_request_2.assignment = spotlit_staff
        corp_request_2.save()
        corp_request_status = self.create_request_status(corp_request_2, Status.ASSIGNED_STATUS, "2015-04-29 12:00:00")

        # create another request and don't assign it to anyone
        ind_request_na = self.create_request(employee)
        ind_request_status_na = self.create_request_status(ind_request_na, Status.ASSIGNED_STATUS, "2015-04-29 12:00:00")


        ids = Status.get_all_current_ids_queryset_for_analyst(analyst)
        self.assertEquals(len(ids), 2)
        self.assertEquals(corp_request_status.id in ids, True)
        self.assertEquals(ind_request_status.id in ids, True)

    def test_get_all_requests_by_statuses_for_analyst(self):
        # create an employee to create some requests
        user_e = self.create_user("employee", "employee@company.com", "employee")
        group_e = self.create_group("CompanyEmployee")
        user_e.groups.add(group_e)
        employee = self.create_company_employee(user_e)
        company = employee.company

        # create an analyst to assign those requests to..
        analyst = self.create_user("analyst", "analyst@analyst.com", "analyst")
        group_a = self.create_group("SpotLitAnalyst")
        analyst.groups.add(group_a)
        spotlit_staff = self.create_spotlit_staff(analyst)

        # null check
        new_statuses = Status.get_all_requests_by_statuses_for_analyst([Status.NEW_STATUS], analyst)
        self.assertEquals(len(new_statuses), 0)

        # create some requests and assign to analyst
        ind_request_new = self.create_request(employee)
        ind_request_new.assignment = spotlit_staff
        ind_request_new.save()
        ind_request_new_status = self.create_request_status(ind_request_new, Status.NEW_STATUS, "2015-04-29 12:00:00")


        corp_request_assigned = self.create_corporate_request(employee)
        corp_request_assigned.assignment = spotlit_staff
        corp_request_assigned.save()
        corp_request_assigned_status = self.create_request_status(corp_request_assigned, Status.ASSIGNED_STATUS, "2015-04-29 12:00:00")

        ind_request_in_progress = self.create_request(employee)
        ind_request_in_progress.assignment = spotlit_staff
        ind_request_in_progress.save()
        ind_request_in_progress_status = self.create_request_status(ind_request_in_progress, Status.IN_PROGRESS_STATUS, "2015-04-29 12:00:00")


        new_statuses = Status.get_all_requests_by_statuses_for_analyst([Status.NEW_STATUS],analyst)
        self.assertEquals(len(new_statuses), 1)

        assigned_statuses = Status.get_all_requests_by_statuses_for_analyst([Status.ASSIGNED_STATUS], analyst)
        self.assertEquals(len(assigned_statuses), 1)

        in_progress_statuses = Status.get_all_requests_by_statuses_for_analyst([Status.IN_PROGRESS_STATUS], analyst)
        self.assertEquals(len(in_progress_statuses), 1)

        all_statuses = Status.get_all_requests_by_statuses_for_analyst([Status.NEW_STATUS,
                                                                        Status.ASSIGNED_STATUS,
                                                                        Status.IN_PROGRESS_STATUS], analyst)
        self.assertEquals(len(all_statuses), 3)

    def test_add_request_status(self):
        # create an employee to create some requests
        user_e = self.create_user("employee", "employee@company.com", "employee")
        group_e = self.create_group("CompanyEmployee")
        user_e.groups.add(group_e)
        employee = self.create_company_employee(user_e)
        company = employee.company

        # create a request
        ind_request = self.create_request(employee)
        ind_request_status = Status.add_request_status(ind_request, Status.NEW_STATUS, 'No Comment!')
        self.assertEquals(ind_request_status is not None, True)

    ###########################
    #
    #   Request Tests
    #
    ###########################

    def test_get_report_url(self):
        # create an employee to create some requests
        user_e = self.create_user("employee", "employee@company.com", "employee")
        group_e = self.create_group("CompanyEmployee")
        user_e.groups.add(group_e)
        employee = self.create_company_employee(user_e)
        company = employee.company

        # create a request
        ind_request = self.create_request(employee)
        ind_request_status = Status.add_request_status(ind_request, Status.NEW_STATUS, 'No Comment!')
        self.assertEquals(ind_request_status is not None, True)


        # now we are going to create a slugged url
        date = datetime.datetime.now().strftime("%Y-%m-%d")
        test_url = "%s_%s_%s" % (slugify(company.name), date, ind_request.display_id)

        self.assertEquals(test_url, ind_request.get_report_url())

    def test_get_request_status(self):
        user_e = self.create_user("employee", "employee@company.com", "employee")
        group_e = self.create_group("CompanyEmployee")
        user_e.groups.add(group_e)

        employee = self.create_company_employee(user_e)
        company = employee.company

        # add a couple requests for same employee with different statuses
        ind_request = self.create_request(employee)

        # Null Check
        self.assertEquals(None, ind_request.get_request_status())

        ind_request_status_new = self.create_request_status(ind_request, 1, "2015-04-29 12:00:00")
        ind_request_status_assigned = self.create_request_status(ind_request, 2, "2015-04-29 12:01:00")
        request_status = ind_request.get_request_status()
        self.assertEquals(ind_request_status_assigned.status, request_status)

    def test_get_in_progress_request_status(self):
        user_e = self.create_user("employee", "employee@company.com", "employee")
        group_e = self.create_group("CompanyEmployee")
        user_e.groups.add(group_e)

        employee = self.create_company_employee(user_e)
        company = employee.company

        # create a request to check statuses for
        ind_request = self.create_request(employee)

        # Null Check
        self.assertEquals(None, ind_request.get_in_progress_request_status())
        ind_request_status_new = self.create_request_status(ind_request, Status.NEW_STATUS, "2015-04-29 12:00:00")
        ind_request_status_in_prog = self.create_request_status(
            ind_request, Status.IN_PROGRESS_STATUS, "2015-04-29 12:01:00")

        ind_request_status_in_prog_2 = self.create_request_status(
            ind_request, Status.IN_PROGRESS_STATUS, "2015-04-29 12:02:00")


        self.assertEquals(ind_request_status_in_prog, ind_request.get_in_progress_request_status())

    def test_get_complete_request_status(self):
        user_e = self.create_user("employee", "employee@company.com", "employee")
        group_e = self.create_group("CompanyEmployee")
        user_e.groups.add(group_e)

        employee = self.create_company_employee(user_e)
        company = employee.company

        # create a request to check statuses for
        ind_request = self.create_request(employee)

        # Null Check
        self.assertEquals(None, ind_request.get_complete_request_status())

        ind_request_status_new = self.create_request_status(
            ind_request, Status.NEW_STATUS, "2015-04-29 12:00:00")

        ind_request_status_comp = self.create_request_status(
            ind_request, Status.COMPLETED_STATUS, "2015-04-29 12:01:00")

        ind_request_status_comp2 = self.create_request_status(
            ind_request, Status.COMPLETED_STATUS, "2015-04-29 12:02:00")

        self.assertEquals(ind_request_status_comp2, ind_request.get_complete_request_status())

    def test_get_requests_for_analyst(self):
        user_e = self.create_user("employee", "employee@company.com", "employee")
        group_e = self.create_group("CompanyEmployee")
        user_e.groups.add(group_e)
        employee = self.create_company_employee(user_e)
        company = employee.company

        # create an analyst to assign those requests to..
        analyst = self.create_user("analyst", "analyst@analyst.com", "analyst")
        group_a = self.create_group("SpotLitAnalyst")
        analyst.groups.add(group_a)
        spotlit_staff = self.create_spotlit_staff(analyst)

        # Null Check
        requests = Request.get_requests_for_analyst(analyst)
        self.assertEquals(len(requests), 0)

        # now lets create a few requests and assign them to an analyst
        ind_request0 = self.create_request(employee)
        ind_request0.assignment = spotlit_staff
        ind_request0.save()

        ind_request1 = self.create_request(employee)
        ind_request1.assignment = spotlit_staff
        ind_request1.save()

        ind_request2 = self.create_request(employee)
        ind_request2.assignment = spotlit_staff
        ind_request2.save()

        requests = Request.get_requests_for_analyst(analyst)

        self.assertEquals(len(requests), 3)

    def test_generate_display_id(self):
        user_e = self.create_user("employee", "employee@company.com", "employee")
        group_e = self.create_group("CompanyEmployee")
        user_e.groups.add(group_e)
        employee = self.create_company_employee(user_e)
        company = employee.company


        # lets create a request to generate the id for..
        ind_request = self.create_request(employee)
        id_str = str(ind_request.id)

        if (len(id_str) < 4):
            id_str = id_str.zfill(4)


        ind_request_display_id = "HR-"+id_str
        self.assertEquals(ind_request_display_id, Request.generate_display_id(ind_request))

    ###########################
    #
    #   Corporate Request Tests
    #
    ###########################

    def test_get_report_url(self):
        user_e = self.create_user("employee", "employee@company.com", "employee")
        group_e = self.create_group("CompanyEmployee")
        user_e.groups.add(group_e)
        employee = self.create_company_employee(user_e)
        company = employee.company

        # create a request
        corp_request = self.create_corporate_request(employee)
        status = Status.add_request_status(corp_request, Status.NEW_STATUS, 'No Comment!')
        self.assertEquals(status is not None, True)

        # now we are going to create a slugged url
        date = datetime.datetime.now().strftime("%Y-%m-%d")
        test_url = "%s_%s_%s" % (slugify(corp_request.company_name), date, corp_request.display_id)
        self.assertEquals(test_url, corp_request.get_report_url())

    def test_generate_display_id(self):
        # create an employee to create some requests
        user_e = self.create_user("employee", "employee@company.com", "employee")
        group_e = self.create_group("CompanyEmployee")
        user_e.groups.add(group_e)
        employee = self.create_company_employee(user_e)
        company = employee.company

        corp_request = self.create_corporate_request(employee)

        id_str = str(corp_request.id)

        if (len(id_str) < 4):
            id_str = id_str.zfill(4)

        self.assertEquals("HR-"+id_str, CorporateRequest.generate_display_id(corp_request))

    def test_get_request_status(self):
        # create an employee to create some requests
        user_e = self.create_user("employee", "employee@company.com", "employee")
        group_e = self.create_group("CompanyEmployee")
        user_e.groups.add(group_e)
        employee = self.create_company_employee(user_e)
        company = employee.company

        corp_request = self.create_corporate_request(employee)
        self.assertEquals(None, corp_request.get_request_status())

        status_new = self.create_request_status(corp_request, Status.NEW_STATUS, "2015-04-29 12:00:00")
        status_assigned = self.create_request_status(corp_request, Status.ASSIGNED_STATUS, "2015-04-29 12:00:01")

        self.assertEquals(Status.ASSIGNED_STATUS, corp_request.get_request_status())

    def test_get_requests_for_analyst(self):
        user_e = self.create_user("employee", "employee@company.com", "employee")
        group_e = self.create_group("CompanyEmployee")
        user_e.groups.add(group_e)
        employee = self.create_company_employee(user_e)
        company = employee.company

        # create an analyst to assign those requests to..
        analyst = self.create_user("analyst", "analyst@analyst.com", "analyst")
        group_a = self.create_group("SpotLitAnalyst")
        analyst.groups.add(group_a)
        spotlit_staff = self.create_spotlit_staff(analyst)

        # Null Check
        requests = CorporateRequest.get_requests_for_analyst(analyst)
        self.assertEquals(len(requests), 0)

        # now lets create a few requests and assign them to an analyst
        ind_request0 = self.create_corporate_request(employee)
        ind_request0.assignment = spotlit_staff
        ind_request0.save()

        ind_request1 = self.create_corporate_request(employee)
        ind_request1.assignment = spotlit_staff
        ind_request1.save()

        ind_request2 = self.create_corporate_request(employee)
        ind_request2.assignment = spotlit_staff
        ind_request2.save()

        requests = CorporateRequest.get_requests_for_analyst(analyst)

        self.assertEquals(len(requests), 3)

    ###########################
    #
    #   Custom Request Tests
    #
    ###########################

    def test_get_custom_request_status(self):
        # create a company, user, and a company employee
        user_e = self.create_user("employee", "employee@company.com", "employee")
        group_e = self.create_group("CompanyEmployee")
        user_e.groups.add(group_e)
        employee = self.create_company_employee(user_e)
        company = employee.company

        # now lets create some custom requests..
        custom_request = self.create_custom_request(employee)
        status = self.create_request_status(custom_request, Status.NEW_STATUS, "2015-04-29 12:00:00")
        self.assertEquals(Status.NEW_STATUS, custom_request.get_request_status())

    def test_get_custom_report_url(self):
        # create a company, user, and a company employee
        user_e = self.create_user("employee", "employee@company.com", "employee")
        group_e = self.create_group("CompanyEmployee")
        user_e.groups.add(group_e)
        employee = self.create_company_employee(user_e)
        company = employee.company

        # now lets create some custom requests..
        custom_request = self.create_custom_request(employee)
        status = self.create_request_status(custom_request, Status.NEW_STATUS, "2015-04-29 12:00:00")

        # now we are going to create a slugged url
        date = datetime.datetime.now().strftime("%Y-%m-%d")
        test_url = "%s_%s_%s" % (slugify(custom_request.created_by.company.name), date, custom_request.display_id)
        self.assertEquals(test_url, custom_request.get_report_url())

    def test_get_custom_in_progress_request_status(self):
        # create a company, user, and a company employee
        user_e = self.create_user("employee", "employee@company.com", "employee")
        group_e = self.create_group("CompanyEmployee")
        user_e.groups.add(group_e)
        employee = self.create_company_employee(user_e)
        company = employee.company

        # now lets create some custom requests..
        custom_request = self.create_custom_request(employee)

        # null check
        get_in_prog_status = custom_request.get_in_progress_request_status()
        self.assertEquals(get_in_prog_status, None)

        status_new = self.create_request_status(custom_request, Status.NEW_STATUS, "2015-04-29 12:00:00")
        status_in_progress = self.create_request_status(custom_request, Status.IN_PROGRESS_STATUS, "2015-04-29 12:00:00")
        get_in_prog_status = custom_request.get_in_progress_request_status()
        self.assertEquals(get_in_prog_status, status_in_progress)

    def test_get_custom_complete_request_status(self):
        # create a company, user, and a company employee
        user_e = self.create_user("employee", "employee@company.com", "employee")
        group_e = self.create_group("CompanyEmployee")
        user_e.groups.add(group_e)
        employee = self.create_company_employee(user_e)
        company = employee.company

        # now lets create some custom requests..
        custom_request = self.create_custom_request(employee)

        # null check
        get_completed_status = custom_request.get_complete_request_status()
        self.assertEquals(get_completed_status, None)

        status_new = self.create_request_status(custom_request, Status.NEW_STATUS, "2015-04-29 12:00:00")
        status_completed = self.create_request_status(custom_request, Status.COMPLETED_STATUS, "2015-04-29 12:00:00")
        get_completed_status = custom_request.get_complete_request_status()
        self.assertEquals(get_completed_status, status_completed)

    def test_get_custom_requests_for_analyst(self):
        # create a company, user, and a company employee
        user_e = self.create_user("employee", "employee@company.com", "employee")
        group_e = self.create_group("CompanyEmployee")
        user_e.groups.add(group_e)
        employee = self.create_company_employee(user_e)
        company = employee.company

        # create an analyst to assign those requests to..
        analyst = self.create_user("analyst", "analyst@analyst.com", "analyst")
        group_a = self.create_group("SpotLitAnalyst")
        analyst.groups.add(group_a)
        spotlit_staff = self.create_spotlit_staff(analyst)

        # null check

        no_requests = CustomRequest.get_requests_for_analyst(analyst)
        self.assertEquals(len(no_requests), 0)


        # now lets create some custom requests..

        dynamic_form = self.create_dynamic_request_form(employee)


        custom_request1 = self.create_custom_request_for_dynamic_form(dynamic_form, employee, 'form 1')
        custom_request1.assignment = spotlit_staff
        custom_request1.save()

        custom_request2 = self.create_custom_request_for_dynamic_form(dynamic_form, employee, 'form 2')
        custom_request2.assignment = spotlit_staff
        custom_request2.save()

        custom_request3 = self.create_custom_request_for_dynamic_form(dynamic_form, employee, 'form 3')
        custom_request3.assignment = spotlit_staff
        custom_request3.save()

        three_requests =  CustomRequest.get_requests_for_analyst(analyst)
        self.assertEquals(len(three_requests), 3)

    def test_generate_custom_display_id(self):
        # create an employee to create some requests
        user_e = self.create_user("employee", "employee@company.com", "employee")
        group_e = self.create_group("CompanyEmployee")
        user_e.groups.add(group_e)
        employee = self.create_company_employee(user_e)
        company = employee.company

        dynamic_form = self.create_dynamic_request_form(employee)

        custom_request = self.create_custom_request_for_dynamic_form(dynamic_form, employee, "Mark")

        id_str = str(custom_request.id)

        if (len(id_str) < 4):
            id_str = id_str.zfill(4)

        self.assertEquals("HR-"+id_str, CustomRequest.generate_display_id(custom_request))

    ###########################
    #
    #   SpotLitStaff Tests
    #
    ###########################

    def test_is_analyst(self):
        user_m = self.create_user("manager", "manager@manager.com", "manager")
        user_a = self.create_user("analyst", "analyst@analyst.com", "analyst")

        group_m = self.create_group("SpotLitManager")
        group_a = self.create_group("SpotLitAnalyst")

        user_m.groups.add(group_m)
        user_m.save()
        manager = self.create_spotlit_staff(user_m)

        user_a.groups.add(group_a)
        user_a.save()
        analyst = self.create_spotlit_staff(user_a)

        test_manager = manager.is_analyst()
        self.assertEquals(test_manager, False)

        test_analyst = analyst.is_analyst()
        self.assertEquals(test_analyst, True)

    def test_is_manager(self):
        user_m = self.create_user("manager", "manager@manager.com", "manager")
        user_a = self.create_user("analyst", "analyst@analyst.com", "analyst")

        group_m = self.create_group("SpotLitManager")
        group_a = self.create_group("SpotLitAnalyst")

        user_m.groups.add(group_m)
        user_m.save()
        manager = self.create_spotlit_staff(user_m)

        user_a.groups.add(group_a)
        user_a.save()
        analyst = self.create_spotlit_staff(user_a)

        test_manager = manager.is_manager()
        self.assertEquals(test_manager, True)

        test_analyst = analyst.is_manager()
        self.assertEquals(test_analyst, False)

    def test_is_reviewer(self):
        user_r = self.create_user("reviewer", "reviewer@reviewer.com", "reviewer")
        group_r = self.create_group("Reviewer")

        user_r.groups.add(group_r)
        user_r.save()

        reviewer = self.create_spotlit_staff(user_r)
        test_reviewer = reviewer.is_reviewer()

        self.assertEquals(test_reviewer, True)


        user_m = self.create_user("manager", "manager@manager.com", "manager")
        group_m = self.create_group("SpotlitManager")

        user_m.groups.add(group_m)
        user_m.save()

        manager = self.create_spotlit_staff(user_m)
        test_manager = manager.is_reviewer()

        self.assertEquals(test_manager, False)


    def test_get_analysts(self):
        # test no analysts in user objects
        user_m = self.create_user("manager", "manager@manager.com", "manager")
        group_m = self.create_group("SpotLitManager")
        group_a = self.create_group("SpotLitAnalyst")

        user_m.groups.add(group_m)
        user_m.save()
        manager = self.create_spotlit_staff(user_m)

        test_manager = SpotLitStaff.get_analysts()
        self.assertEquals(len(test_manager), 0)

        # test one analyst
        user_a1 = self.create_user("analyst1", "analyst@analyst.com", "analyst")
        user_a1.groups.add(group_a)
        user_a1.save()
        analyst1 = self.create_spotlit_staff(user_a1)

        analysts = SpotLitStaff.get_analysts()
        self.assertEquals(len(analysts), 1)
        self.assertEquals(analyst1 in analysts, True)

        # test two analysts
        user_a2 = self.create_user("analyst2", "analyst2@analyst.com", "analyst")
        user_a2.groups.add(group_a)
        user_a2.save()
        analyst2 = self.create_spotlit_staff(user_a2)

        analysts = SpotLitStaff.get_analysts()
        self.assertEquals(len(analysts), 2)
        self.assertEquals(analyst2 in analysts, True)


    def test_get_reviewers(self):
        # lets add some reviewers..
        user_r = self.create_user("reviewer", "reviewer@reviewer.com", "reviewer")
        group_r = self.create_group("Reviewer")
        user_r.groups.add(group_r)
        reviewer = self.create_spotlit_staff(user_r)

        user_r1 = self.create_user("reviewer1", "reviewer1@reviewer.com", "reviewer1")
        user_r1.groups.add(group_r)
        reviewer1 = self.create_spotlit_staff(user_r1)

        user_r2 = self.create_user("reviewer2", "reviewer2@reviewer.com", "reviewer2")
        user_r2.groups.add(group_r)
        reviewer2 = self.create_spotlit_staff(user_r2)

        reviewers = SpotLitStaff.get_reviewers()

        self.assertEquals(len(reviewers), 3)
        self.assertEquals(reviewer in reviewers, True)
        self.assertEquals(reviewer1 in reviewers, True)
        self.assertEquals(reviewer2 in reviewers, True)






    ###########################
    #
    #   CompanyDueDiligenceTypeSelection Tests
    #
    ###########################

    def test_get_due_diligence_types_for_current_user(self):
        user_e = self.create_user("employee", "employee@company.com", "employee")
        group_e = self.create_group("CompanyEmployee")
        user_e.groups.add(group_e)

        employee = self.create_company_employee(user_e)
        company = employee.company

        # test no dd_types
        dd_types = CompanyDueDiligenceTypeSelection.get_due_diligence_types_for_current_user(user_e)
        self.assertEquals(len(dd_types), 0)

        # test returns correct dd_types
        hr = self.create_due_diligence_type("HR")
        investigative = self.create_due_diligence_type("investigative")
        selection = self.create_company_due_diligence_selection(company, hr)

        dd_types = CompanyDueDiligenceTypeSelection.get_due_diligence_types_for_current_user(user_e)
        self.assertEquals(len(dd_types), 1)
        self.assertEquals(dd_types.first().due_diligence_type == hr, True)

    ###########################
    #
    #   CompanyServiceSelection Tests
    #
    ###########################

    def test_get_service_selections_for_request(self):
        self.assertEquals(True, True)

    ###########################
    #
    #   CompanyEmployee Tests
    #
    ###########################

    def test_get_company_employee(self):
        self.assertEquals(True, True)













