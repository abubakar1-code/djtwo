from django.test import TestCase
from django.test import Client
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User, Group
from core.models import Company, CompanyDueDiligenceTypeSelection, CompanyEmployee, CorporateRequest, CustomRequest,\
    CustomRequestFields, DueDiligenceType, DynamicRequestForm, DynamicRequestFormFields, LayoutGroupSections, Request,\
    RequestFormFieldTypes, SpotLitStaff, Status


class ViewsTest(TestCase):
    urls = 'spotlit_due_diligence.spotlit_due_diligence.urls'

    ###########################
    #
    # Helpers
    #
    ###########################


    def create_user(self, name, email, password):
        user = User.objects.create_user(name, email, password)
        user.save()
        return user

    def create_group(self, group_name):
        group = Group(name=group_name)
        group.save()
        return group

    def create_company_employee(self, user):
        company = Company(name='company')
        company.save()
        employee = CompanyEmployee(user=user, phone_number='123445667', company=company, position='HR Rep')
        employee.save()
        return employee

    def create_etrade_company_employee(self, user):
        company = Company(name='E*TRADE')
        company.save()
        employee = CompanyEmployee(user=user, phone_number='123445667', company=company, position='HR Rep')
        employee.save()
        return employee

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
            label='Reporting Period',
            group=group_section,
        )
        form_field.save()

        request_type = DueDiligenceType(name="Human Resources")
        request_type.save()
        request_type_selection = CompanyDueDiligenceTypeSelection(company=employee.company,
                                                                  due_diligence_type=request_type,
                                                                  name="test", comments="", level=1)
        request_type_selection.save()



        custom_request = CustomRequest(
            dynamic_request_form=dynamic_request_form,
            name='custom request',
            created_by=employee,
            request_type=request_type_selection
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

    def create_request_status(self, request, status, datetime):
        request_status = Status(content_object=request, status=status, datetime=datetime, comments='')
        request_status.save()
        return request_status




    ###########################
    #
    # Test Login
    #
    ###########################

    def test_login_view(self):
        with self.settings(STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage'):
            client = Client()
            url = reverse('login')
            response = client.get(url)
            self.assertEquals(response.status_code, 200)

    def test_login(self):
        with self.settings(STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage'):
            user_e = self.create_user("employee", "employee@company.com", "employee")
            group_e = self.create_group("CompanyEmployee")
            user_e.groups.add(group_e)

            employee = self.create_company_employee(user_e)
            company = employee.company
            client = Client()
            url = reverse('login')
            response = client.post(url, {'username': 'employee', 'password': 'employee'}, follow=True)
            self.assertEquals(response.status_code, 200)


    ###########################
    #
    # Test Employee User
    #
    ###########################


    def test_employee_dashboard(self):
        with self.settings(STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage'):
            # lets first create a user, and make them an employee
            user_e = self.create_user("employee", "employee@company.com", "employee")
            group_e = self.create_group("CompanyEmployee")
            user_e.groups.add(group_e)
            employee = self.create_company_employee(user_e)
            company = employee.company

            # next we must log this employee in.
            client = Client()
            url = reverse('login')
            response = client.post(url, {'username': 'employee', 'password': 'employee'}, follow=True)
            self.assertEquals(response.status_code, 200)

            dashboard_url = reverse('employee_dashboard')
            response = client.get(dashboard_url, follow=True)
            self.assertEquals(response.status_code, 200)
            self.assertTrue('company_logo_active' in response.context)
            self.assertTrue('company_logo' in response.context)
            self.assertTrue('is_corporate' in response.context)
            self.assertTrue('is_individual' in response.context)
            self.assertTrue('is_custom' in response.context)
            self.assertTrue('is_custom_sidebar' in response.context)
            self.assertTrue('custom_requests' in response.context)

    def test_advanced_search_employee(self):
        with self.settings(STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage'):
            # lets first create a user, and make them an employee
            user_e = self.create_user("employee", "employee@company.com", "employee")
            group_e = self.create_group("CompanyEmployee")
            user_e.groups.add(group_e)
            employee = self.create_company_employee(user_e)
            company = employee.company

            # next we must log this employee in.
            client = Client()
            url = reverse('login')
            response = client.post(url, {'username': 'employee', 'password': 'employee'}, follow=True)
            self.assertEquals(response.status_code, 200)

            advanced_search_url = reverse('advanced_search_employee')
            response = client.get(advanced_search_url)
            self.assertEquals(response.status_code, 200)
            self.assertTrue('analysts' in response.context)
            self.assertTrue('types' in response.context)
            self.assertTrue('statuses' in response.context)
            self.assertTrue('request_types' in response.context)
            self.assertTrue('is_custom' in response.context)
            self.assertTrue('is_individual' in response.context)
            self.assertTrue('is_custom_sidebar' in response.context)
            self.assertTrue('is_corporate_sidebar' in response.context)
            self.assertTrue('is_corporate' in response.context)
            self.assertTrue('fields' in response.context)
            self.assertTrue('dynamic_forms' in response.context)
            self.assertTrue('custom_requests' in response.context)
            self.assertTrue('company_logo' in response.context)
            self.assertTrue('company_logo_active' in response.context)
            self.assertTrue('company' in response.context)

    def test_create_individual_request_view(self):
        with self.settings(STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage'):
            # lets first create a user, and make them an employee
            user_e = self.create_user("employee", "employee@company.com", "employee")
            group_e = self.create_group("CompanyEmployee")
            user_e.groups.add(group_e)
            employee = self.create_company_employee(user_e)
            company = employee.company

            # next we must log this employee in.
            client = Client()
            url = reverse('login')
            response = client.post(url, {'username': 'employee', 'password': 'employee'}, follow=True)
            self.assertEquals(response.status_code, 200)


            create_ind_req_url = reverse('create_individual_request')
            response = client.get(create_ind_req_url)
            self.assertEquals(response.status_code, 200)

            response = client.post(create_ind_req_url, {'request_type': 1000, 'first_name': 'Mark'}, follow=True)
            self.assertEquals(response.status_code, 200)

    def test_create_corporate_request_view(self):
        with self.settings(STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage'):
            # lets first create a user, and make them an employee
            user_e = self.create_user("employee", "employee@company.com", "employee")
            group_e = self.create_group("CompanyEmployee")
            user_e.groups.add(group_e)
            employee = self.create_company_employee(user_e)
            company = employee.company

            # next we must log this employee in.
            client = Client()
            url = reverse('login')
            response = client.post(url, {'username': 'employee', 'password': 'employee'}, follow=True)
            self.assertEquals(response.status_code, 200)

            create_corp_req_url = reverse('create_corporate_request')
            response = client.get(create_corp_req_url, follow=True)
            self.assertEquals(response.status_code, 200)

            response = client.post(
                create_corp_req_url, {'request_type': 1000, 'company_name': 'Test Company'}, follow=True)
            self.assertEquals(response.status_code, 200)

    def test_create_custom_request(self):
        with self.settings(STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage'):
            # lets first create a user, and make them an employee
            user_e = self.create_user("employee", "employee@company.com", "employee")
            group_e = self.create_group("CompanyEmployee")
            user_e.groups.add(group_e)
            employee = self.create_company_employee(user_e)
            company = employee.company

            # next we must log this employee in.
            client = Client()
            url = reverse('login')
            response = client.post(url, {'username': 'employee', 'password': 'employee'}, follow=True)
            self.assertEquals(response.status_code, 200)

            dynamic_request = self.create_dynamic_request_form(employee)

            create_custom_request_url = reverse('create_custom_request', kwargs={'dynamic_request_pk':dynamic_request.id})

            response = client.post(create_custom_request_url, {'request_type': 1000, 'name': 'name'}, follow=True)

            self.assertEquals(response.status_code, 200)



    ###########################
    #
    # Test Supervisor User
    #
    ###########################




    ###########################
    #
    # Test Manager User
    #
    ###########################

    def test_manager_request_for_custom_detail_view(self):
        with self.settings(STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage'):
            # we need to create a custom request, a custom request must be created by a employee so let's do that 1st
            # create employee...
            user_e = self.create_user("employee", "employee@company.com", "employee")
            group_e = self.create_group("CompanyEmployee")
            user_e.groups.add(group_e)
            employee = self.create_company_employee(user_e)
            company = employee.company

            client = Client()
            url = reverse('login')
            response = client.post(url, {'username': 'employee', 'password': 'employee'}, follow=True)
            self.assertEquals(response.status_code, 200)

            # now lets create that custom request
            custom_request = self.create_custom_request(employee)

            # lets create another user, and make them a manager
            manager_user = self.create_user("manager", "manager@company.com", "manager")
            manager_group = self.create_group("SpotLitManager")
            manager_user.groups.add(manager_group)

            # next log the manager in
            client = Client()
            url = reverse('login')
            response = client.post(url, {'username': 'manager', 'password': 'manager'}, follow=True)
            self.assertEquals(response.status_code, 200)

            # lets also create a status for this
            status_new = self.create_request_status(custom_request, Status.NEW_STATUS, "2015-04-29 11:59:00")
            status_complete = self.create_request_status(custom_request, Status.COMPLETED_STATUS, "2015-04-29 12:00:00")


            # now lets test if we get the detail view back
            url = reverse('custom_request_manager', kwargs={"pk": custom_request.id})
            response = client.get(url, follow=True)
            self.assertEquals(response.status_code, 200)

    # writing unit tests to make sure something doesn't exist...
    def test_delete_dd_failure(self):
        with self.settings(STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage'):
            user_e = self.create_user("employee", "employee@company.com", "employee")
            group_e = self.create_group("CompanyEmployee")
            user_e.groups.add(group_e)
            employee = self.create_company_employee(user_e)
            company = employee.company

            request = self.create_request(employee)

            url = '/delete_dd_type/'+str(company.id) +'/'+str(request.request_type.id)
            client = Client()
            response = client.get(url, follow=True)
            self.assertEquals(response.status_code, 404)

    # writing unit tests to make sure something doesn't exist...
    def test_delete_employee_failure(self):
        with self.settings(STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage'):
            user_e = self.create_user("employee", "employee@company.com", "employee")
            group_e = self.create_group("CompanyEmployee")
            user_e.groups.add(group_e)
            employee = self.create_company_employee(user_e)
            company = employee.company

            request = self.create_request(employee)

            url = '/employee_delete/'+str(company.id) +'/'+str(employee.id)
            client = Client()
            response = client.get(url, follow=True)
            self.assertEquals(response.status_code, 404)

    # writing unit tests to make sure something doesn't exist...
    def test_dynamic_request_form_delete_failure(self):
        with self.settings(STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage'):
            user_e = self.create_user("employee", "employee@company.com", "employee")
            group_e = self.create_group("CompanyEmployee")
            user_e.groups.add(group_e)
            employee = self.create_company_employee(user_e)
            company = employee.company

            dynamic_form = self.create_dynamic_request_form(employee)

            request = self.create_request(employee)
            url = '/dynamic_request_form_delete/'+str(company.id)+'/'+str(dynamic_form.id)

            client = Client()
            response = client.get(url, follow=True)
            self.assertEquals(response.status_code, 404)

    #ajax call for a manager to change a reviewer on a individual request
    def test_ajax_change_reviewer(self):
        with self.settings(STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage'):
            # we need to create request, a request must be created by a employee so let's do that 1st
            # create employee...
            user_e = self.create_user("employee", "employee@company.com", "employee")
            group_e = self.create_group("CompanyEmployee")
            user_e.groups.add(group_e)
            employee = self.create_company_employee(user_e)
            company = employee.company
            request = self.create_request(employee)
            # create a reviewer
            user_r = self.create_user("reviewer", "reviewer@reviewer.com", "reviewer")
            group_r = self.create_group("Reviewer")
            user_r.groups.add(group_r)
            reviewer = SpotLitStaff(user=user_r, phone_number="1234567890", is_activated=True)
            reviewer.save()
            request.reviewer = reviewer

            # create a reviewer
            user_r2 = self.create_user("reviewer2", "reviewer2@reviewer.com", "reviewer2")
            user_r2.groups.add(group_r)
            reviewer2 = SpotLitStaff(user=user_r2, phone_number="1234567890", is_activated=True)
            reviewer2.save()

            client = Client()
            response = client.post('/ajax_edit_reviewer/', {'reviewer': reviewer2.id, 'requestID': request.id },HTTP_X_REQUESTED_WITH='XMLHttpRequest')
            self.assertEquals(response.status_code, 200)
            request = Request.objects.get(pk=request.id)
            self.assertEquals(request.reviewer.id, reviewer2.id)

            response = client.get(reverse('ajax_edit_reviewer'))
            self.assertEquals(response.status_code, 500)

    #ajax call for a manager to change a reviewer on a custom request
    def test_ajax_change_reviewer_custom(self):
        with self.settings(STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage'):
            # we need to create request, a request must be created by a employee so let's do that 1st
            # create employee...
            user_e = self.create_user("employee", "employee@company.com", "employee")
            group_e = self.create_group("CompanyEmployee")
            user_e.groups.add(group_e)
            employee = self.create_company_employee(user_e)
            company = employee.company
            request = self.create_custom_request(employee)
            # create a reviewer
            user_r = self.create_user("reviewer", "reviewer@reviewer.com", "reviewer")
            group_r = self.create_group("Reviewer")
            user_r.groups.add(group_r)
            reviewer = SpotLitStaff(user=user_r, phone_number="1234567890", is_activated=True)
            reviewer.save()
            request.reviewer = reviewer

            # create a reviewer
            user_r2 = self.create_user("reviewer2", "reviewer2@reviewer.com", "reviewer2")
            user_r2.groups.add(group_r)
            reviewer2 = SpotLitStaff(user=user_r2, phone_number="1234567890", is_activated=True)
            reviewer2.save()

            client = Client()
            response = client.post('/ajax_edit_reviewer_custom/', {'reviewer': reviewer2.id, 'requestID': request.id },HTTP_X_REQUESTED_WITH='XMLHttpRequest')
            self.assertEquals(response.status_code, 200)
            request = CustomRequest.objects.get(pk=request.id)
            self.assertEquals(request.reviewer.id, reviewer2.id)

            response = client.get(reverse('ajax_edit_reviewer_custom'))
            self.assertEquals(response.status_code, 500)

    #ajax call for a manager to change a reviewer on a corporate request
    def test_ajax_change_reviewer_corporate(self):
        with self.settings(STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage'):
            # we need to create request, a request must be created by a employee so let's do that 1st
            # create employee...
            user_e = self.create_user("employee", "employee@company.com", "employee")
            group_e = self.create_group("CompanyEmployee")
            user_e.groups.add(group_e)
            employee = self.create_company_employee(user_e)
            company = employee.company
            request = self.create_corporate_request(employee)
            # create a reviewer
            user_r = self.create_user("reviewer", "reviewer@reviewer.com", "reviewer")
            group_r = self.create_group("Reviewer")
            user_r.groups.add(group_r)
            reviewer = SpotLitStaff(user=user_r, phone_number="1234567890", is_activated=True)
            reviewer.save()
            request.reviewer = reviewer

            # create a reviewer
            user_r2 = self.create_user("reviewer2", "reviewer2@reviewer.com", "reviewer2")
            user_r2.groups.add(group_r)
            reviewer2 = SpotLitStaff(user=user_r2, phone_number="1234567890", is_activated=True)
            reviewer2.save()

            client = Client()
            response = client.post('/ajax_edit_reviewer_corporate/', {'reviewer': reviewer2.id, 'requestID': request.id },HTTP_X_REQUESTED_WITH='XMLHttpRequest')
            self.assertEquals(response.status_code, 200)
            request = CorporateRequest.objects.get(pk=request.id)
            self.assertEquals(request.reviewer.id, reviewer2.id)

            response = client.get(reverse('ajax_edit_reviewer_corporate'))
            self.assertEquals(response.status_code, 500)

    def test_ajax_change_analyst_corporate(self):
        with self.settings(STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage'):
            # we need to create request, a request must be created by a employee so let's do that 1st
            # create employee...
            user_e = self.create_user("employee", "employee@company.com", "employee")
            group_e = self.create_group("CompanyEmployee")
            user_e.groups.add(group_e)
            employee = self.create_company_employee(user_e)
            company = employee.company
            request = self.create_corporate_request(employee)


            # create a analyst
            user_a = self.create_user("analyst", "analyst@analyst.com", "analyst")
            group_a = self.create_group("SpotLitAnalyst")
            user_a.groups.add(group_a)
            analyst = SpotLitStaff(user=user_a, phone_number="1234567890", is_activated=True)
            analyst.save()
            request.assignment = analyst
            status = self.create_request_status(request, Status.ASSIGNED_STATUS, "2015-04-29 11:59:00")

            # create a analyst
            user_a2 = self.create_user("analyst2", "analyst2@analyst.com", "analyst2")
            user_a2.groups.add(group_a)
            analyst2 = SpotLitStaff(user=user_a2, phone_number="1234567890", is_activated=True)
            analyst2.save()

            client = Client()
            response = client.post('/ajax_edit_analyst_corporate/', {'analyst': analyst2.id, 'requestID': request.id}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
            self.assertEquals(response.status_code, 200)
            request = CorporateRequest.objects.get(pk=request.id)
            self.assertEquals(request.assignment.id, analyst2.id)

            response = client.get(reverse('ajax_edit_analyst_corporate'))
            self.assertEquals(response.status_code, 500)

    def test_ajax_change_analyst(self):
        with self.settings(STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage'):
            # we need to create request, a request must be created by a employee so let's do that 1st
            # create employee...
            user_e = self.create_user("employee", "employee@company.com", "employee")
            group_e = self.create_group("CompanyEmployee")
            user_e.groups.add(group_e)
            employee = self.create_company_employee(user_e)
            company = employee.company
            request = self.create_request(employee)


            # create a analyst
            user_a = self.create_user("analyst", "analyst@analyst.com", "analyst")
            group_a = self.create_group("SpotLitAnalyst")
            user_a.groups.add(group_a)
            analyst = SpotLitStaff(user=user_a, phone_number="1234567890", is_activated=True)
            analyst.save()
            request.assignment = analyst
            status = self.create_request_status(request, Status.ASSIGNED_STATUS, "2015-04-29 11:59:00")

            # create a analyst
            user_a2 = self.create_user("analyst2", "analyst2@analyst.com", "analyst2")
            user_a2.groups.add(group_a)
            analyst2 = SpotLitStaff(user=user_a2, phone_number="1234567890", is_activated=True)
            analyst2.save()

            client = Client()
            response = client.post('/ajax_edit_analyst/', {'analyst': analyst2.id, 'requestID': request.id}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
            self.assertEquals(response.status_code, 200)
            request = Request.objects.get(pk=request.id)
            self.assertEquals(request.assignment.id, analyst2.id)

            response = client.get(reverse('ajax_edit_analyst'))
            self.assertEquals(response.status_code, 500)

    def test_ajax_change_analyst_custom(self):
        with self.settings(STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage'):
            # we need to create request, a request must be created by a employee so let's do that 1st
            # create employee...
            user_e = self.create_user("employee", "employee@company.com", "employee")
            group_e = self.create_group("CompanyEmployee")
            user_e.groups.add(group_e)
            employee = self.create_company_employee(user_e)
            company = employee.company
            request = self.create_custom_request(employee)


            # create a analyst
            user_a = self.create_user("analyst", "analyst@analyst.com", "analyst")
            group_a = self.create_group("SpotLitAnalyst")
            user_a.groups.add(group_a)
            analyst = SpotLitStaff(user=user_a, phone_number="1234567890", is_activated=True)
            analyst.save()
            request.assignment = analyst
            status = self.create_request_status(request, Status.ASSIGNED_STATUS, "2015-04-29 11:59:00")

            # create a analyst
            user_a2 = self.create_user("analyst2", "analyst2@analyst.com", "analyst2")
            user_a2.groups.add(group_a)
            analyst2 = SpotLitStaff(user=user_a2, phone_number="1234567890", is_activated=True)
            analyst2.save()

            client = Client()
            response = client.post('/ajax_edit_analyst_custom/', {'analyst': analyst2.id, 'requestID': request.id}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
            self.assertEquals(response.status_code, 200)
            request = CustomRequest.objects.get(pk=request.id)
            self.assertEquals(request.assignment.id, analyst2.id)

            response = client.get(reverse('ajax_edit_analyst_custom'))
            self.assertEquals(response.status_code, 500)

    def test_assign_staff(self):
        # we need to create a request, a request must be created by a employee so let's do that 1st
        # create employee...
        user_e = self.create_user("employee", "employee@company.com", "employee")
        group_e = self.create_group("CompanyEmployee")
        user_e.groups.add(group_e)
        employee = self.create_company_employee(user_e)
        company = employee.company

        # now lets create a request
        request = self.create_request(employee)
        status = self.create_request_status(request, Status.NEW_STATUS, "2015-04-29 11:59:00")


        # lets create another user, and make them a manager
        manager_user = self.create_user("manager", "manager@company.com", "manager")
        manager_group = self.create_group("SpotLitManager")
        manager_user.groups.add(manager_group)

        # now we need to create a analyst to assign to
        analyst_user = self.create_user("analyst", "analyst@analyst.com", "analyst")
        analyst_group = self.create_group("SpotlitAnalyst")
        analyst_user.groups.add(analyst_group)
        analyst = SpotLitStaff(user=analyst_user, phone_number="1234567890", is_activated=True)
        analyst.save()

        # we also need to create a reviewer to assign to.
        reviewer_user = self.create_user("reviewer", "reviewer@reviewer.com", "reviewer")
        reviewer_group = self.create_group("Reviewer")
        reviewer_user.groups.add(reviewer_group)
        reviewer = SpotLitStaff(user=reviewer_user, phone_number="1234567890", is_activated=True)
        reviewer.save()

        # next log the manager in
        client = Client()
        url = reverse('login')
        response = client.post(url, {'username': 'manager', 'password': 'manager'}, follow=True)
        self.assertEquals(response.status_code, 200)

        url = reverse('assign', kwargs={"pk": request.id})
        response = client.post(url, {'analyst': analyst.id, 'reviewer': reviewer.id, 'comments': "a comment"},
                               follow=True)

        self.assertEquals(response.status_code, 200)
        request = Request.objects.get(pk=request.id)

        self.assertEquals(request.assignment, analyst)
        self.assertEquals(request.reviewer, reviewer)

    def test_assign_corporate_staff(self):
        # we need to create a request, a request must be created by a employee so let's do that 1st
        # create employee...
        user_e = self.create_user("employee", "employee@company.com", "employee")
        group_e = self.create_group("CompanyEmployee")
        user_e.groups.add(group_e)
        employee = self.create_company_employee(user_e)
        company = employee.company

        # now lets create a request
        request = self.create_corporate_request(employee)
        status = self.create_request_status(request, Status.NEW_STATUS, "2015-04-29 11:59:00")


        # lets create another user, and make them a manager
        manager_user = self.create_user("manager", "manager@company.com", "manager")
        manager_group = self.create_group("SpotLitManager")
        manager_user.groups.add(manager_group)

        # now we need to create a analyst to assign to
        analyst_user = self.create_user("analyst", "analyst@analyst.com", "analyst")
        analyst_group = self.create_group("SpotlitAnalyst")
        analyst_user.groups.add(analyst_group)
        analyst = SpotLitStaff(user=analyst_user, phone_number="1234567890", is_activated=True)
        analyst.save()

        # we also need to create a reviewer to assign to.
        reviewer_user = self.create_user("reviewer", "reviewer@reviewer.com", "reviewer")
        reviewer_group = self.create_group("Reviewer")
        reviewer_user.groups.add(reviewer_group)
        reviewer = SpotLitStaff(user=reviewer_user, phone_number="1234567890", is_activated=True)
        reviewer.save()

        # next log the manager in
        client = Client()
        url = reverse('login')
        response = client.post(url, {'username': 'manager', 'password': 'manager'}, follow=True)
        self.assertEquals(response.status_code, 200)

        url = reverse('corporate_assign', kwargs={"pk": request.id})
        response = client.post(url, {'analyst': analyst.id, 'reviewer': reviewer.id, 'comments': "a comment"},
                               follow=True)

        self.assertEquals(response.status_code, 200)
        request = CorporateRequest.objects.get(pk=request.id)

        self.assertEquals(request.assignment, analyst)
        self.assertEquals(request.reviewer, reviewer)

    def test_assign_custom_staff(self):
        # we need to create a request, a request must be created by a employee so let's do that 1st
        # create employee...
        user_e = self.create_user("employee", "employee@company.com", "employee")
        group_e = self.create_group("CompanyEmployee")
        user_e.groups.add(group_e)
        employee = self.create_company_employee(user_e)
        company = employee.company

        # now lets create a request
        request = self.create_custom_request(employee)
        status = self.create_request_status(request, Status.NEW_STATUS, "2015-04-29 11:59:00")


        # lets create another user, and make them a manager
        manager_user = self.create_user("manager", "manager@company.com", "manager")
        manager_group = self.create_group("SpotLitManager")
        manager_user.groups.add(manager_group)

        # now we need to create a analyst to assign to
        analyst_user = self.create_user("analyst", "analyst@analyst.com", "analyst")
        analyst_group = self.create_group("SpotlitAnalyst")
        analyst_user.groups.add(analyst_group)
        analyst = SpotLitStaff(user=analyst_user, phone_number="1234567890", is_activated=True)
        analyst.save()

        # we also need to create a reviewer to assign to.
        reviewer_user = self.create_user("reviewer", "reviewer@reviewer.com", "reviewer")
        reviewer_group = self.create_group("Reviewer")
        reviewer_user.groups.add(reviewer_group)
        reviewer = SpotLitStaff(user=reviewer_user, phone_number="1234567890", is_activated=True)
        reviewer.save()

        # next log the manager in
        client = Client()
        url = reverse('login')
        response = client.post(url, {'username': 'manager', 'password': 'manager'}, follow=True)
        self.assertEquals(response.status_code, 200)

        url = reverse('custom_assign', kwargs={"pk": request.id})
        response = client.post(url, {'analyst': analyst.id, 'reviewer': reviewer.id, 'comments': "a comment"},
                               follow=True)

        self.assertEquals(response.status_code, 200)
        request = CustomRequest.objects.get(pk=request.id)

        self.assertEquals(request.assignment, analyst)
        self.assertEquals(request.reviewer, reviewer)


    ###########################
    #
    # Test Reviewer User
    #
    ###########################

    def test_reviewer_dashboard(self):
        reviewer_user = self.create_user("reviewer", "reviewer@reviewer.com", "reviewer")
        reviewer_group = self.create_group("Reviewer")
        reviewer_user.groups.add(reviewer_group)

        client = Client()
        url = reverse('login')
        response = client.post(url, {'username': 'reviewer', 'password': "reviewer"}, follow=True)
        self.assertEquals(response.status_code, 200)

        url = reverse('reviewer_dashboard')
        response = client.get(url, follow=True)
        self.assertEquals(response.status_code, 200)

    def test_reviewer_request_detail_view(self):
        reviewer_user = self.create_user("reviewer", "reviewer@reviewer.com", "reviewer")
        reviewer_group = self.create_group("Reviewer")
        reviewer_user.groups.add(reviewer_group)

        # create employee...
        user_e = self.create_user("employee", "employee@company.com", "employee")
        group_e = self.create_group("CompanyEmployee")
        user_e.groups.add(group_e)
        employee = self.create_company_employee(user_e)
        company = employee.company

        client = Client()
        url = reverse('login')
        response = client.post(url, {'username': 'employee', 'password': "employee"}, follow=True)
        self.assertEquals(response.status_code, 200)

        request = self.create_request(employee)
        new_status = self.create_request_status(request, Status.NEW_STATUS, "2015-04-29 11:59:00")


        # logged in as employee.. should redirect to dashboard.
        url = reverse('request_reviewer', kwargs={"pk": request.id})
        response = client.get(url)
        self.assertEquals(response.status_code, 302)

        # now when logged in as reviewer in new status
        url = reverse('login')
        response = client.post(url, {'username': 'reviewer', 'password': "reviewer"}, follow=True)
        self.assertEquals(response.status_code, 200)

        url = reverse('request_reviewer', kwargs={"pk": request.id})
        response = client.get(url)
        self.assertEquals(response.status_code, 200)

        review_status = self.create_request_status(request, Status.REVIEW_STATUS, "2015-04-29 11:59:01")
        response = client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_reviewer_custom_request_detail_view(self):
        reviewer_user = self.create_user("reviewer", "reviewer@reviewer.com", "reviewer")
        reviewer_group = self.create_group("Reviewer")
        reviewer_user.groups.add(reviewer_group)

        # create employee...
        user_e = self.create_user("employee", "employee@company.com", "employee")
        group_e = self.create_group("CompanyEmployee")
        user_e.groups.add(group_e)
        employee = self.create_company_employee(user_e)
        company = employee.company

        client = Client()
        url = reverse('login')
        response = client.post(url, {'username': 'employee', 'password': "employee"}, follow=True)
        self.assertEquals(response.status_code, 200)

        request = self.create_custom_request(employee)
        new_status = self.create_request_status(request, Status.NEW_STATUS, "2015-04-29 11:59:00")


        # logged in as employee.. should redirect to dashboard.
        url = reverse('request_reviewer_for_custom', kwargs={"pk": request.id})
        response = client.get(url)
        self.assertEquals(response.status_code, 302)

        # now when logged in as reviewer in new status
        url = reverse('login')
        response = client.post(url, {'username': 'reviewer', 'password': "reviewer"}, follow=True)
        self.assertEquals(response.status_code, 200)

        url = reverse('request_reviewer_for_custom', kwargs={"pk": request.id})
        response = client.get(url)
        self.assertEquals(response.status_code, 200)

        review_status = self.create_request_status(request, Status.REVIEW_STATUS, "2015-04-29 11:59:01")
        response = client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_reviewer_corporate_request_detail_view(self):
        reviewer_user = self.create_user("reviewer", "reviewer@reviewer.com", "reviewer")
        reviewer_group = self.create_group("Reviewer")
        reviewer_user.groups.add(reviewer_group)

        # create employee...
        user_e = self.create_user("employee", "employee@company.com", "employee")
        group_e = self.create_group("CompanyEmployee")
        user_e.groups.add(group_e)
        employee = self.create_company_employee(user_e)
        company = employee.company

        client = Client()
        url = reverse('login')
        response = client.post(url, {'username': 'employee', 'password': "employee"}, follow=True)
        self.assertEquals(response.status_code, 200)

        request = self.create_corporate_request(employee)
        new_status = self.create_request_status(request, Status.NEW_STATUS, "2015-04-29 11:59:00")


        # logged in as employee.. should redirect to dashboard.
        url = reverse('request_reviewer_for_corporate', kwargs={"pk": request.id})
        response = client.get(url)
        self.assertEquals(response.status_code, 302)

        # now when logged in as reviewer in new status
        url = reverse('login')
        response = client.post(url, {'username': 'reviewer', 'password': "reviewer"}, follow=True)
        self.assertEquals(response.status_code, 200)

        url = reverse('request_reviewer_for_corporate', kwargs={"pk": request.id})
        response = client.get(url)
        self.assertEquals(response.status_code, 200)

        review_status = self.create_request_status(request, Status.REVIEW_STATUS, "2015-04-29 11:59:01")
        response = client.get(url)
        self.assertEquals(response.status_code, 200)



    ###########################
    #
    # Test Request Actions
    #
    ###########################


    def test_assign_analyst(self):
        with self.settings(STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage'):
            # we need to create request, a request must be created by a employee so let's do that 1st
            # create employee...
            user_e = self.create_user("employee", "employee@company.com", "employee")
            group_e = self.create_group("CompanyEmployee")
            user_e.groups.add(group_e)
            employee = self.create_company_employee(user_e)
            company = employee.company

            # now lets create that request
            request = self.create_request(employee)

            # lets also create a status for this
            status_new = self.create_request_status(request, Status.NEW_STATUS, "2015-04-29 11:59:00")

            # lets create another user, and make them a manager
            manager_user = self.create_user("manager", "manager@prescient.com", "manager")
            manager_group = self.create_group("SpotLitManager")
            manager_user.groups.add(manager_group)

            # create a analyst to assign it to
            analyst_user = self.create_user("analyst", "analyst@prescient.com", "analyst")
            analyst_group = self.create_group("SpotLitAnalyst")
            analyst_user.groups.add(analyst_group)
            analyst_spotlit_staff = SpotLitStaff(user=analyst_user, phone_number="1234567890", is_activated=True)
            analyst_spotlit_staff.save()

            # create a reviewer to assign it to
            reviewer_user = self.create_user("reviewer", "reviewer@prescient.com", "reviewer")
            reviewer_group = self.create_group("Reviewer")
            reviewer_user.groups.add(reviewer_group)
            reviewer_spotlit_staff = SpotLitStaff(user=reviewer_user, phone_number="1234567890", is_activated=True)
            reviewer_spotlit_staff.save()


            # first lets try to assign this as an employee... we should get a redirect
            client = Client()
            url = reverse('login')
            response = client.post(url, {'username': 'employee', 'password': 'employee'}, follow=True)
            self.assertEquals(response.status_code, 200)

            # assign the request to a analyst
            url = reverse('assign', kwargs={"pk": request.id})
            response = client.post(url, {"analyst": analyst_spotlit_staff.id, "comments": "No Comment!"})
            self.assertEquals(response.status_code, 302)

            # next log the manager in
            client = Client()
            url = reverse('login')
            response = client.post(url, {'username': 'manager', 'password': 'manager'}, follow=True)
            self.assertEquals(response.status_code, 200)

            # lets try to assign this when the status is not NEW, it should also redirect
            status_in_progress = self.create_request_status(request, Status.IN_PROGRESS_STATUS, "2015-04-29 12:00:00")
            url = reverse('assign', kwargs={"pk": request.id})
            response = client.post(url, {"analyst": analyst_spotlit_staff.id, "comments": "No Comment!"})
            self.assertEquals(response.status_code, 302)


            # now lets create a New status like it is supposed to be...
            status_new = self.create_request_status(request, Status.NEW_STATUS, "2015-04-29 12:01:00")


            # assign the request to a fake analyst... this should blow up
            url = reverse('assign', kwargs={"pk": request.id})
            response = client.post(url, {"analyst": 99, "comments": "No Comment!"}, follow=True)
            self.assertEquals(response.status_code, 500)

            #finally lets do this right..
            url = reverse('assign', kwargs={"pk": request.id})
            response = client.post(url, {"analyst": analyst_spotlit_staff.id,
                                         "reviewer":reviewer_spotlit_staff.id,
                                         "comments": "No Comment!"}, follow=True)

            self.assertEquals(response.status_code, 200)


            # make sure that it is actually assigned..
            updated_request = Request.objects.get(id=request.id)

            self.assertEquals(request.get_request_status(), Status.ASSIGNED_STATUS)
            self.assertEquals(analyst_spotlit_staff, updated_request.assignment)

    def test_begin_request(self):
        with self.settings(STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage'):
            # we need to create request, a request must be created by a employee so let's do that 1st
            # create employee...
            user_e = self.create_user("employee", "employee@company.com", "employee")
            group_e = self.create_group("CompanyEmployee")
            user_e.groups.add(group_e)
            employee = self.create_company_employee(user_e)
            company = employee.company

            # now lets create that request
            request = self.create_request(employee)

            # lets also create a status for this
            status_new = self.create_request_status(request, Status.NEW_STATUS, "2015-04-29 11:59:00")

            # lets create another user, and make them a manager
            manager_user = self.create_user("manager", "manager@prescient.com", "manager")
            manager_group = self.create_group("SpotLitManager")
            manager_user.groups.add(manager_group)

            # create a analyst to assign it to
            analyst_user = self.create_user("analyst", "analyst@prescient.com", "analyst")
            analyst_group = self.create_group("SpotLitAnalyst")
            analyst_user.groups.add(analyst_group)
            analyst_spotlit_staff = SpotLitStaff(user=analyst_user, phone_number="1234567890", is_activated=True)
            analyst_spotlit_staff.save()

            # assign the request an the analyst
            request.assignment = analyst_spotlit_staff
            request.save()

            # give the request an assigned status
            status_assigned = self.create_request_status(request, Status.ASSIGNED_STATUS, "2015-04-29 12:00:00")

            self.assertEquals(request.assignment, analyst_spotlit_staff)

            # next lets try to begin this request as a manager... this should redirect
            client = Client()
            url = reverse('login')
            response = client.post(url, {'username': 'manager', 'password': 'manager'}, follow=True)
            self.assertEquals(response.status_code, 200)
            # begin the request
            url = reverse('begin', kwargs={"pk": request.id})
            response = client.get(url)
            self.assertEquals(response.status_code, 302)

            # next lets log the analyst in...
            client = Client()
            url = reverse('login')
            response = client.post(url, {'username': 'analyst', 'password': 'analyst'}, follow=True)
            self.assertEquals(response.status_code, 200)

            # lets try to begin the request when it is not in assigned status.. this should also redirect
            status_new = self.create_request_status(request, Status.NEW_STATUS, "2015-04-29 12:01:00")

            # begin the request
            url = reverse('begin', kwargs={"pk": request.id})
            response = client.get(url)
            self.assertEquals(response.status_code, 302)

            # now lets try with a assigned status.. this should work
            status_assigned = self.create_request_status(request, Status.ASSIGNED_STATUS, "2015-04-29 12:02:00")

            # begin the request
            url = reverse('begin', kwargs={"pk": request.id})
            response = client.get(url, follow=True)
            self.assertEquals(response.status_code, 200)


            # test that the status is in progress
            current_status = request.get_request_status()
            self.assertEquals(current_status, Status.IN_PROGRESS_STATUS)

    def test_reject_request(self):
        with self.settings(STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage'):
            # we need to create request, a request must be created by a employee so let's do that 1st
            # create employee...
            user_e = self.create_user("employee", "employee@company.com", "employee")
            group_e = self.create_group("CompanyEmployee")
            user_e.groups.add(group_e)
            employee = self.create_company_employee(user_e)
            company = employee.company

            # now lets create that request
            request = self.create_request(employee)

            # lets also create a status for this
            status_new = self.create_request_status(request, Status.NEW_STATUS, "2015-04-29 11:59:00")

            # lets create another user, and make them a manager
            manager_user = self.create_user("manager", "manager@prescient.com", "manager")
            manager_group = self.create_group("SpotLitManager")
            manager_user.groups.add(manager_group)

            # create a analyst to assign it to
            analyst_user = self.create_user("analyst", "analyst@prescient.com", "analyst")
            analyst_group = self.create_group("SpotLitAnalyst")
            analyst_user.groups.add(analyst_group)
            analyst_spotlit_staff = SpotLitStaff(user=analyst_user, phone_number="1234567890", is_activated=True)
            analyst_spotlit_staff.save()

            # assign the request an the analyst
            request.assignment = analyst_spotlit_staff
            request.save()
            self.assertEquals(request.assignment, analyst_spotlit_staff)

            # give the request an assigned status
            status_assigned = self.create_request_status(request, Status.ASSIGNED_STATUS, "2015-04-29 12:00:00")


            # lets try to reject this request as a employee.. it should redirect..
            client = Client()
            url = reverse('login')
            response = client.post(url, {'username': "employee", 'password':"employee"}, follow=True)
            self.assertEquals(response.status_code, 200)

            # reject the request
            url = reverse('reject', kwargs={"pk": request.id})
            response = client.post(url, {'comments': "No Comment!"})
            self.assertEquals(response.status_code, 302)

            # next lets log the analyst in...
            client = Client()
            url = reverse('login')
            response = client.post(url, {'username': 'analyst', 'password': 'analyst'}, follow=True)
            self.assertEquals(response.status_code, 200)

            # lets try to reject the request when it is not in progress, or assigned
            status_new = self.create_request_status(request, Status.NEW_STATUS, "2015-04-29 12:01:00")

            # reject the request.. this should redirect.
            url = reverse('reject', kwargs={"pk": request.id})
            response = client.post(url, {'comments': "No Comment!"})
            self.assertEquals(response.content, "Rejection Failed")

            # now lets to it when it's assigned...
            status_assigned = self.create_request_status(request, Status.ASSIGNED_STATUS, "2015-04-29 12:02:00")

            # now lets reject it... with a get.. it should fail
            url = reverse('reject', kwargs={"pk": request.id})
            response = client.get(url)
            self.assertEquals(response.content, "Rejection Failed")


            # finnally the way it should be.. this should work
            url = reverse('reject', kwargs={"pk": request.id})
            response = client.post(url, {'comments': "No Comment!"}, follow=True)
            self.assertEquals(response.status_code, 200)

            # test that the status is rejected
            current_status = request.get_request_status()
            self.assertEquals(current_status, Status.REJECTED_STATUS)

    def test_incomplete_request(self):
        with self.settings(STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage'):
            # we need to create request, a request must be created by a employee so let's do that 1st
            # create employee...
            user_e = self.create_user("employee", "employee@company.com", "employee")
            group_e = self.create_group("CompanyEmployee")
            user_e.groups.add(group_e)
            employee = self.create_company_employee(user_e)
            company = employee.company

            # now lets create that request
            request = self.create_request(employee)

            # lets also create a status for this
            status_new = self.create_request_status(request, Status.NEW_STATUS, "2015-04-29 11:59:00")

            # lets create another user, and make them a manager
            manager_user = self.create_user("manager", "manager@prescient.com", "manager")
            manager_group = self.create_group("SpotLitManager")
            manager_user.groups.add(manager_group)

            # create a analyst to assign it to
            analyst_user = self.create_user("analyst", "analyst@prescient.com", "analyst")
            analyst_group = self.create_group("SpotLitAnalyst")
            analyst_user.groups.add(analyst_group)
            analyst_spotlit_staff = SpotLitStaff(user=analyst_user, phone_number="1234567890", is_activated=True)
            analyst_spotlit_staff.save()

            # assign the request an the analyst
            request.assignment = analyst_spotlit_staff
            request.save()

            # give the request an assigned status
            status_assigned = self.create_request_status(request, Status.ASSIGNED_STATUS, "2015-04-29 12:00:00")

            self.assertEquals(request.assignment, analyst_spotlit_staff)

            # next lets log the employee in to mark it incomplete.. this should redirect.
            client = Client()
            url = reverse('login')
            response = client.post(url, {'username': 'employee', 'password': 'employee'}, follow=True)
            self.assertEquals(response.status_code, 200)

            url = reverse('incomplete', kwargs={'pk': request.id})
            response = client.post(url, {'comments': "No Comment!"})
            self.assertEquals(response.status_code, 302)

            # next lets log the manager in...
            client = Client()
            url = reverse('login')
            response = client.post(url, {'username': 'manager', 'password': 'manager'}, follow=True)
            self.assertEquals(response.status_code, 200)

            # next create a submitted status, you shouldn't be able to incomplete a submitted status..
            status_submitted = self.create_request_status(request, Status.SUBMITTED_STATUS, "2015-04-29 12:01:00")

            url = reverse('incomplete', kwargs={'pk': request.id})
            response = client.post(url, {'comments': "No Comment!"}, follow=True)
            self.assertEquals(response.status_code, 200)
            self.assertEquals(response.content, "Incomplete Failed")

            status_new = self.create_request_status(request, Status.NEW_STATUS, "2015-04-29 12:02:00")
            response = client.get(url)
            self.assertEquals(response.content, "Incomplete failed")

            # this one should work.
            response = client.post(url, {'comments': "No Comment!"}, follow=True)
            self.assertEquals(response.status_code, 200)

            # make sure the status was marked incomplete...
            current_status = request.get_request_status()
            self.assertEquals(current_status, Status.INCOMPLETE_STATUS)

    def test_submit_request(self):
        with self.settings(STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage'):
            # we need to create a request, a request must be created by a employee so let's do that 1st
            # create employee...
            user_e = self.create_user("employee", "employee@company.com", "employee")
            group_e = self.create_group("CompanyEmployee")
            user_e.groups.add(group_e)
            employee = self.create_company_employee(user_e)
            company = employee.company

            # now lets create that custom request
            request = self.create_request(employee)

            # lets create another user, and make them a manager
            manager_user = self.create_user("manager", "manager@company.com", "manager")
            manager_group = self.create_group("SpotLitManager")
            manager_user.groups.add(manager_group)

            # next log the manager in
            client = Client()
            url = reverse('login')
            response = client.post(url, {'username': 'manager', 'password': 'manager'}, follow=True)
            self.assertEquals(response.status_code, 200)

            # must have a new status
            status_new = self.create_request_status(request, Status.NEW_STATUS, "2015-04-29 11:59:00")

            # status must be complete to be submitted
            status_complete = self.create_request_status(request, Status.COMPLETED_STATUS, "2015-04-29 12:00:00")

            url = reverse('submit', kwargs={"pk": request.id})
            response = client.post(url, {"comments": "No Comment!"}, follow=True)
            self.assertEquals(response.status_code, 200)

            status = request.get_request_status()

            self.assertEquals(status, Status.SUBMITTED_STATUS)

    def test_return_request(self):
        with self.settings(STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage'):
            # we need to create a request, a request must be created by a employee so let's do that 1st
            # create employee...
            user_e = self.create_user("employee", "employee@company.com", "employee")
            group_e = self.create_group("CompanyEmployee")
            user_e.groups.add(group_e)
            employee = self.create_company_employee(user_e)
            company = employee.company

            # now lets create that custom request
            request = self.create_request(employee)

            # lets create another user, and make them a manager
            manager_user = self.create_user("manager", "manager@company.com", "manager")
            manager_group = self.create_group("SpotLitManager")
            manager_user.groups.add(manager_group)

             # create a analyst to assign it to
            analyst_user = self.create_user("analyst", "analyst@prescient.com", "analyst")
            analyst_group = self.create_group("SpotLitAnalyst")
            analyst_user.groups.add(analyst_group)
            analyst_spotlit_staff = SpotLitStaff(user=analyst_user, phone_number="1234567890", is_activated=True)
            analyst_spotlit_staff.save()

            # assign the request an the analyst
            request.assignment = analyst_spotlit_staff
            request.save()


            # next log the manager in
            client = Client()
            url = reverse('login')
            response = client.post(url, {'username': 'manager', 'password': 'manager'}, follow=True)
            self.assertEquals(response.status_code, 200)

            # must have a new status
            status_new = self.create_request_status(request, Status.NEW_STATUS, "2015-04-29 11:59:00")

            # status must be complete to be returned
            status_complete = self.create_request_status(request, Status.COMPLETED_STATUS, "2015-04-29 12:00:00")

            url = reverse('return', kwargs={"pk": request.id})
            response = client.post(url, {"comments": "No Comment!"}, follow=True)
            self.assertEquals(response.status_code, 200)

            status = request.get_request_status()

            self.assertEquals(status, Status.NEW_RETURNED_STATUS)

    def test_return_request_reviewer(self):
        with self.settings(STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage'):
            # we need to create a request, a request must be created by a employee so let's do that 1st
            # create employee...
            user_e = self.create_user("employee", "employee@company.com", "employee")
            group_e = self.create_group("CompanyEmployee")
            user_e.groups.add(group_e)
            employee = self.create_company_employee(user_e)
            company = employee.company

            # now lets create that custom request
            request = self.create_request(employee)

            # lets create another user, and make them a manager
            manager_user = self.create_user("manager", "manager@company.com", "manager")
            manager_group = self.create_group("SpotLitManager")
            manager_user.groups.add(manager_group)

            # create a analyst to assign it to
            analyst_user = self.create_user("analyst", "analyst@prescient.com", "analyst")
            analyst_group = self.create_group("SpotLitAnalyst")
            analyst_user.groups.add(analyst_group)
            analyst_spotlit_staff = SpotLitStaff(user=analyst_user, phone_number="1234567890", is_activated=True)
            analyst_spotlit_staff.save()

            # create a reviewer
            reviewer_user = self.create_user("reviewer", "reviewer@prescient.com", "reviewer")
            reviewer_group = self.create_group("Reviewer")
            reviewer_user.groups.add(reviewer_group)
            reviewer_spotlit_staff = SpotLitStaff(user=reviewer_user, phone_number="1234567890", is_activated=True)
            reviewer_spotlit_staff.save()


            # assign the request an the analyst and reviewer
            request.assignment = analyst_spotlit_staff
            request.reviewer = reviewer_spotlit_staff
            request.save()


            # next log the manager in
            client = Client()
            url = reverse('login')
            response = client.post(url, {'username': 'manager', 'password': 'manager'}, follow=True)
            self.assertEquals(response.status_code, 200)

            # must have a new status
            status_new = self.create_request_status(request, Status.NEW_STATUS, "2015-04-29 11:59:00")

            # status must be complete to be returned
            status_complete = self.create_request_status(request, Status.COMPLETED_STATUS, "2015-04-29 12:00:00")

            url = reverse('return_reviewer', kwargs={"pk": request.id})
            response = client.post(url, {"comments": "No Comment!"}, follow=True)
            self.assertEquals(response.status_code, 200)

            status = request.get_request_status()

            self.assertEquals(status, Status.REVIEW_STATUS)

    def test_delete_request(self):
        with self.settings(STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage'):
            # we need to create a request, a request must be created by a employee so let's do that 1st
            # create employee...
            user_e = self.create_user("employee", "employee@company.com", "employee")
            group_e = self.create_group("CompanyEmployee")
            user_e.groups.add(group_e)
            employee = self.create_company_employee(user_e)
            company = employee.company

            # now lets create that request
            request = self.create_request(employee)

            # lets create another user, and make them a manager
            manager_user = self.create_user("manager", "manager@company.com", "manager")
            manager_group = self.create_group("SpotLitManager")
            manager_user.groups.add(manager_group)

            # next log the manager in
            client = Client()
            url = reverse('login')
            response = client.post(url, {'username': 'manager', 'password': 'manager'}, follow=True)
            self.assertEquals(response.status_code, 200)
            url = reverse('delete', kwargs={"pk": request.id})

            # only a company employee can delete a request, so if the user is anything else, it should redirect to home
            response = client.post(url, {"comments": "No Comment!"})
            self.assertEquals(response.status_code, 302)

            # next log the employee in
            client = Client()
            url = reverse('login')
            response = client.post(url, {'username': 'employee', 'password': 'employee'}, follow=True)
            self.assertEquals(response.status_code, 200)

            # must have a new status
            status_new = self.create_request_status(request, Status.NEW_STATUS, "2015-04-29 11:59:00")

            # mark request deleted
            url = reverse('delete', kwargs={"pk": request.id})
            response = client.post(url, {"comments": "No Comment!"}, follow=True)

            # the Request must be marked incomplete before it can be deleted, so this should fail
            self.assertEquals(response.content, "Incomplete Failed")

            # now we create an incomplete status
            status_incomplete = self.create_request_status(request, Status.INCOMPLETE_STATUS, "2015-04-29 12:00:00")

            # and try to mark request as deleted.. should work this time.
            url = reverse('delete', kwargs={"pk": request.id})
            response = client.post(url, {"comments": "No Comment!"}, follow=True)
            self.assertEquals(response.content, "Deleted request")
            self.assertEquals(response.status_code, 200)

            # should get back a deleted status now..
            status = request.get_request_status()
            self.assertEquals(status, Status.DELETED_STATUS)

    ###########################
    #
    # Test Corporate Request Actions
    #
    ###########################

    def test_assign_corporate_analyst(self):
        with self.settings(STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage'):
            # we need to create request, a request must be created by a employee so let's do that 1st
            # create employee...
            user_e = self.create_user("employee", "employee@company.com", "employee")
            group_e = self.create_group("CompanyEmployee")
            user_e.groups.add(group_e)
            employee = self.create_company_employee(user_e)
            company = employee.company

            # now lets create that request
            corporate_request = self.create_corporate_request(employee)

            # lets also create a status for this
            status_new = self.create_request_status(corporate_request, Status.NEW_STATUS, "2015-04-29 11:59:00")

            # lets create another user, and make them a manager
            manager_user = self.create_user("manager", "manager@prescient.com", "manager")
            manager_group = self.create_group("SpotLitManager")
            manager_user.groups.add(manager_group)

            # create a analyst to assign it to
            analyst_user = self.create_user("analyst", "analyst@prescient.com", "analyst")
            analyst_group = self.create_group("SpotLitAnalyst")
            analyst_user.groups.add(analyst_group)
            analyst_spotlit_staff = SpotLitStaff(user=analyst_user, phone_number="1234567890", is_activated=True)
            analyst_spotlit_staff.save()

            # create a reviewer to assign it to
            reviewer_user = self.create_user("reviewer", "reviewer@prescient.com", "reviewer")
            reviewer_group = self.create_group("Reviewer")
            reviewer_user.groups.add(reviewer_group)
            reviewer_spotlit_staff = SpotLitStaff(user=reviewer_user, phone_number="1234567890", is_activated=True)
            reviewer_spotlit_staff.save()


            # first lets try to assign this as an employee... we should get a redirect
            client = Client()
            url = reverse('login')
            response = client.post(url, {'username': 'employee', 'password': 'employee'}, follow=True)
            self.assertEquals(response.status_code, 200)

            # assign the request to a analyst
            url = reverse('corporate_assign', kwargs={"pk": corporate_request.id})
            response = client.post(url, {"analyst": analyst_spotlit_staff.id, "comments": "No Comment!"})
            self.assertEquals(response.status_code, 302)

            # next log the manager in
            client = Client()
            url = reverse('login')
            response = client.post(url, {'username': 'manager', 'password': 'manager'}, follow=True)
            self.assertEquals(response.status_code, 200)

            # lets try to assign this when the status is not NEW, it should also redirect
            status_in_progress = self.create_request_status(corporate_request, Status.IN_PROGRESS_STATUS, "2015-04-29 12:00:00")
            url = reverse('corporate_assign', kwargs={"pk": corporate_request.id})
            response = client.post(url, {"analyst": analyst_spotlit_staff.id, "comments": "No Comment!"})
            self.assertEquals(response.status_code, 302)


            # now lets create a New status like it is supposed to be...
            status_new = self.create_request_status(corporate_request, Status.NEW_STATUS, "2015-04-29 12:01:00")


            # assign the request to a fake analyst... this should blow up
            url = reverse('corporate_assign', kwargs={"pk": corporate_request.id})
            response = client.post(url, {"analyst": 99, "comments": "No Comment!"}, follow=True)
            self.assertEquals(response.status_code, 500)

            #finally lets do this right..
            url = reverse('corporate_assign', kwargs={"pk": corporate_request.id})
            response = client.post(url, {"analyst": analyst_spotlit_staff.id, "reviewer": reviewer_spotlit_staff.id, "comments": "No Comment!"}, follow=True)
            self.assertEquals(response.status_code, 200)


            # make sure that it is actually assigned..
            updated_request = CorporateRequest.objects.get(id=corporate_request.id)

            self.assertEquals(corporate_request.get_request_status(), Status.ASSIGNED_STATUS)
            self.assertEquals(analyst_spotlit_staff, updated_request.assignment)

    def test_begin_corporate_request(self):
        with self.settings(STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage'):
            # we need to create request, a request must be created by a employee so let's do that 1st
            # create employee...
            user_e = self.create_user("employee", "employee@company.com", "employee")
            group_e = self.create_group("CompanyEmployee")
            user_e.groups.add(group_e)
            employee = self.create_company_employee(user_e)
            company = employee.company

            # now lets create that request
            corporate_request = self.create_corporate_request(employee)

            # lets also create a status for this
            status_new = self.create_request_status(corporate_request, Status.NEW_STATUS, "2015-04-29 11:59:00")

            # lets create another user, and make them a manager
            manager_user = self.create_user("manager", "manager@prescient.com", "manager")
            manager_group = self.create_group("SpotLitManager")
            manager_user.groups.add(manager_group)

            # create a analyst to assign it to
            analyst_user = self.create_user("analyst", "analyst@prescient.com", "analyst")
            analyst_group = self.create_group("SpotLitAnalyst")
            analyst_user.groups.add(analyst_group)
            analyst_spotlit_staff = SpotLitStaff(user=analyst_user, phone_number="1234567890", is_activated=True)
            analyst_spotlit_staff.save()

            # assign the request an the analyst
            corporate_request.assignment = analyst_spotlit_staff
            corporate_request.save()

            # give the request an assigned status
            status_assigned = self.create_request_status(corporate_request, Status.ASSIGNED_STATUS, "2015-04-29 12:00:00")

            self.assertEquals(corporate_request.assignment, analyst_spotlit_staff)

            # next lets try to begin this request as a manager... this should redirect
            client = Client()
            url = reverse('login')
            response = client.post(url, {'username': 'manager', 'password': 'manager'}, follow=True)
            self.assertEquals(response.status_code, 200)
            # begin the request
            url = reverse('corporate_begin', kwargs={"pk": corporate_request.id})
            response = client.get(url)
            self.assertEquals(response.status_code, 302)

            # next lets log the analyst in...
            client = Client()
            url = reverse('login')
            response = client.post(url, {'username': 'analyst', 'password': 'analyst'}, follow=True)
            self.assertEquals(response.status_code, 200)

            # lets try to begin the request when it is not in assigned status.. this should also redirect
            status_new = self.create_request_status(corporate_request, Status.NEW_STATUS, "2015-04-29 12:01:00")

            # begin the request
            url = reverse('corporate_begin', kwargs={"pk": corporate_request.id})
            response = client.get(url)
            self.assertEquals(response.status_code, 302)

            # now lets try with a assigned status.. this should work
            status_assigned = self.create_request_status(corporate_request, Status.ASSIGNED_STATUS, "2015-04-29 12:02:00")

            # begin the request
            url = reverse('corporate_begin', kwargs={"pk": corporate_request.id})
            response = client.get(url, follow=True)
            self.assertEquals(response.status_code, 200)


            # test that the status is in progress
            current_status = corporate_request.get_request_status()
            self.assertEquals(current_status, Status.IN_PROGRESS_STATUS)

    def test_reject_corporate_request(self):
        with self.settings(STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage'):
            # we need to create request, a request must be created by a employee so let's do that 1st
            # create employee...
            user_e = self.create_user("employee", "employee@company.com", "employee")
            group_e = self.create_group("CompanyEmployee")
            user_e.groups.add(group_e)
            employee = self.create_company_employee(user_e)
            company = employee.company

            # now lets create that request
            corporate_request = self.create_corporate_request(employee)

            # lets also create a status for this
            status_new = self.create_request_status(corporate_request, Status.NEW_STATUS, "2015-04-29 11:59:00")

            # lets create another user, and make them a manager
            manager_user = self.create_user("manager", "manager@prescient.com", "manager")
            manager_group = self.create_group("SpotLitManager")
            manager_user.groups.add(manager_group)

            # create a analyst to assign it to
            analyst_user = self.create_user("analyst", "analyst@prescient.com", "analyst")
            analyst_group = self.create_group("SpotLitAnalyst")
            analyst_user.groups.add(analyst_group)
            analyst_spotlit_staff = SpotLitStaff(user=analyst_user, phone_number="1234567890", is_activated=True)
            analyst_spotlit_staff.save()

            # assign the request an the analyst
            corporate_request.assignment = analyst_spotlit_staff
            corporate_request.save()
            self.assertEquals(corporate_request.assignment, analyst_spotlit_staff)

            # give the request an assigned status
            status_assigned = self.create_request_status(corporate_request, Status.ASSIGNED_STATUS, "2015-04-29 12:00:00")


            # lets try to reject this request as a employee.. it should redirect..
            client = Client()
            url = reverse('login')
            response = client.post(url, {'username': "employee", 'password':"employee"}, follow=True)
            self.assertEquals(response.status_code, 200)

            # reject the request
            url = reverse('corporate_reject', kwargs={"pk": corporate_request.id})
            response = client.post(url, {'comments': "No Comment!"})
            self.assertEquals(response.status_code, 302)

            # next lets log the analyst in...
            client = Client()
            url = reverse('login')
            response = client.post(url, {'username': 'analyst', 'password': 'analyst'}, follow=True)
            self.assertEquals(response.status_code, 200)

            # lets try to reject the request when it is not in progress, or assigned
            status_new = self.create_request_status(corporate_request, Status.NEW_STATUS, "2015-04-29 12:01:00")

            # reject the request.. this should redirect.
            url = reverse('corporate_reject', kwargs={"pk": corporate_request.id})
            response = client.post(url, {'comments': "No Comment!"})
            self.assertEquals(response.content, "Rejection Failed")

            # now lets to it when it's assigned...
            status_assigned = self.create_request_status(corporate_request, Status.ASSIGNED_STATUS, "2015-04-29 12:02:00")

            # now lets reject it... with a get.. it should fail
            url = reverse('corporate_reject', kwargs={"pk": corporate_request.id})
            response = client.get(url)
            self.assertEquals(response.content, "Rejection Failed")

            # finnally the way it should be.. this should work
            url = reverse('corporate_reject', kwargs={"pk": corporate_request.id})
            response = client.post(url, {'comments': "No Comment!"}, follow=True)
            self.assertEquals(response.status_code, 200)

            # test that the status is rejected
            current_status = corporate_request.get_request_status()
            self.assertEquals(current_status, Status.REJECTED_STATUS)

    def test_incomplete_corporate_request(self):
        with self.settings(STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage'):
            # we need to create request, a request must be created by a employee so let's do that 1st
            # create employee...
            user_e = self.create_user("employee", "employee@company.com", "employee")
            group_e = self.create_group("CompanyEmployee")
            user_e.groups.add(group_e)
            employee = self.create_company_employee(user_e)
            company = employee.company

            # now lets create that request
            corporate_request = self.create_corporate_request(employee)

            # lets also create a status for this
            status_new = self.create_request_status(corporate_request, Status.NEW_STATUS, "2015-04-29 11:59:00")

            # lets create another user, and make them a manager
            manager_user = self.create_user("manager", "manager@prescient.com", "manager")
            manager_group = self.create_group("SpotLitManager")
            manager_user.groups.add(manager_group)

            # create a analyst to assign it to
            analyst_user = self.create_user("analyst", "analyst@prescient.com", "analyst")
            analyst_group = self.create_group("SpotLitAnalyst")
            analyst_user.groups.add(analyst_group)
            analyst_spotlit_staff = SpotLitStaff(user=analyst_user, phone_number="1234567890", is_activated=True)
            analyst_spotlit_staff.save()

            # assign the request an the analyst
            corporate_request.assignment = analyst_spotlit_staff
            corporate_request.save()

            # give the request an assigned status
            status_assigned = self.create_request_status(corporate_request, Status.ASSIGNED_STATUS, "2015-04-29 12:00:00")

            self.assertEquals(corporate_request.assignment, analyst_spotlit_staff)

            # next lets log the employee in to mark it incomplete.. this should redirect.
            client = Client()
            url = reverse('login')
            response = client.post(url, {'username': 'employee', 'password': 'employee'}, follow=True)
            self.assertEquals(response.status_code, 200)

            url = reverse('corporate_incomplete', kwargs={'pk': corporate_request.id})
            response = client.post(url, {'comments': "No Comment!"})
            self.assertEquals(response.status_code, 302)

            # next lets log the manager in...
            client = Client()
            url = reverse('login')
            response = client.post(url, {'username': 'manager', 'password': 'manager'}, follow=True)
            self.assertEquals(response.status_code, 200)

            # next create a submitted status, you shouldn't be able to incomplete a submitted status..
            status_submitted = self.create_request_status(corporate_request, Status.SUBMITTED_STATUS, "2015-04-29 12:01:00")

            url = reverse('corporate_incomplete', kwargs={'pk': corporate_request.id})
            response = client.post(url, {'comments': "No Comment!"}, follow=True)
            self.assertEquals(response.status_code, 200)
            self.assertEquals(response.content, "Incomplete Failed")

            status_new = self.create_request_status(corporate_request, Status.NEW_STATUS, "2015-04-29 12:02:00")
            response = client.get(url)
            self.assertEquals(response.content, "Incomplete failed")

            # this one should work.
            response = client.post(url, {'comments': "No Comment!"}, follow=True)
            self.assertEquals(response.status_code, 200)

            # make sure the status was marked incomplete...
            current_status = corporate_request.get_request_status()
            self.assertEquals(current_status, Status.INCOMPLETE_STATUS)

    def test_submit_corporate_request(self):
        with self.settings(STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage'):
            # we need to create a corporate request, a corporate request must be created by a employee so let's do that 1st
            # create employee...
            user_e = self.create_user("employee", "employee@company.com", "employee")
            group_e = self.create_group("CompanyEmployee")
            user_e.groups.add(group_e)
            employee = self.create_etrade_company_employee(user_e)
            company = employee.company

            # now lets create a corporate request
            corporate_request = self.create_corporate_request(employee)

            # lets create another user, and make them a manager
            manager_user = self.create_user("manager", "manager@company.com", "manager")
            manager_group = self.create_group("SpotLitManager")
            manager_user.groups.add(manager_group)

            # next log the manager in
            client = Client()
            url = reverse('login')
            response = client.post(url, {'username': 'manager', 'password': 'manager'}, follow=True)
            self.assertEquals(response.status_code, 200)

            # must have a new status
            status_new = self.create_request_status(corporate_request, Status.NEW_STATUS, "2015-04-29 11:59:00")

            # status must be complete to be submitted
            status_complete = self.create_request_status(corporate_request, Status.COMPLETED_STATUS, "2015-04-29 12:00:00")

            url = reverse('corporate_submit', kwargs={"pk": corporate_request.id})
            response = client.post(url, {"comments": "No Comment!"}, follow=True)
            self.assertEquals(response.status_code, 200)

            status = corporate_request.get_request_status()
            self.assertEquals(status, Status.SUBMITTED_STATUS)

    def test_return_corporate_request(self):
        with self.settings(STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage'):
            # we need to create a request, a request must be created by a employee so let's do that 1st
            # create employee...
            user_e = self.create_user("employee", "employee@company.com", "employee")
            group_e = self.create_group("CompanyEmployee")
            user_e.groups.add(group_e)
            employee = self.create_company_employee(user_e)
            company = employee.company

            # now lets create that custom request
            corporate_request = self.create_corporate_request(employee)

            # lets create another user, and make them a manager
            manager_user = self.create_user("manager", "manager@company.com", "manager")
            manager_group = self.create_group("SpotLitManager")
            manager_user.groups.add(manager_group)

             # create a analyst to assign it to
            analyst_user = self.create_user("analyst", "analyst@prescient.com", "analyst")
            analyst_group = self.create_group("SpotLitAnalyst")
            analyst_user.groups.add(analyst_group)
            analyst_spotlit_staff = SpotLitStaff(user=analyst_user, phone_number="1234567890", is_activated=True)
            analyst_spotlit_staff.save()

            # assign the request an the analyst
            corporate_request.assignment = analyst_spotlit_staff
            corporate_request.save()


            # next log the manager in
            client = Client()
            url = reverse('login')
            response = client.post(url, {'username': 'manager', 'password': 'manager'}, follow=True)
            self.assertEquals(response.status_code, 200)

            # must have a new status
            status_new = self.create_request_status(corporate_request, Status.NEW_STATUS, "2015-04-29 11:59:00")

            # status must be complete to be returned
            status_complete = self.create_request_status(corporate_request, Status.COMPLETED_STATUS, "2015-04-29 12:00:00")

            url = reverse('corporate_return', kwargs={"pk": corporate_request.id})
            response = client.post(url, {"comments": "No Comment!"}, follow=True)
            self.assertEquals(response.status_code, 200)

            status = corporate_request.get_request_status()

            self.assertEquals(status, Status.NEW_RETURNED_STATUS)

    def test_return_corporate_request_reviewer(self):
        with self.settings(STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage'):
            # we need to create a request, a request must be created by a employee so let's do that 1st
            # create employee...
            user_e = self.create_user("employee", "employee@company.com", "employee")
            group_e = self.create_group("CompanyEmployee")
            user_e.groups.add(group_e)
            employee = self.create_company_employee(user_e)
            company = employee.company

            # now lets create that corporate request
            corporate_request = self.create_corporate_request(employee)

            # lets create another user, and make them a manager
            manager_user = self.create_user("manager", "manager@company.com", "manager")
            manager_group = self.create_group("SpotLitManager")
            manager_user.groups.add(manager_group)

            # create a analyst to assign it to
            analyst_user = self.create_user("analyst", "analyst@prescient.com", "analyst")
            analyst_group = self.create_group("SpotLitAnalyst")
            analyst_user.groups.add(analyst_group)
            analyst_spotlit_staff = SpotLitStaff(user=analyst_user, phone_number="1234567890", is_activated=True)
            analyst_spotlit_staff.save()

            # create a reviewer
            reviewer_user = self.create_user("reviewer", "reviewer@prescient.com", "reviewer")
            reviewer_group = self.create_group("Reviewer")
            reviewer_user.groups.add(reviewer_group)
            reviewer_spotlit_staff = SpotLitStaff(user=reviewer_user, phone_number="1234567890", is_activated=True)
            reviewer_spotlit_staff.save()


            # assign the request an the analyst and reviewer
            corporate_request.assignment = analyst_spotlit_staff
            corporate_request.reviewer = reviewer_spotlit_staff
            corporate_request.save()


            # next log the manager in
            client = Client()
            url = reverse('login')
            response = client.post(url, {'username': 'manager', 'password': 'manager'}, follow=True)
            self.assertEquals(response.status_code, 200)

            # must have a new status
            status_new = self.create_request_status(corporate_request, Status.NEW_STATUS, "2015-04-29 11:59:00")

            # status must be complete to be returned
            status_complete = self.create_request_status(corporate_request, Status.COMPLETED_STATUS, "2015-04-29 12:00:00")

            url = reverse('corporate_return_reviewer', kwargs={"pk": corporate_request.id})
            response = client.post(url, {"comments": "No Comment!"}, follow=True)
            self.assertEquals(response.status_code, 200)

            status = corporate_request.get_request_status()

            self.assertEquals(status, Status.REVIEW_STATUS)

    def test_delete_corporate_request(self):
        with self.settings(STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage'):
            # we need to create a corporate, a request must be created by a employee so let's do that 1st
            # create employee...
            user_e = self.create_user("employee", "employee@company.com", "employee")
            group_e = self.create_group("CompanyEmployee")
            user_e.groups.add(group_e)
            employee = self.create_company_employee(user_e)
            company = employee.company

            # now lets create that corporate request
            corporate_request = self.create_corporate_request(employee)

            # lets create another user, and make them a manager
            manager_user = self.create_user("manager", "manager@company.com", "manager")
            manager_group = self.create_group("SpotLitManager")
            manager_user.groups.add(manager_group)

            # next log the manager in
            client = Client()
            url = reverse('login')
            response = client.post(url, {'username': 'manager', 'password': 'manager'}, follow=True)
            self.assertEquals(response.status_code, 200)
            url = reverse('corporate_delete', kwargs={"pk": corporate_request.id})

            # only a company employee can delete a request, so if the user is anything else, it should redirect to home
            response = client.post(url, {"comments": "No Comment!"})
            self.assertEquals(response.status_code, 302)

            # next log the employee in
            client = Client()
            url = reverse('login')
            response = client.post(url, {'username': 'employee', 'password': 'employee'}, follow=True)
            self.assertEquals(response.status_code, 200)

            # must have a new status
            status_new = self.create_request_status(corporate_request, Status.NEW_STATUS, "2015-04-29 11:59:00")

            # mark request deleted
            url = reverse('corporate_delete', kwargs={"pk": corporate_request.id})
            response = client.post(url, {"comments": "No Comment!"}, follow=True)

            # the Request must be marked incomplete before it can be deleted, so this should fail
            self.assertEquals(response.content, "Incomplete Failed")

            # now we create an incomplete status
            status_incomplete = self.create_request_status(corporate_request, Status.INCOMPLETE_STATUS, "2015-04-29 12:00:00")

            # and try to mark request as deleted.. should work this time.
            url = reverse('corporate_delete', kwargs={"pk": corporate_request.id})
            response = client.post(url, {"comments": "No Comment!"}, follow=True)
            self.assertEquals(response.content, "Deleted request")
            self.assertEquals(response.status_code, 200)

            # should get back a deleted status now..
            status = corporate_request.get_request_status()
            self.assertEquals(status, Status.DELETED_STATUS)

    ###########################
    #
    # Test Custom Request Actions
    #
    ###########################

    def test_assign_custom_analyst(self):
        with self.settings(STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage'):
            # we need to create request, a request must be created by a employee so let's do that 1st
            # create employee...
            user_e = self.create_user("employee", "employee@company.com", "employee")
            group_e = self.create_group("CompanyEmployee")
            user_e.groups.add(group_e)
            employee = self.create_company_employee(user_e)
            company = employee.company

            # now lets create that request
            custom_request = self.create_custom_request(employee)

            # lets also create a status for this
            status_new = self.create_request_status(custom_request, Status.NEW_STATUS, "2015-04-29 11:59:00")

            # lets create another user, and make them a manager
            manager_user = self.create_user("manager", "manager@prescient.com", "manager")
            manager_group = self.create_group("SpotLitManager")
            manager_user.groups.add(manager_group)

            # create a analyst to assign it to
            analyst_user = self.create_user("analyst", "analyst@prescient.com", "analyst")
            analyst_group = self.create_group("SpotLitAnalyst")
            analyst_user.groups.add(analyst_group)
            analyst_spotlit_staff = SpotLitStaff(user=analyst_user, phone_number="1234567890", is_activated=True)
            analyst_spotlit_staff.save()

            # create a reviewer to assign it to
            reviewer_user = self.create_user("reviewer", "reviewer@prescient.com", "reviewer")
            reviewer_group = self.create_group("Reviewer")
            reviewer_user.groups.add(reviewer_group)
            reviewer_spotlit_staff = SpotLitStaff(user=reviewer_user, phone_number="1234567890", is_activated=True)
            reviewer_spotlit_staff.save()


            # first lets try to assign this as an employee... we should get a redirect
            client = Client()
            url = reverse('login')
            response = client.post(url, {'username': 'employee', 'password': 'employee'}, follow=True)
            self.assertEquals(response.status_code, 200)

            # assign the request to a analyst
            url = reverse('custom_assign', kwargs={"pk": custom_request.id})
            response = client.post(url, {"analyst": analyst_spotlit_staff.id, "comments": "No Comment!"})
            self.assertEquals(response.status_code, 302)

            # next log the manager in
            client = Client()
            url = reverse('login')
            response = client.post(url, {'username': 'manager', 'password': 'manager'}, follow=True)
            self.assertEquals(response.status_code, 200)

            # lets try to assign this when the status is not NEW, it should also redirect
            status_in_progress = self.create_request_status(custom_request, Status.IN_PROGRESS_STATUS, "2015-04-29 12:00:00")
            url = reverse('custom_assign', kwargs={"pk": custom_request.id})
            response = client.post(url, {"analyst": analyst_spotlit_staff.id, "comments": "No Comment!"})
            self.assertEquals(response.status_code, 302)


            # now lets create a New status like it is supposed to be...
            status_new = self.create_request_status(custom_request, Status.NEW_STATUS, "2015-04-29 12:01:00")


            # assign the request to a fake analyst... this should blow up
            url = reverse('custom_assign', kwargs={"pk": custom_request.id})
            response = client.post(url, {"analyst": 99, "comments": "No Comment!"}, follow=True)
            self.assertEquals(response.status_code, 500)

            #finally lets do this right..
            url = reverse('custom_assign', kwargs={"pk": custom_request.id})
            response = client.post(url, {"analyst": analyst_spotlit_staff.id, "reviewer": reviewer_spotlit_staff.id, "comments": "No Comment!"}, follow=True)
            self.assertEquals(response.status_code, 200)


            # make sure that it is actually assigned..
            updated_request = CustomRequest.objects.get(id=custom_request.id)

            self.assertEquals(custom_request.get_request_status(), Status.ASSIGNED_STATUS)
            self.assertEquals(analyst_spotlit_staff, updated_request.assignment)

    def test_begin_custom_request(self):
        with self.settings(STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage'):
            # we need to create request, a request must be created by a employee so let's do that 1st
            # create employee...
            user_e = self.create_user("employee", "employee@company.com", "employee")
            group_e = self.create_group("CompanyEmployee")
            user_e.groups.add(group_e)
            employee = self.create_company_employee(user_e)
            company = employee.company

            # now lets create that request
            custom_request = self.create_custom_request(employee)

            # lets also create a status for this
            status_new = self.create_request_status(custom_request, Status.NEW_STATUS, "2015-04-29 11:59:00")

            # lets create another user, and make them a manager
            manager_user = self.create_user("manager", "manager@prescient.com", "manager")
            manager_group = self.create_group("SpotLitManager")
            manager_user.groups.add(manager_group)

            # create a analyst to assign it to
            analyst_user = self.create_user("analyst", "analyst@prescient.com", "analyst")
            analyst_group = self.create_group("SpotLitAnalyst")
            analyst_user.groups.add(analyst_group)
            analyst_spotlit_staff = SpotLitStaff(user=analyst_user, phone_number="1234567890", is_activated=True)
            analyst_spotlit_staff.save()

            # assign the request an the analyst
            custom_request.assignment = analyst_spotlit_staff
            custom_request.save()

            # give the request an assigned status
            status_assigned = self.create_request_status(custom_request, Status.ASSIGNED_STATUS, "2015-04-29 12:00:00")

            self.assertEquals(custom_request.assignment, analyst_spotlit_staff)

            # next lets try to begin this request as a manager... this should redirect
            client = Client()
            url = reverse('login')
            response = client.post(url, {'username': 'manager', 'password': 'manager'}, follow=True)
            self.assertEquals(response.status_code, 200)
            # begin the request
            url = reverse('custom_begin', kwargs={"pk": custom_request.id})
            response = client.get(url)
            self.assertEquals(response.status_code, 302)

            # next lets log the analyst in...
            client = Client()
            url = reverse('login')
            response = client.post(url, {'username': 'analyst', 'password': 'analyst'}, follow=True)
            self.assertEquals(response.status_code, 200)

            # lets try to begin the request when it is not in assigned status.. this should also redirect
            status_new = self.create_request_status(custom_request, Status.NEW_STATUS, "2015-04-29 12:01:00")

            # begin the request
            url = reverse('custom_begin', kwargs={"pk": custom_request.id})
            response = client.get(url)
            self.assertEquals(response.status_code, 302)

            # now lets try with a assigned status.. this should work
            status_assigned = self.create_request_status(custom_request, Status.ASSIGNED_STATUS, "2015-04-29 12:02:00")

            # begin the request
            url = reverse('custom_begin', kwargs={"pk": custom_request.id})
            response = client.get(url, follow=True)
            self.assertEquals(response.status_code, 200)


            # test that the status is in progress
            current_status = custom_request.get_request_status()
            self.assertEquals(current_status, Status.IN_PROGRESS_STATUS)

    def test_reject_custom_request(self):
        with self.settings(STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage'):
            # we need to create request, a request must be created by a employee so let's do that 1st
            # create employee...
            user_e = self.create_user("employee", "employee@company.com", "employee")
            group_e = self.create_group("CompanyEmployee")
            user_e.groups.add(group_e)
            employee = self.create_company_employee(user_e)
            company = employee.company

            # now lets create that request
            custom_request = self.create_custom_request(employee)

            # lets also create a status for this
            status_new = self.create_request_status(custom_request, Status.NEW_STATUS, "2015-04-29 11:59:00")

            # lets create another user, and make them a manager
            manager_user = self.create_user("manager", "manager@prescient.com", "manager")
            manager_group = self.create_group("SpotLitManager")
            manager_user.groups.add(manager_group)

            # create a analyst to assign it to
            analyst_user = self.create_user("analyst", "analyst@prescient.com", "analyst")
            analyst_group = self.create_group("SpotLitAnalyst")
            analyst_user.groups.add(analyst_group)
            analyst_spotlit_staff = SpotLitStaff(user=analyst_user, phone_number="1234567890", is_activated=True)
            analyst_spotlit_staff.save()

            # assign the request an the analyst
            custom_request.assignment = analyst_spotlit_staff
            custom_request.save()
            self.assertEquals(custom_request.assignment, analyst_spotlit_staff)

            # give the request an assigned status
            status_assigned = self.create_request_status(custom_request, Status.ASSIGNED_STATUS, "2015-04-29 12:00:00")


            # lets try to reject this request as a employee.. it should redirect..
            client = Client()
            url = reverse('login')
            response = client.post(url, {'username': "employee", 'password':"employee"}, follow=True)
            self.assertEquals(response.status_code, 200)

            # reject the request
            url = reverse('custom_reject', kwargs={"pk": custom_request.id})
            response = client.post(url, {'comments': "No Comment!"})
            self.assertEquals(response.status_code, 302)

            # next lets log the analyst in...
            client = Client()
            url = reverse('login')
            response = client.post(url, {'username': 'analyst', 'password': 'analyst'}, follow=True)
            self.assertEquals(response.status_code, 200)

            # lets try to reject the request when it is not in progress, or assigned
            status_new = self.create_request_status(custom_request, Status.NEW_STATUS, "2015-04-29 12:01:00")

            # reject the request.. this should redirect.
            url = reverse('custom_reject', kwargs={"pk": custom_request.id})
            response = client.post(url, {'comments': "No Comment!"})
            self.assertEquals(response.content, "Rejection Failed")

            # now lets to it when it's assigned...
            status_assigned = self.create_request_status(custom_request, Status.ASSIGNED_STATUS, "2015-04-29 12:02:00")

            # now lets reject it... with a get.. it should fail
            url = reverse('custom_reject', kwargs={"pk": custom_request.id})
            response = client.get(url)
            self.assertEquals(response.content, "Rejection Failed")

            # finnally the way it should be.. this should work
            url = reverse('custom_reject', kwargs={"pk": custom_request.id})
            response = client.post(url, {'comments': "No Comment!"}, follow=True)
            self.assertEquals(response.status_code, 200)

            # test that the status is rejected
            current_status = custom_request.get_request_status()
            self.assertEquals(current_status, Status.REJECTED_STATUS)

    def test_incomplete_custom_request(self):
        with self.settings(STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage'):
            # we need to create request, a request must be created by a employee so let's do that 1st
            # create employee...
            user_e = self.create_user("employee", "employee@company.com", "employee")
            group_e = self.create_group("CompanyEmployee")
            user_e.groups.add(group_e)
            employee = self.create_company_employee(user_e)
            company = employee.company

            # now lets create that request
            custom_request = self.create_custom_request(employee)

            # lets also create a status for this
            status_new = self.create_request_status(custom_request, Status.NEW_STATUS, "2015-04-29 11:59:00")

            # lets create another user, and make them a manager
            manager_user = self.create_user("manager", "manager@prescient.com", "manager")
            manager_group = self.create_group("SpotLitManager")
            manager_user.groups.add(manager_group)

            # create a analyst to assign it to
            analyst_user = self.create_user("analyst", "analyst@prescient.com", "analyst")
            analyst_group = self.create_group("SpotLitAnalyst")
            analyst_user.groups.add(analyst_group)
            analyst_spotlit_staff = SpotLitStaff(user=analyst_user, phone_number="1234567890", is_activated=True)
            analyst_spotlit_staff.save()

            # assign the request an the analyst
            custom_request.assignment = analyst_spotlit_staff
            custom_request.save()

            # give the request an assigned status
            status_assigned = self.create_request_status(custom_request, Status.ASSIGNED_STATUS, "2015-04-29 12:00:00")

            self.assertEquals(custom_request.assignment, analyst_spotlit_staff)

            # next lets log the employee in to mark it incomplete.. this should redirect.
            client = Client()
            url = reverse('login')
            response = client.post(url, {'username': 'employee', 'password': 'employee'}, follow=True)
            self.assertEquals(response.status_code, 200)

            url = reverse('custom_incomplete', kwargs={'pk': custom_request.id})
            response = client.post(url, {'comments': "No Comment!"})
            self.assertEquals(response.status_code, 302)

            # next lets log the manager in...
            client = Client()
            url = reverse('login')
            response = client.post(url, {'username': 'manager', 'password': 'manager'}, follow=True)
            self.assertEquals(response.status_code, 200)

            # next create a submitted status, you shouldn't be able to incomplete a submitted status..
            status_submitted = self.create_request_status(custom_request, Status.SUBMITTED_STATUS, "2015-04-29 12:01:00")

            url = reverse('custom_incomplete', kwargs={'pk': custom_request.id})
            response = client.post(url, {'comments': "No Comment!"}, follow=True)
            self.assertEquals(response.status_code, 200)
            self.assertEquals(response.content, "Incomplete Failed")

            status_new = self.create_request_status(custom_request, Status.NEW_STATUS, "2015-04-29 12:02:00")
            response = client.get(url)
            self.assertEquals(response.content, "Incomplete failed")

            # this one should work.
            response = client.post(url, {'comments': "No Comment!"}, follow=True)
            self.assertEquals(response.status_code, 200)

            # make sure the status was marked incomplete...
            current_status = custom_request.get_request_status()
            self.assertEquals(current_status, Status.INCOMPLETE_STATUS)

    def test_submit_custom_request(self):
        with self.settings(STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage'):
            # we need to create a custom request, a custom request must be created by a employee so let's do that 1st
            # create employee...
            user_e = self.create_user("employee", "employee@company.com", "employee")
            group_e = self.create_group("CompanyEmployee")
            user_e.groups.add(group_e)
            employee = self.create_etrade_company_employee(user_e)
            company = employee.company

            # now lets create that custom request
            custom_request = self.create_custom_request(employee)

            # lets create another user, and make them a manager
            manager_user = self.create_user("manager", "manager@company.com", "manager")
            manager_group = self.create_group("SpotLitManager")
            manager_user.groups.add(manager_group)

            # next log the employee in, they shouldn't be able to submit so it should redirect..
            client = Client()
            url = reverse('login')
            response = client.post(url, {'username': 'employee', 'password': 'employee'}, follow=True)
            self.assertEquals(response.status_code, 200)

            url = reverse('custom_submit', kwargs={"pk": custom_request.id})
            response = client.post(url, {"comments": "No Comment!", "reporting_period": "October 2015"})
            self.assertEquals(response.status_code, 302)

            # try to submit before it's completed.. this should fail..
            status_new = self.create_request_status(custom_request, Status.NEW_STATUS, "2015-04-29 11:59:00")

            url = reverse('login')
            response = client.post(url, {'username': 'manager', 'password': 'manager'}, follow=True)
            self.assertEquals(response.status_code, 200)

            # try to submit before it's completed.. this should fail..
            url = reverse('custom_submit', kwargs={"pk": custom_request.id})
            response = client.post(url, {"comments": "No Comment!", "reporting_period": "October 2015"}, follow=True)
            self.assertEquals(response.content, "Submit Failed")

            # status must be complete to be submitted
            status_complete = self.create_request_status(custom_request, Status.COMPLETED_STATUS, "2015-04-29 12:00:00")

            # lets try a get.. this should fail
            response = client.get(url)
            self.assertEquals(response.content, "Submit failed")

            # this one should work
            url = reverse('custom_submit', kwargs={"pk": custom_request.id})
            response = client.post(url, {"comments": "No Comment!", "reporting_period": "October 2015"}, follow=True)
            self.assertEquals(response.status_code, 200)

            status = custom_request.get_request_status()

            self.assertEquals(status, Status.SUBMITTED_STATUS)

    def test_return_custom_request(self):
        with self.settings(STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage'):
            # we need to create a request, a request must be created by a employee so let's do that 1st
            # create employee...
            user_e = self.create_user("employee", "employee@company.com", "employee")
            group_e = self.create_group("CompanyEmployee")
            user_e.groups.add(group_e)
            employee = self.create_company_employee(user_e)
            company = employee.company

            # now lets create that custom request
            custom_request = self.create_custom_request(employee)

            # lets create another user, and make them a manager
            manager_user = self.create_user("manager", "manager@company.com", "manager")
            manager_group = self.create_group("SpotLitManager")
            manager_user.groups.add(manager_group)

             # create a analyst to assign it to
            analyst_user = self.create_user("analyst", "analyst@prescient.com", "analyst")
            analyst_group = self.create_group("SpotLitAnalyst")
            analyst_user.groups.add(analyst_group)
            analyst_spotlit_staff = SpotLitStaff(user=analyst_user, phone_number="1234567890", is_activated=True)
            analyst_spotlit_staff.save()

            # assign the request an the analyst
            custom_request.assignment = analyst_spotlit_staff
            custom_request.save()


            # next log the manager in
            client = Client()
            url = reverse('login')
            response = client.post(url, {'username': 'manager', 'password': 'manager'}, follow=True)
            self.assertEquals(response.status_code, 200)

            # must have a new status
            status_new = self.create_request_status(custom_request, Status.NEW_STATUS, "2015-04-29 11:59:00")

            # status must be complete to be returned
            status_complete = self.create_request_status(custom_request, Status.COMPLETED_STATUS, "2015-04-29 12:00:00")

            url = reverse('custom_return', kwargs={"pk": custom_request.id})
            response = client.post(url, {"comments": "No Comment!"}, follow=True)
            self.assertEquals(response.status_code, 200)

            status = custom_request.get_request_status()

            self.assertEquals(status, Status.NEW_RETURNED_STATUS)

    def test_delete_custom_request(self):
        with self.settings(STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage'):
            # we need to create a custom request, a request must be created by a employee so let's do that 1st
            # create employee...
            user_e = self.create_user("employee", "employee@company.com", "employee")
            group_e = self.create_group("CompanyEmployee")
            user_e.groups.add(group_e)
            employee = self.create_company_employee(user_e)
            company = employee.company

            # now lets create that custom request
            custom_request = self.create_custom_request(employee)

            # lets create another user, and make them a manager
            manager_user = self.create_user("manager", "manager@company.com", "manager")
            manager_group = self.create_group("SpotLitManager")
            manager_user.groups.add(manager_group)

            # next log the manager in
            client = Client()
            url = reverse('login')
            response = client.post(url, {'username': 'manager', 'password': 'manager'}, follow=True)
            self.assertEquals(response.status_code, 200)
            url = reverse('custom_delete', kwargs={"pk": custom_request.id})

            # only a company employee can delete a request, so if the user is anything else, it should redirect to home
            response = client.post(url, {"comments": "No Comment!"})
            self.assertEquals(response.status_code, 302)

            # next log the employee in
            client = Client()
            url = reverse('login')
            response = client.post(url, {'username': 'employee', 'password': 'employee'}, follow=True)
            self.assertEquals(response.status_code, 200)

            # must have a new status
            status_new = self.create_request_status(custom_request, Status.NEW_STATUS, "2015-04-29 11:59:00")

            # mark request deleted
            url = reverse('custom_delete', kwargs={"pk": custom_request.id})
            response = client.post(url, {"comments": "No Comment!"}, follow=True)

            # the Request must be marked incomplete before it can be deleted, so this should fail
            self.assertEquals(response.content, "Delete Failed")

            # now we create an incomplete status
            status_incomplete = self.create_request_status(custom_request, Status.INCOMPLETE_STATUS, "2015-04-29 12:00:00")

            # and try to mark request as deleted.. should work this time.
            url = reverse('custom_delete', kwargs={"pk": custom_request.id})
            response = client.post(url, {"comments": "No Comment!"}, follow=True)
            self.assertEquals(response.content, "Deleted custom request")
            self.assertEquals(response.status_code, 200)

            # should get back a deleted status now..
            status = custom_request.get_request_status()
            self.assertEquals(status, Status.DELETED_STATUS)

    def test_return_custom_request_reviewer(self):
        with self.settings(STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage'):
            # we need to create a request, a request must be created by a employee so let's do that 1st
            # create employee...
            user_e = self.create_user("employee", "employee@company.com", "employee")
            group_e = self.create_group("CompanyEmployee")
            user_e.groups.add(group_e)
            employee = self.create_company_employee(user_e)
            company = employee.company

            # now lets create that custom request
            custom_request = self.create_custom_request(employee)

            # lets create another user, and make them a manager
            manager_user = self.create_user("manager", "manager@company.com", "manager")
            manager_group = self.create_group("SpotLitManager")
            manager_user.groups.add(manager_group)

            # create a analyst to assign it to
            analyst_user = self.create_user("analyst", "analyst@prescient.com", "analyst")
            analyst_group = self.create_group("SpotLitAnalyst")
            analyst_user.groups.add(analyst_group)
            analyst_spotlit_staff = SpotLitStaff(user=analyst_user, phone_number="1234567890", is_activated=True)
            analyst_spotlit_staff.save()

            # create a reviewer
            reviewer_user = self.create_user("reviewer", "reviewer@prescient.com", "reviewer")
            reviewer_group = self.create_group("Reviewer")
            reviewer_user.groups.add(reviewer_group)
            reviewer_spotlit_staff = SpotLitStaff(user=reviewer_user, phone_number="1234567890", is_activated=True)
            reviewer_spotlit_staff.save()


            # assign the request an the analyst and reviewer
            custom_request.assignment = analyst_spotlit_staff
            custom_request.reviewer = reviewer_spotlit_staff
            custom_request.save()


            # next log the manager in
            client = Client()
            url = reverse('login')
            response = client.post(url, {'username': 'manager', 'password': 'manager'}, follow=True)
            self.assertEquals(response.status_code, 200)

            # must have a new status
            status_new = self.create_request_status(custom_request, Status.NEW_STATUS, "2015-04-29 11:59:00")

            # status must be complete to be returned
            status_complete = self.create_request_status(custom_request, Status.COMPLETED_STATUS, "2015-04-29 12:00:00")

            url = reverse('custom_return_reviewer', kwargs={"pk": custom_request.id})
            response = client.post(url, {"comments": "No Comment!"}, follow=True)
            self.assertEquals(response.status_code, 200)

            status = custom_request.get_request_status()

            self.assertEquals(status, Status.REVIEW_STATUS)




