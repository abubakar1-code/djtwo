from __future__ import absolute_import

from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404, render_to_response
from django.views import generic
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import password_reset, password_reset_confirm
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse_lazy, reverse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from functools import partial, wraps
from django.forms.formsets import formset_factory
from django.forms import modelformset_factory
from django.http import HttpResponseServerError, HttpResponse, HttpResponseRedirect, HttpResponseForbidden, JsonResponse, request
from django.core import serializers
from django.core.paginator import Paginator
from django.template import RequestContext
from pytz import timezone
from django.conf import settings
from django.utils.http import urlsafe_base64_decode

from .batch_upload_async import BatchUploadThread
from .csv_report_generator import CsvReportGenerator
from .excel_report_generator import ExcelReportGenerator

from itertools import chain

from django.contrib import messages
import xlwt
from django.template.response import TemplateResponse
from django.shortcuts import resolve_url
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, SetPasswordForm, PasswordChangeForm
from django.contrib.auth.tokens import default_token_generator
from .tasks import zip_custom_requests, zip_individual_requests, zip_corporate_requests

from .migrate_client_attachments import MigrateAttachments




import datetime
import json
import math
from django.utils import formats


from braces import views

from .forms import AnalystRequestDetailStatusForm, LoginForm, IndividualRequestForm, CorporateRequestForm, CompanyEmployeeRegistrationForm, CompanyForm, \
    CompanyDueDiligenceSelectionForm, HumanResourcesTypeSelectionForm, InvestigativeTypeSelectionForm, \
    RegulatoryTypeSelectionForm, BusinessInvestmentTypeSelectionForm, ServicesForm, ForgotPasswordForm, \
    ChangePasswordForm, SetCompanyCorporateForm, DynamicRequestFormForm, DynamicRequestFormFieldsForm, CustomRequestForm,\
    SetCompanyIndividualForm, DocumentForm, EtradeReportingPeriodForm, SurchargeForm,CustomerRegistrationForm , \
    IndividualRequestFormManager, CorporateRequestFormManager, CustomRequestFormManager, AnalystNotesForm, AnalystInternalDocForm

from .models import BaseRequestDetailStatus, CorporateRequestDetailStatus, CustomRequestDetailStatus, RequestDetailStatus, RequestSelectedSupervisor, SpotLitStaff, Request, CorporateRequest, \
    CompanyServiceSelection, CompanyEmployee, Company, CompanyDueDiligenceTypeSelection, DueDiligenceType, \
    DueDiligenceTypeServices, CompanyServiceSelection, Service, RequestServiceStatus, CorporateRequestServiceStatus, \
    SPOTLIT_ANALYST_GROUP, SPOTLIT_MANAGER_GROUP, COMPANY_EMPLOYEE_GROUP, REVIEWER, Reports, DynamicRequestForm, \
    DynamicRequestFormFields, CustomRequest, CustomRequestFields, CustomRequestServiceStatus,\
    BatchFile, BaseRequestStatus, Status, RequestArchive, Surcharge, ChargeType, CustomRequestSelectedSupervisor, CorporateRequestSelectedSupervisor

from .utils import *

from .email_util import send_data_form_email, send_status_change_email, send_status_change_email_for_corporate, send_activation_email, \
    send_received_email, send_created_by_change_email, send_analyst_change_email, send_status_change_email_for_custom, \
    send_new_customer_registration_email_to_admin, send_verification_email
from .pdf_generator import generate_pdf, archive_pdf, generate_archived_pdf, generate_report_pdf_file

from eztables.views import DatatablesView
import magic
import re
import os
import csv
from .field_choices import *
from localflavor.us.us_states import US_STATES


class HomeRedirect(generic.TemplateView):
    template_name = 'redirect.html'

    def dispatch(self, request, *args, **kwargs):
        return redirect_to_dashboard(request.user)

class ChartTest(generic.TemplateView):
    template_name = 'core/chart.html'




def get_dashboard_for_user(current_user):
    url = ""
    group = get_user_group(current_user)
    if (group is None):
        url = reverse_lazy('login')
    elif (group.name == SPOTLIT_MANAGER_GROUP):
        url = reverse_lazy('manager_dashboard')
    elif (group.name == SPOTLIT_ANALYST_GROUP):
        url = reverse_lazy('analyst_dashboard')
    elif (group.name == REVIEWER):
        url = reverse_lazy('reviewer_dashboard')
    elif (group.name == REGISTERED_CUSTOMER_GROUP):
        url = reverse_lazy('customer_profile')
    elif (group.name == COMPANY_EMPLOYEE_GROUP):
        user = get_company_employee(current_user)
        if is_company_supervisor(user):
            url = reverse_lazy('supervisor_dashboard')
        else:
            url = reverse_lazy('employee_dashboard')
    else:
        url = reverse_lazy('login')
    return url


def get_dashboard_for_user_after_signin(current_user):
    url = ""
    group = get_user_group(current_user)
    if (group is None):
        url = reverse_lazy('login')
    elif (group.name == SPOTLIT_MANAGER_GROUP):
        url = reverse_lazy('manager_dashboard')
    elif (group.name == SPOTLIT_ANALYST_GROUP):
        url = reverse_lazy('analyst_dashboard')
    elif (group.name == REVIEWER):
        url = reverse_lazy('reviewer_dashboard')
    elif (group.name == REGISTERED_CUSTOMER_GROUP):
        url = reverse_lazy('customer_profile')
    elif (group.name == COMPANY_EMPLOYEE_GROUP):
        user = get_company_employee(current_user)
        if is_company_supervisor(user):
            url = reverse_lazy('supervisor_dashboard')
        else:
            url = reverse_lazy('employee_dashboard')
    else:
        url = reverse_lazy('login')
    return url


def redirect_to_dashboard(current_user):
    if (current_user.is_authenticated()):
        url = get_dashboard_for_user(current_user)
        return redirect(url)
    else:
        return redirect(reverse_lazy('login'))


# Authentication******************************************

class LoginView(generic.FormView, generic.edit.FormMixin):
    form_class = LoginForm
    template_name = 'core/login.html'

    def get_success_url(self):
        if is_company_employee(self.request.user):
            employee = get_company_employee(self.request.user)
            employee.is_activated = True
            employee.save()
        return get_dashboard_for_user_after_signin(self.request.user)

    def form_valid(self, form):
        self.request.session.flush()
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user = authenticate(username=username, password=password)

        if user is not None and user.is_active:
            login(self.request, user)
            return super(LoginView, self).form_valid(form)
        else:
            return self.form_invalid(form)


@csrf_protect
def password_reset(request, is_admin_site=False,
                   template_name='registration/password_reset_form.html',
                   email_template_name='registration/password_reset_email.html',
                   subject_template_name='registration/password_reset_subject.txt',
                   password_reset_form=PasswordResetForm,
                   token_generator=default_token_generator,
                   post_reset_redirect=None,
                   from_email=None,
                   current_app=None,
                   extra_context=None):
    if post_reset_redirect is None:
        post_reset_redirect = reverse('password_reset_done')
    else:
        post_reset_redirect = resolve_url(post_reset_redirect)
    if request.method == "POST":
        form = password_reset_form(request.POST)
        if form.is_valid():
            opts = {
                'use_https': request.is_secure(),
                'token_generator': token_generator,
                'from_email': from_email,
                'email_template_name': email_template_name,
                'subject_template_name': subject_template_name,
                'request': request,
            }
            if is_admin_site:
                opts = dict(opts, domain_override=request.get_host())
            form.save(**opts)
            return HttpResponseRedirect(post_reset_redirect)
    else:
        form = password_reset_form()
    context = {
        'form': form,
    }
    if extra_context is not None:
        context.update(extra_context)
    return TemplateResponse(request, template_name, context,
                            current_app=current_app)


def forgot_password(request):
    return password_reset(request, template_name='core/forgot_password.html',
                          password_reset_form=ForgotPasswordForm,
                          email_template_name='emails/reset_email.txt',
                          subject_template_name='emails/reset_subject.txt',
                          post_reset_redirect=reverse('login'),
                          from_email='Voyint Admin <info@voyint.com>',
                          extra_context={"domain": "portal.voyint.com"})


def reset_confirm(request, uidb64=None, token=None):
    # Wrap the built-in reset confirmation view and pass to it all the captured parameters like uidb64, token
    # and template name, url to redirect after password reset is confirmed.
    return password_reset_confirm(request, template_name='core/reset_confirm.html',
                                  set_password_form=ChangePasswordForm,
                                  uidb64=uidb64, token=token, post_reset_redirect=reverse('login'))

class VerifyAccount(generic.View):
    def get(self, request, uidb64=None, token=None, *args, **kwargs):
        user_id = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=user_id)
        if user != request.user:
            return redirect_to_dashboard(request.user)
        if user is not None:
            if not is_unverified_user(user):
                url = get_dashboard_for_user(user)
                return redirect_to_dashboard(user)
            else:
                user.groups.remove(get_unverified_user_group())
                user.save()
                url = get_dashboard_for_user(user)
                return redirect(url)

        return HttpResponse('Activation link is invalid!')



class LogOutView(generic.RedirectView):
    permanent = True
    url = reverse_lazy('login')

    def get(self, request, *args, **kwargs):
        request.session.flush()
        logout(request)
        return super(LogOutView, self).get(request, *args, **kwargs)


# Access Controls Mixins***********************************************

class SupervisorOnlyMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if (is_company_supervisor_mixin_check(request.user)):
            return super(SupervisorOnlyMixin, self).dispatch(request, *args, **kwargs)
        else:
            return redirect_to_dashboard(request.user)

class ManagerOnlyMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if (is_manager(request.user)):
            return super(ManagerOnlyMixin, self).dispatch(request, *args, **kwargs)
        else:
            return redirect_to_dashboard(request.user)

class ManagerCustomerMixin(object):
    def dispatch(self,request,*args,**kwargs):
        if (is_manager(request.user)):
            return super(ManagerCustomerMixin, self).dispatch(request, *args, **kwargs)
        elif is_registered_customer(request.user):
            return super(ManagerCustomerMixin, self).dispatch(request, *args, **kwargs)
        else:
            return redirect_to_dashboard(request.user)

class ManagerSupervisorOnlyMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if is_manager(request.user):
            return super(ManagerSupervisorOnlyMixin, self).dispatch(request, *args, **kwargs)
        elif is_company_supervisor_mixin_check(request.user):
            return super(ManagerSupervisorOnlyMixin, self).dispatch(request, *args, **kwargs)
        else:
            return redirect_to_dashboard(request.user)


class EmployeeOnlyMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if (is_company_employee(request.user)):
            return super(EmployeeOnlyMixin, self).dispatch(request, *args, **kwargs)
        else:
            return redirect_to_dashboard(request.user)


class CorporateEmployeeOnlyMixin(EmployeeOnlyMixin):
    def dispatch(self, request, *args, **kwargs):
        if (is_corporate_company_employee(request.user)):
            return super(CorporateEmployeeOnlyMixin, self).dispatch(request, *args, **kwargs)
        else:
            return redirect_to_dashboard(request.user)


class AnalystOnlyMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if (is_analyst(request.user)):
            return super(AnalystOnlyMixin, self).dispatch(request, *args, **kwargs)
        else:
            return redirect_to_dashboard(request.user)


# Company Employee Registration/Updating*******************************

class CompanyEmployeeRegistration(ManagerOnlyMixin, generic.FormView):
    form_class = CompanyEmployeeRegistrationForm
    model = User
    template_name = 'core/employee_signup.html'

    def get_success_url(self):
        return reverse('company', kwargs={"pk": self.kwargs['pk']})

    def form_valid(self, form):
        username = form.cleaned_data.get('username')
        try:
            user = User.objects.get(username=username)
            if user:
                form._errors['username'] = ['User with that email address already exists.']
                return self.form_invalid(form)
        except Exception, e:
            print "unique user"

        user = User.objects.create_user(form.cleaned_data['username'],
                                        form.cleaned_data['username'], None)
        user.first_name = form.cleaned_data['first_name']
        user.last_name = form.cleaned_data['last_name']
        user.groups.add(get_company_employee_group())
        user.save()

        company_id = self.kwargs['pk']
        if (company_is_valid(company_id)):
            company = Company.objects.get(id=company_id)
            position = form.cleaned_data['position']
            phone_number = form.cleaned_data['phone_number']
            supervisor = form.cleaned_data['supervisor']

            employee = CompanyEmployee(user=user, company=company, position=position, phone_number=phone_number,
                                       is_activated=False, supervisor=supervisor)
            employee.save()
            send_activation_email(self.request, username, user)
            return super(CompanyEmployeeRegistration, self).form_valid(form)

        return self.form_invalid(form)

def resend_signup_email(request, company_pk, employee_pk):
    if(is_manager(request.user) and company_is_valid(company_pk) and employee_is_valid(employee_pk)):
        employee = get_object_or_404(CompanyEmployee, pk=employee_pk)
        company = get_object_or_404(Company, pk=company_pk)
        send_activation_email(request, employee.user.username, employee.user)

        return HttpResponseRedirect(reverse('company', kwargs={"pk": company.pk}))
    return redirect_to_dashboard(request.user)

def resend_verification_email(request):
    if is_unverified_user(request.user):
        send_verification_email(request,request.user)
    return redirect_to_dashboard(request.user)



class CompanyEmployeeUpdate(ManagerOnlyMixin, generic.FormView):
    form_class = CompanyEmployeeRegistrationForm
    template_name = 'core/employee_update.html'

    def get_initial(self):
        employee = None
        employee_pk = self.kwargs['pk']
        if (employee_is_valid(employee_pk)):
            employee = CompanyEmployee.objects.get(pk=self.kwargs['pk'])
        initial = {'employee': employee}
        return initial

    def get_success_url(self):
        employee = CompanyEmployee.objects.get(pk=self.kwargs['pk'])
        return reverse('company', kwargs={"pk": employee.company.pk})

    def form_valid(self, form):
        employee_pk = self.kwargs['pk']
        if (not employee_is_valid(employee_pk)):
            return self.form_invalid(form)

        employee = CompanyEmployee.objects.get(pk=employee_pk)
        user = employee.user
        username = form.cleaned_data.get('username')

        is_valid_username = True
        try:
            user = User.objects.get(username=username)
            if user and employee.user != user:
                form._errors['username'] = ['User with that email address already exists.']
                is_valid_username = False
        except Exception, e:
            print "unique user"

        if (not is_valid_username):
            return self.form_invalid(form)
        else:
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            position = form.cleaned_data['position']
            phone_number = form.cleaned_data['phone_number']
            supervisor = form.cleaned_data['supervisor']

            if (user.username != username):
                user.username = username
            if (user.email != username):
                user.email = username
            if (employee.user.first_name != first_name):
                user.first_name = first_name
            if (user.last_name != last_name):
                user.last_name = last_name
            if ( employee.position != position):
                employee.position = position
            if (employee.phone_number != phone_number):
                employee.phone_number = phone_number
            if (employee.supervisor != supervisor):
                employee.supervisor = supervisor
            user.save()
            employee.save()

            return super(CompanyEmployeeUpdate, self).form_valid(form)


# Customer Registration Form***********************

class CustomerRegistration(generic.FormView, generic.edit.FormMixin):
    form_class=CustomerRegistrationForm
    model = User
    template_name = "core/customer_registration.html"

    def get_success_url(self):
        return reverse('customer_profile')

    def form_valid(self, form):
        username = form.cleaned_data.get('username')
        email = form.cleaned_data.get('email')
        password = form.cleaned_data.get('password')
        try:
            user = User.objects.get(email=email)
            if user:
                form._errors['email'] = ['User with that email address already exists.']
                return self.form_invalid(form)
        except Exception, e:
            print "unique user"

        user = User.objects.create_user(username,email,password)
        user.first_name = form.cleaned_data['first_name']
        user.last_name = form.cleaned_data['last_name']
        user.groups.add(get_registered_customer_group())
        user.groups.add(get_unverified_user_group())
        user.save()
        send_verification_email(self.request,user)
        send_new_customer_registration_email_to_admin(self.request,user)
        user = authenticate(username=username,password=password)
        login(self.request, user)
        return super(CustomerRegistration, self).form_valid(form)

# Customer Profile Page*********************************
class CustomerProfileView(generic.TemplateView):
    template_name = "core/customer_profile.html"

    def get(self,request,*args,**kwargs):
        current_user = request.user
        if is_registered_customer(current_user):
            context = self.get_context_data(**kwargs)
            context['username'] = current_user.username
            if is_unverified_user(current_user):
                context['is_unverified'] = True
            return self.render_to_response(context)
        else:
            return redirect_to_dashboard(current_user)

# Dynamic Request Form Creation/Updating*******************************

class DynamicRequestFormCreation(ManagerOnlyMixin, generic.FormView):
    form_class = DynamicRequestFormForm
    model = DynamicRequestForm
    template_name = 'core/create_dynamic_request_form.html'

    def get_initial(self):
        initial = super(DynamicRequestFormCreation, self).get_initial()

        initial['render_form'] = "True"
        return initial

    def get_success_url(self):
        return reverse('company', kwargs={"pk": self.kwargs['pk']})

    def form_valid(self, form):
        company_id = self.kwargs['pk']
        if company_is_valid(company_id):
            company = Company.objects.get(id=company_id)

            name = form.cleaned_data.get('name')
            render_form = form.cleaned_data.get('render_form')
            try:
                name = DynamicRequestForm.objects.get(company=company, name=name)
                if name:
                    form._errors['name'] = ['Custom Request Form with that name already exists.']
                    return self.form_invalid(form)
            except Exception, e:
                print "unique form"

            dynamic_request_form = DynamicRequestForm(name=name, company=company, render_form=render_form)
            dynamic_request_form.save()
            return super(DynamicRequestFormCreation, self).form_valid(form)

        return self.form_invalid(form)


class DynamicRequestFormUpdate(ManagerOnlyMixin, generic.FormView):
    form_class = DynamicRequestFormForm
    template_name = 'core/update_dynamic_request_form.html'

    def get_initial(self):
        dynamic_request_form = None
        dynamic_request_form_pk = self.kwargs['pk']

        if (dynamic_request_form_is_valid(dynamic_request_form_pk)):
            dynamic_request_form = DynamicRequestForm.objects.get(pk=self.kwargs['pk'])

        initial = {'dynamic_request_form': dynamic_request_form}

        return initial

    def get_success_url(self):
        dynamic_request_form = DynamicRequestForm.objects.get(pk=self.kwargs['pk'])
        return reverse('company', kwargs={"pk": dynamic_request_form.company.pk})

    def form_valid(self, form):
         dynamic_request_form_pk = self.kwargs['pk']
         if (dynamic_request_form_is_valid(dynamic_request_form_pk)):

            drf = DynamicRequestForm.objects.get(pk=dynamic_request_form_pk)
            name = form.cleaned_data.get('name')
            if drf.name.lower() != name.lower():
                try:
                    drf = DynamicRequestForm.objects.get(company=drf.company, name=name)
                    if drf:
                        form._errors['name'] = ['Custom Request Form with that name already exists.']
                        return self.form_invalid(form)
                except Exception, e:
                    print "name does not exist"

            drf.name = name
            drf.render_form = form.cleaned_data.get('render_form')
            drf.save()
            return super(DynamicRequestFormUpdate, self).form_valid(form)

         return self.form_invalid(form)


class DynamicRequestFormConfiguration(ManagerOnlyMixin, generic.FormView):
    form_class = DynamicRequestFormFieldsForm
    template_name = 'core/update_dynamic_request_form_fields.html'

    def get_initial(self):
        initial = super(DynamicRequestFormConfiguration, self).get_initial()

        return initial

    def get_context_data(self, **kwargs):
        context = super(DynamicRequestFormConfiguration, self).get_context_data(**kwargs)
        dynamic_request_form = DynamicRequestForm.objects.get(pk=self.kwargs['pk'])
        context['fields'] = DynamicRequestFormFields.objects.filter(dynamic_request_form=dynamic_request_form)\
            .order_by('sort_order', 'group')
        context['dynamic_request_form'] = dynamic_request_form
        return context

    def get_success_url(self):
        dynamic_request_form = DynamicRequestForm.objects.get(pk=self.kwargs['pk'])
        return reverse('dynamic_request_form_configure', kwargs={"pk": dynamic_request_form.pk})

    def form_valid(self, form):

        dynamic_request_form_pk = self.kwargs['pk']
        if (dynamic_request_form_is_valid(dynamic_request_form_pk)):
            drf = DynamicRequestForm.objects.get(pk=dynamic_request_form_pk)

            label = form.cleaned_data.get('label')
            help_text = form.cleaned_data.get('help_text')
            type = form.cleaned_data.get('type')
            group = form.cleaned_data.get('group')
            sort_order = form.cleaned_data.get('sort_order')
            field_format = form.cleaned_data.get('field_format')
            required = form.cleaned_data.get('required')

            fields = DynamicRequestFormFields(label=label, help_text=help_text, type=type, group=group,
                                              field_format=field_format, sort_order=sort_order,
                                              dynamic_request_form=drf, required=required)
            fields.save()

            return super(DynamicRequestFormConfiguration, self).form_valid(form)

        return self.form_invalid(form)

class DynamicRequestFormConfigurationUpdate(ManagerOnlyMixin, generic.FormView):
    form_class = DynamicRequestFormFieldsForm
    template_name = 'core/update_dynamic_request_form_fields.html'

    def get_initial(self):
        initial = super(DynamicRequestFormConfigurationUpdate, self).get_initial()
        field = None
        field_pk = self.kwargs['pk']

        if dynamic_request_form_field_is_valid(field_pk):
            field = DynamicRequestFormFields.objects.get(pk=self.kwargs['pk'])

        initial = {'field': field}

        return initial

    def get_context_data(self, **kwargs):
        context = super(DynamicRequestFormConfigurationUpdate, self).get_context_data(**kwargs)
        field = DynamicRequestFormFields.objects.get(pk=self.kwargs['pk'])

        context['fields'] = DynamicRequestFormFields.objects.filter(dynamic_request_form=field.dynamic_request_form)\
            .order_by('sort_order', 'group')
        context['dynamic_request_form'] = field.dynamic_request_form
        return context

    def get_success_url(self):
        field = DynamicRequestFormFields.objects.get(pk=self.kwargs['pk'])
        return reverse('dynamic_request_form_configure', kwargs={"pk": field.dynamic_request_form.pk})

    def form_valid(self, form):

        field_pk = self.kwargs['pk']
        if (dynamic_request_form_field_is_valid(field_pk)):
            field = DynamicRequestFormFields.objects.get(pk=field_pk)

            field.label = form.cleaned_data.get('label')
            field.help_text = form.cleaned_data.get('help_text')
            field.type = form.cleaned_data.get('type')
            field.group = form.cleaned_data.get('group')
            field.sort_order = form.cleaned_data.get('sort_order')
            field.field_format = form.cleaned_data.get('field_format')
            field.required = form.cleaned_data.get('required')

            field.save()

            return super(DynamicRequestFormConfigurationUpdate, self).form_valid(form)

        return self.form_invalid(form)

@login_required
def delete_dynamic_request_form_field(request, dynamic_request_pk, field_pk):
    if (is_manager(request.user) and dynamic_request_form_is_valid(dynamic_request_pk)):
        field = get_object_or_404(DynamicRequestFormFields, pk=field_pk)

        if not are_there_custom_request_fields_using_dynamic_request_form_field(field_pk):
            field.delete()
        else:
            field.required = False
            field.archive = True
            field.save()


    return HttpResponseRedirect(reverse('dynamic_request_form_configure', kwargs={"pk": dynamic_request_pk}))


# View Create/Update Custom Request ***********************************************
class CreateCustomRequestView(EmployeeOnlyMixin, generic.FormView):
    model = CustomRequest
    form_class = CustomRequestForm
    template_name = 'core/create_custom_request.html'

    def get_form_kwargs(self):
        kwargs = super(CreateCustomRequestView, self).get_form_kwargs()
        kwargs.update({'request': self.request})

        # Retrieve Custom Fields
        dynamic_request_form = get_object_or_404(DynamicRequestForm, pk=self.kwargs['dynamic_request_pk'])
        fields = DynamicRequestFormFields.objects.filter(dynamic_request_form=dynamic_request_form, archive=False).order_by('sort_order', 'group')
        kwargs.update({'fields': fields})
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(CreateCustomRequestView, self).get_context_data(**kwargs)

        # for the selecting service logic
        service_selections = []
        context['services'] = Service.objects.all().order_by('display_order')
        try:
            company = CompanyEmployee.get_company_employee(self.request.user).company
            service_selections = CompanyServiceSelection.get_service_selections_for_company(company)
        except Exception, e:
            raise e
        json_serializer = serializers.get_serializer("json")()
        serialized_selections = json_serializer.serialize(service_selections, ensure_ascii=False, use_natural_keys=True)
        context['company_service_selections'] = serialized_selections

        company_logo = None
        company = None
        try:
            company = CompanyEmployee.objects.get(user=self.request.user).company
        except:
            pass

        try:
            company_logo = company.logo
        except:
            pass

        custom_requests = None
        try:
            custom_requests = DynamicRequestForm.objects.filter(company=company)
        except:
            pass

        context['company_logo_active'] = company.company_logo_active
        context['company_logo'] = company_logo
        context['custom_requests'] = custom_requests
        context['is_corporate_sidebar'] = company.is_corporate
        context['is_individual'] = company.is_individual
        context['is_custom_sidebar'] = company.is_custom
        context['upload_form'] = DocumentForm()
        context['is_supervisor'] = is_company_supervisor_mixin_check(self.request.user)
        context['batch_upload_active'] = company.batch_upload_active


        #to decide what services to display
        due_diligence_services = DueDiligenceTypeServices.objects.order_by('pk')
        serialized_type_services = json_serializer.serialize(due_diligence_services, ensure_ascii=False,
                                                             use_natural_keys=True)
        context['type_services'] = serialized_type_services

        custom_request = get_object_or_404(DynamicRequestForm, pk=self.kwargs['dynamic_request_pk'])
        context['custom_request_form'] = custom_request
        context['dynamic_request_pk'] = custom_request.pk

        return context

    def get_success_url(self):
        return get_dashboard_for_user(self.request.user)

    def form_valid(self, form):
        dynamic_request_form = get_object_or_404(DynamicRequestForm, pk=self.kwargs['dynamic_request_pk'])
        fields = DynamicRequestFormFields.objects.filter(dynamic_request_form=dynamic_request_form, archive=False).order_by('sort_order', 'group')

        request = form.save(dynamic_request_form, fields)

        #create new status
        request_status = Status(content_object=request, status=Status.NEW_STATUS, datetime=datetime.datetime.now())

        request_status.save()

        #send email to manager, to inform that request was created
        send_status_change_email(request, User.objects.get(username=settings.REQUEST_VOYINT_MANAGER_USERNAME),
                                 Status.NEW_STATUS)

        #send email to creator to acknowledge reciept
        send_received_email(request, request.created_by.user)
        return super(CreateCustomRequestView, self).form_valid(form)


class UpdateCustomRequestView(EmployeeOnlyMixin, generic.UpdateView):
    model = CustomRequest
    form_class = CustomRequestForm
    template_name = 'core/update_custom_request.html'

    def get_form_kwargs(self):
        kwargs = super(UpdateCustomRequestView, self).get_form_kwargs()
        kwargs.update({'request': self.request})

        # Retrieve Custom Fields
        custom_request = get_object_or_404(CustomRequest, pk=self.kwargs['pk'])
        fields = CustomRequestFields.objects.filter(custom_request=custom_request)\
            .order_by('form_field__sort_order', 'form_field__group')

        kwargs.update({'fields': fields})
        kwargs.update({'update': True})

        return kwargs

    def get_context_data(self, **kwargs):
        context = super(UpdateCustomRequestView, self).get_context_data(**kwargs)
        context['services'] = Service.objects.all()

        # for the selecting service logic
        service_selections = []
        try:
            company = CompanyEmployee.get_company_employee(self.request.user).company
            service_selections = CompanyServiceSelection.get_service_selections_for_company(company)
        except Exception, e:
            raise e
        json_serializer = serializers.get_serializer("json")()
        serialized_selections = json_serializer.serialize(service_selections, ensure_ascii=False, use_natural_keys=True)
        context['company_service_selections'] = serialized_selections

        company_logo = None
        company = None
        try:
            company = CompanyEmployee.objects.get(user=self.request.user).company
        except:
            pass

        try:
            company_logo = company.logo
        except:
            pass

        custom_requests = None
        try:
            custom_requests = DynamicRequestForm.objects.filter(company=company)
        except:
            pass

        context['company_logo'] = company_logo
        context['custom_requests'] = custom_requests
        context['is_corporate_sidebar'] = company.is_corporate
        context['is_individual'] = company.is_individual
        context['is_custom_sidebar'] = company.is_custom
        context['is_supervisor'] = is_company_supervisor_mixin_check(self.request.user)

        #to decide what services to display
        due_diligence_services = DueDiligenceTypeServices.objects.order_by('pk')
        serialized_type_services = json_serializer.serialize(due_diligence_services, ensure_ascii=False,
                                                             use_natural_keys=True)
        context['type_services'] = serialized_type_services

        custom_request = get_object_or_404(CustomRequest, pk=self.kwargs['pk'])
        context['dynamic_request_form'] = custom_request.dynamic_request_form

        return context

    def get_success_url(self):
        return get_dashboard_for_user(self.request.user)

    def form_valid(self, form):
        custom_request = get_object_or_404(CustomRequest, pk=self.kwargs['pk'])
        fields = CustomRequestFields.objects.filter(custom_request=custom_request)\
            .order_by('form_field__sort_order', 'form_field__group')

        custom_request = form.save(custom_request, fields, True)

        #create new status
        request_status = Status(content_object=custom_request, status=Status.NEW_STATUS,
                                       datetime=datetime.datetime.now())
        request_status.save()

        #send email to manager, to inform that request was created
        send_status_change_email(custom_request, User.objects.get(username=settings.REQUEST_VOYINT_MANAGER_USERNAME),
                                 Status.NEW_STATUS)

        custom_request.delete_unrelated_services_after_update()
        return super(UpdateCustomRequestView, self).form_valid(form)

# Create/Update Request ***********************************************
class CreateIndividualRequestView(EmployeeOnlyMixin, generic.FormView):
    model = Request
    form_class = IndividualRequestForm
    template_name = 'core/create_individual_request.html'

    def get_form_kwargs(self):
        kwargs = super(CreateIndividualRequestView, self).get_form_kwargs()
        kwargs.update({'request': self.request})
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(CreateIndividualRequestView, self).get_context_data(**kwargs)

        # for the selecting service logic
        service_selections = []
        context['services'] = Service.objects.all().order_by('display_order')
        try:
            company = CompanyEmployee.get_company_employee(self.request.user).company
            service_selections = CompanyServiceSelection.get_service_selections_for_company(company)
            public_service_selections = CompanyServiceSelection.get_service_selections_for_public_packages()
            service_selections = service_selections | public_service_selections
        except Exception, e:
            raise e
        json_serializer = serializers.get_serializer("json")()
        serialized_selections = json_serializer.serialize(service_selections, ensure_ascii=False, use_natural_keys=True)
        context['company_service_selections'] = serialized_selections

        company_logo = None
        company = None
        try:
            company = CompanyEmployee.objects.get(user=self.request.user).company
        except:
            pass

        try:
            company_logo = company.logo
        except:
            pass

        custom_requests = None
        try:
            custom_requests = DynamicRequestForm.objects.filter(company=company)
        except:
            pass


        context['company_logo_active'] = company.company_logo_active
        context['company_logo'] = company_logo
        context['custom_requests'] = custom_requests

        #to decide what services to display
        due_diligence_services = DueDiligenceTypeServices.objects.order_by('pk')
        serialized_type_services = json_serializer.serialize(due_diligence_services, ensure_ascii=False,
                                                             use_natural_keys=True)
        context['type_services'] = serialized_type_services

        context['is_corporate_sidebar'] = company.is_corporate
        context['is_individual'] = company.is_individual
        context['is_custom_sidebar'] = company.is_custom
        context['is_supervisor'] = is_company_supervisor_mixin_check(self.request.user)

        return context

    def get_success_url(self):
        return get_dashboard_for_user(self.request.user)

    def form_valid(self, form):
        # check for ssn if us citizen
        #ssn = form.cleaned_data['ssn']
        #citizenship = form.cleaned_data['citizenship']
        #if (not ssn or len(ssn) == 0) and citizenship == 'US':
        #form._errors['ssn'] = ['SSN required for US citizens.']
        #return self.form_invalid(form)


        request = form.save()
        #create new status
        # request_status = RequestStatus(request=request, status=RequestStatus.NEW_STATUS,
        #                                datetime=datetime.datetime.now())

        request_status = Status(content_object=request, status=Status.NEW_STATUS, datetime=datetime.datetime.now())
        request_status.save()

        #send email to manager, to inform that request was created
        #the below two lines were commented out to make it run locally
        send_status_change_email(request, User.objects.get(username=settings.REQUEST_VOYINT_MANAGER_USERNAME),
                                 Status.NEW_STATUS)

        #send email to creator to acknowledge reciept
        #the below line was commented out to make it run locally
        send_received_email(request, request.created_by.user)
        return super(CreateIndividualRequestView, self).form_valid(form)


class UpdateIndividualRequestView(EmployeeOnlyMixin, generic.UpdateView):
    model = Request
    form_class = IndividualRequestForm
    template_name = 'core/update_request.html'

    def get_form_kwargs(self):
        kwargs = super(UpdateIndividualRequestView, self).get_form_kwargs()
        kwargs.update({'request': self.request})
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(UpdateIndividualRequestView, self).get_context_data(**kwargs)
        context['services'] = Service.objects.all()

        # for the selecting service logic
        service_selections = []
        try:
            company = CompanyEmployee.get_company_employee(self.request.user).company
            service_selections = CompanyServiceSelection.get_service_selections_for_company(company)
            public_service_selections = CompanyServiceSelection.get_service_selections_for_public_packages()
            service_selections = service_selections | public_service_selections
        except Exception, e:
            raise e
        json_serializer = serializers.get_serializer("json")()
        serialized_selections = json_serializer.serialize(service_selections, ensure_ascii=False, use_natural_keys=True)
        context['company_service_selections'] = serialized_selections

        company_logo = None
        company = None
        try:
            company = CompanyEmployee.objects.get(user=self.request.user).company
        except:
            pass

        try:
            company_logo = company.logo
        except:
            pass

        custom_requests = None
        try:
            custom_requests = DynamicRequestForm.objects.filter(company=company)
        except:
            pass

        context['company_logo_active'] = company.company_logo_active
        context['company_logo'] = company_logo
        context['custom_requests'] = custom_requests

        #to decide what services to display
        due_diligence_services = DueDiligenceTypeServices.objects.order_by('pk')
        serialized_type_services = json_serializer.serialize(due_diligence_services, ensure_ascii=False,
                                                             use_natural_keys=True)
        context['type_services'] = serialized_type_services

        context['is_corporate_sidebar'] = company.is_corporate
        print company.is_corporate
        context['is_individual'] = company.is_individual
        context['is_custom_sidebar'] = company.is_custom
        context['is_supervisor'] = is_company_supervisor_mixin_check(self.request.user)

        return context

    def get_success_url(self):
        return get_dashboard_for_user(self.request.user)

    def form_valid(self, form):
        # check for ssn if us citizen
        #ssn = form.cleaned_data['ssn']
        #citizenship = form.cleaned_data['citizenship']
        #if (not ssn or len(ssn) == 0) and citizenship == 'US':
        #form._errors['ssn'] = ['SSN required for US citizens.']
        #return self.form_invalid(form)

        request = form.save()
        #create new status
        request_status = Status(content_object=request, status=Status.NEW_STATUS,
                                       datetime=datetime.datetime.now())
        request_status.save()

        #send email to manager, to inform that request was created
        send_status_change_email(request, User.objects.get(username=settings.REQUEST_VOYINT_MANAGER_USERNAME),
                                 Status.NEW_STATUS)

        request.delete_unrelated_services_after_update()
        return super(UpdateIndividualRequestView, self).form_valid(form)


class CreateCorporateRequestView(CorporateEmployeeOnlyMixin, generic.FormView):
    model = CorporateRequest
    form_class = CorporateRequestForm
    template_name = 'core/create_corporate_request.html'

    def get_form_kwargs(self):
        kwargs = super(CreateCorporateRequestView, self).get_form_kwargs()
        kwargs.update({'request': self.request})
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(CreateCorporateRequestView, self).get_context_data(**kwargs)

        # for the selecting service logic
        service_selections = []
        context['services'] = Service.objects.all().order_by('display_order')
        try:
            company = CompanyEmployee.get_company_employee(self.request.user).company
            service_selections = CompanyServiceSelection.get_service_selections_for_company(company)
            public_service_selections = CompanyServiceSelection.get_service_selections_for_public_packages()
            service_selections = service_selections | public_service_selections
        except Exception, e:
            raise e
        json_serializer = serializers.get_serializer("json")()
        serialized_selections = json_serializer.serialize(service_selections, ensure_ascii=False, use_natural_keys=True)
        context['company_service_selections'] = serialized_selections

        company_logo = None
        company = None
        try:
            company = CompanyEmployee.objects.get(user=self.request.user).company
        except:
            pass

        try:
            company_logo = company.logo
        except:
            pass

        custom_requests = None
        try:
            custom_requests = DynamicRequestForm.objects.filter(company=company)
        except:
            pass

        context['company_logo_active'] = company.company_logo_active
        context['company_logo'] = company_logo
        context['custom_requests'] = custom_requests

        #to decide what services to display
        due_diligence_services = DueDiligenceTypeServices.objects.order_by('pk')
        serialized_type_services = json_serializer.serialize(due_diligence_services, ensure_ascii=False,
                                                             use_natural_keys=True)
        context['type_services'] = serialized_type_services

        context['is_corporate_sidebar'] = company.is_corporate
        context['is_individual'] = company.is_individual
        context['is_custom_sidebar'] = company.is_custom
        context['is_supervisor'] = is_company_supervisor_mixin_check(self.request.user)

        return context

    def get_success_url(self):
        return get_dashboard_for_user(self.request.user)

    def form_valid(self, form):
        # check for ssn if us citizen
        #ssn = form.cleaned_data['ssn']
        #citizenship = form.cleaned_data['citizenship']
        #if (not ssn or len(ssn) == 0) and citizenship == 'US':
        #form._errors['ssn'] = ['SSN required for US citizens.']
        #return self.form_invalid(form)

        request = form.save()
        #create new status
        # request_status = CorporateRequestStatus(corporate_request=request, status=CorporateRequestStatus.NEW_STATUS,
        #                                         datetime=datetime.datetime.now())
        #

        request_status = Status(content_object=request, status=Status.NEW_STATUS, datetime=datetime.datetime.now())

        request_status.save()

        #send email to manager, to inform that request was created
        send_status_change_email_for_corporate(request, User.objects.get(username=settings.REQUEST_VOYINT_MANAGER_USERNAME),
                                               Status.NEW_STATUS)

        #send email to creator to acknowledge reciept
        send_received_email(request, request.created_by.user)
        return super(CreateCorporateRequestView, self).form_valid(form)


class UpdateCorporateRequestView(EmployeeOnlyMixin, generic.UpdateView):
    model = CorporateRequest
    form_class = CorporateRequestForm
    template_name = 'core/update_corporate_request.html'

    def get_form_kwargs(self):
        kwargs = super(UpdateCorporateRequestView, self).get_form_kwargs()
        kwargs.update({'request': self.request})
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(UpdateCorporateRequestView, self).get_context_data(**kwargs)
        context['services'] = Service.objects.all()

        # for the selecting service logic
        service_selections = []
        try:
            company = CompanyEmployee.get_company_employee(self.request.user).company
            service_selections = CompanyServiceSelection.get_service_selections_for_company(company)
            public_service_selections = CompanyServiceSelection.get_service_selections_for_public_packages()
            service_selections = service_selections | public_service_selections
        except Exception, e:
            raise e
        json_serializer = serializers.get_serializer("json")()
        serialized_selections = json_serializer.serialize(service_selections, ensure_ascii=False, use_natural_keys=True)
        context['company_service_selections'] = serialized_selections

        company_logo = None
        company = None
        try:
            company = CompanyEmployee.objects.get(user=self.request.user).company
        except:
            pass

        try:
            company_logo = company.logo
        except:
            pass

        custom_requests = None
        try:
            custom_requests = DynamicRequestForm.objects.filter(company=company)
        except:
            pass

        context['company_logo'] = company_logo
        context['custom_requests'] = custom_requests
        context['is_corporate_sidebar'] = company.is_corporate
        context['is_individual'] = company.is_individual
        context['is_custom_sidebar'] = company.is_custom
        context['is_supervisor'] = is_company_supervisor_mixin_check(self.request.user)

        #to decide what services to display
        due_diligence_services = DueDiligenceTypeServices.objects.order_by('pk')
        serialized_type_services = json_serializer.serialize(due_diligence_services, ensure_ascii=False,
                                                             use_natural_keys=True)
        context['type_services'] = serialized_type_services

        return context

    def get_success_url(self):
        return get_dashboard_for_user(self.request.user)

    def form_valid(self, form):
        # check for ssn if us citizen
        #ssn = form.cleaned_data['ssn']
        #citizenship = form.cleaned_data['citizenship']
        #if (not ssn or len(ssn) == 0) and citizenship == 'US':
        #form._errors['ssn'] = ['SSN required for US citizens.']
        #return self.form_invalid(form)

        request = form.save()
        #create new status
        request_status = Status(content_object=request, status=Status.NEW_STATUS,
                                                datetime=datetime.datetime.now())
        request_status.save()

        #send email to manager, to inform that request was created
        send_status_change_email_for_corporate(request, User.objects.get(username=settings.REQUEST_VOYINT_MANAGER_USERNAME),
                                               Status.NEW_STATUS)

        request.delete_unrelated_services_after_update()
        return super(UpdateCorporateRequestView, self).form_valid(form)


class UpdateIndividualRequestAttachmentManagerView(ManagerOnlyMixin,generic.UpdateView):
    model = Request
    form_class = IndividualRequestFormManager
    template_name = 'core/update_request_manager.html'

    def get_form_kwargs(self):
        kwargs = super(UpdateIndividualRequestAttachmentManagerView, self).get_form_kwargs()
        kwargs.update({'request': self.request})
        return kwargs

    def get_success_url(self):
        return reverse_lazy('request_manager', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        request = form.save()
        #create new status
        # request_status = Status(content_object=request, status=Status.NEW_STATUS,
        #                                         datetime=datetime.datetime.now())
        # request_status.save()

        return super(UpdateIndividualRequestAttachmentManagerView, self).form_valid(form)

class UpdateCorporateRequestAttachmentManagerView(UpdateIndividualRequestAttachmentManagerView):
    model = CorporateRequest
    form_class = CorporateRequestFormManager
    template_name = 'core/update_corporate_request_manager.html'

    def get_success_url(self):
        return reverse_lazy('corporate_request_manager', kwargs={'pk': self.object.pk})

class UpdateCustomRequestAttachmentManagerView(UpdateIndividualRequestAttachmentManagerView):
    model = CustomRequest
    form_class = CustomRequestFormManager
    template_name = 'core/update_custom_request_manager.html'

    def get_success_url(self):
        return reverse_lazy('custom_request_manager', kwargs={'pk': self.object.pk})

# Company Creation/Update and Detail View *************************************

class CreateCompanyView(ManagerCustomerMixin, generic.CreateView):
    model = Company
    form_class = CompanyForm
    template_name = 'core/create_company.html'
    def get_context_data(self, *args, **kwargs):
        context = super(CreateCompanyView, self).get_context_data(*args, **kwargs)
        if is_manager(self.request.user):
            context['is_user_manager'] = True
        return context

    def get_success_url(self):
        return reverse('company', kwargs={"pk": self.object.id})

    def get(self,request,*args,**kwargs):
        if is_unverified_user(request.user):
            return redirect_to_dashboard(request.user)
        return super(CreateCompanyView,self).get(request,*args,**kwargs)

    def form_valid(self, form):
        current_user = self.request.user
        if is_registered_customer(current_user):
            self.object = form.save()
            current_user.groups.remove(get_registered_customer_group())
            current_user.groups.add(get_company_employee_group())
            current_user.save()
            employee = CompanyEmployee(user=current_user, company=self.object,
                                       is_activated=True, supervisor=True)
            employee.save()
            return redirect('create_company')
        return super(CreateCompanyView, self).form_valid(form)


class UpdateCompanyView(ManagerOnlyMixin, generic.UpdateView):
    model = Company
    form_class = CompanyForm
    template_name = 'core/update_company.html'

    def get_success_url(self):
        return reverse('company', kwargs={"pk": self.object.id})


@login_required
def company_detail_view(request, pk):
    current_user = request.user
    if (is_manager(current_user) and company_is_valid(pk)):
        company = Company.objects.get(pk=pk)
        type_selection = get_company_selections_in_dict(company)
        
        public_packages = get_public_packages_with_company_disabled_status(company)

        company_employees = CompanyEmployee.objects.filter(company=company)
        dynamic_request_forms = DynamicRequestForm.objects.filter(company=company)

        corporate_form = SetCompanyCorporateForm(is_corp=company.is_corporate)
        individual_form = SetCompanyIndividualForm(is_individual=company.is_individual)

        return render(request, 'core/company_detail.html', {
            'corporateForm': corporate_form, 'individualForm': individual_form, 'company': company,
            'types': type_selection,'public_packages':public_packages, 'employees': company_employees,
            'dynamic_request_forms': dynamic_request_forms
        })
    return redirect_to_dashboard(current_user)

@login_required
def change_company_publiic_package_status(request,company_pk,package_pk):
    current_user = request.user
    if (request.method == "POST" and is_manager(current_user) and company_is_valid(company_pk) and public_dd_type_is_valid(package_pk)):
        company = Company.objects.get(pk=company_pk)
        public_package = CompanyDueDiligenceTypeSelection.objects.get(pk=package_pk,is_public=True)
        company_disabled_package = CompanyDisabledPackage.objects.filter(company=company,package=public_package).first()
        # Might change below to unicode when migrating to Python 3.6
        data = json.loads(request.body)
        status = data["status"]
        if status == "enable" and company_disabled_package:
            company_disabled_package.delete()
        elif status == "disable" and not company_disabled_package:
            company_disabled_package = CompanyDisabledPackage(company=company,package=public_package)
            company_disabled_package.save()
        
        return HttpResponseRedirect(reverse('company', kwargs={"pk": company_pk}))

    return redirect_to_dashboard(current_user)

def send_data_form(request_object, current_user,email,state, bcc_requestor):
    status = request_object.get_request_status()
    if (status is not Status.NEW_STATUS and status is not Status.AWAITING_DATA_FORM_APPROVAL):
        return redirect_to_dashboard(current_user)

    if status is Status.NEW_STATUS:
        request_status = Status(content_object=request_object, status=Status.AWAITING_DATA_FORM_APPROVAL,
                                        datetime=datetime.datetime.now())

        request_status.save()

    if state in ["oklahoma","maine","massachusetts","minnesota"]:
        state = "default"

    elif state not in ["california","newyork","newjersey","washington"]:
        state = None


    send_data_form_email(email,request_object.created_by.company.name,state, 
        request_object.created_by.user.email if bcc_requestor is True else None)

    return HttpResponse("Successfully sent data form")

@login_required
def send_data_form_individual(request, pk):
    current_user = request.user
    if (request.method != 'POST' or not is_manager(current_user) or not request_is_valid(pk)):
        return redirect_to_dashboard(current_user)
    
    
    request_object = Request.objects.get(pk=pk)
    state =  (dict(US_STATES)[request_object.address.state].lower()).replace(" ","") if request_object.address is not None else None
    return send_data_form(request_object,current_user,request_object.email,state, json.loads(request.body)['bcc_requestor'])

@login_required
def send_data_form_corporate(request, pk):
    current_user = request.user
    if (request.method != 'POST' or not is_manager(current_user) or not corporate_request_is_valid(pk)):
        return redirect_to_dashboard(current_user)
    
    request_object = CorporateRequest.objects.get(pk=pk)
    
    return send_data_form(request_object,current_user,request_object.email, None, json.loads(request.body)['bcc_requestor'])

@login_required
def send_data_form_custom(request, pk):
    current_user = request.user
    if (request.method != 'POST' or not is_manager(current_user) or not custom_request_is_valid(pk)):
        return redirect_to_dashboard(current_user)
    
    request_object = CustomRequest.objects.get(pk=pk)
    
    return send_data_form(request_object,current_user, request_object.email, None, json.loads(request.body)['bcc_requestor'])

@login_required
def change_is_corporate_on_company(request, pk, is_corp):
    try:
        company = Company.objects.get(pk=pk)
        # Checks to see if the length of the class name is 7 which indicates a "checked" box.
        # If the box is checked then the is_corp field is set to True
        if is_corp == '7':
            company.is_corporate = True
        else:
            company.is_corporate = False
        print company.is_corporate
        company.save()
    except:
        pass

    if company.is_corporate:
        return HttpResponse("Access Granted")
    else:
        return HttpResponse("Access Restricted")

@login_required
def change_is_individual_on_company(request, pk, is_individual):
    try:
        company = Company.objects.get(pk=pk)
        # Checks to see if the length of the class name is 7 which indicates a "checked" box.
        # If the box is checked then the is_individual field is set to True
        if is_individual == '7':
            company.is_individual = True
        else:
            company.is_individual = False
        print company.is_individual
        company.save()
    except:
        pass

    if company.is_individual:
        return HttpResponse("Access Granted")
    else:
        return HttpResponse("Access Restricted")


@login_required
def company_dashboard(request):
    current_user = request.user
    if (is_manager(current_user)):
        companies =  Company.objects.extra(select={'case_insensitive_name': 'lower(name)'}).order_by('case_insensitive_name')
        return render(request, "core/company_dashboard.html", {"companies": companies})
    else:
        return redirect_to_dashboard(current_user)


#Add/Update Due Diligence Types ******************************

@login_required
def add_dd_type(request, pk):
    current_user = request.user
    if (not is_manager(current_user) or not company_is_valid(pk)):
        return redirect_to_dashboard(current_user)

    company = Company.objects.get(pk=pk)
    types = DueDiligenceType.objects.all()
    levels = CompanyDueDiligenceTypeSelection.TYPE_LEVEL_CHOICES

    hr_form = HumanResourcesTypeSelectionForm()
    investigative_form = InvestigativeTypeSelectionForm()
    regulatory_form = RegulatoryTypeSelectionForm()
    business_investment_form = BusinessInvestmentTypeSelectionForm()

    if (request.method == 'POST'):
        valid = False
        dd_type = None
        form = None
        if ('human_resources' in request.POST):
            dd_type = DueDiligenceType.objects.get(name="Pre-Employment")
            hr_form = HumanResourcesTypeSelectionForm(request.POST)
            form = hr_form
            if (hr_form.is_valid()):
                valid = True
        elif ('investigative' in request.POST):
            investigative_form = InvestigativeTypeSelectionForm(request.POST)
            form = investigative_form
            dd_type = DueDiligenceType.objects.get(name="Third Party")
            if (investigative_form.is_valid()):
                valid = True
        elif ('regulatory' in request.POST):
            regulatory_form = RegulatoryTypeSelectionForm(request.POST)
            form = regulatory_form
            dd_type = DueDiligenceType.objects.get(name="Background Investigations")
            if (regulatory_form.is_valid()):
                valid = True
        elif ('business_investment' in request.POST):
            business_investment_form = BusinessInvestmentTypeSelectionForm(request.POST)
            form = business_investment_form
            dd_type = DueDiligenceType.objects.get(name="Know Your Customer")
            if (business_investment_form.is_valid()):
                valid = True

        if (valid):
            name = form.cleaned_data['name']
            if name is None:
                name = ""
            services = form.cleaned_data['services']
            level = form.cleaned_data['levels']
            #comments = form.cleaned_data['comments']
            comments = ""
            price = form.cleaned_data['price']
            invoice_instructions = form.cleaned_data['invoice_instructions']
            is_active = form.cleaned_data['is_active']

            type_selection = CompanyDueDiligenceTypeSelection(due_diligence_type=dd_type, company=company, name=name,
                                                              comments=comments, level=level, price=price,
                                                              invoice_instructions=invoice_instructions,
                                                              is_active=is_active)
            type_selection.save()

            for service_name in services:
                service = Service.objects.get(name=service_name)
                service_selection = CompanyServiceSelection(dd_type=type_selection, service=service)
                service_selection.save()

            return HttpResponseRedirect(reverse('company', kwargs={"pk": company.pk}))

        return render(request, 'core/add_dd_type.html',
                      {'types': types, 'levels': levels, 'hr_form': hr_form, 'investigative_form': investigative_form,
                       "regulatory_form": regulatory_form, "business_investment_form": business_investment_form,
                       "selection_id": dd_type.id
                       })

    return render(request, 'core/add_dd_type.html',
                  {'types': types, 'levels': levels, 'hr_form': hr_form, 'investigative_form': investigative_form,
                   "regulatory_form": regulatory_form, "business_investment_form": business_investment_form,
                   "selection_id": None, "company_name": company.name
                   })


@login_required
def update_dd_type(request, company_pk, dd_pk):
    current_user = request.user
    if (not is_manager(current_user) or not company_is_valid(company_pk) or not dd_type_is_valid(dd_pk)):
        return redirect_to_dashboard(current_user)

    dd_type_selection = get_object_or_404(CompanyDueDiligenceTypeSelection, pk=dd_pk)
    company = Company.objects.get(pk=company_pk)
    types = DueDiligenceType.objects.all()
    levels = CompanyDueDiligenceTypeSelection.TYPE_LEVEL_CHOICES

    hr_form = HumanResourcesTypeSelectionForm()
    investigative_form = InvestigativeTypeSelectionForm()
    regulatory_form = RegulatoryTypeSelectionForm()
    business_investment_form = BusinessInvestmentTypeSelectionForm()

    valid = False
    dd_type = dd_type_selection.due_diligence_type
    form = None
    if (dd_type.name == 'Pre-Employment'):
        hr_form = HumanResourcesTypeSelectionForm(request.POST or None, instance=dd_type_selection)
        form = hr_form
        if (hr_form.is_valid()):
            valid = True
    elif (dd_type.name == 'Third Party'):
        investigative_form = InvestigativeTypeSelectionForm(request.POST or None, instance=dd_type_selection)
        form = investigative_form
        if (investigative_form.is_valid()):
            valid = True
    elif (dd_type.name == 'Background Investigations'):
        regulatory_form = RegulatoryTypeSelectionForm(request.POST or None, instance=dd_type_selection)
        form = regulatory_form
        if (regulatory_form.is_valid()):
            valid = True
    elif (dd_type.name == 'Know Your Customer'):
        business_investment_form = BusinessInvestmentTypeSelectionForm(request.POST or None, instance=dd_type_selection)
        form = business_investment_form
        if (business_investment_form.is_valid()):
            valid = True

    if (valid):
        name = form.cleaned_data['name']
        form_service_names = form.cleaned_data['services']
        level = form.cleaned_data['levels']
        #comments = form.cleaned_data['comments']
        comments = ""
        price = form.cleaned_data['price']
        invoice_instructions = form.cleaned_data['invoice_instructions']
        is_active = form.cleaned_data['is_active']

        dd_type_selection.name = name
        dd_type_selection.level = level
        dd_type_selection.comments = comments
        dd_type_selection.price = price
        dd_type_selection.invoice_intructions = invoice_instructions
        dd_type_selection.is_active = is_active
        dd_type_selection.save()

        saved_service_selections = CompanyServiceSelection.objects.filter(dd_type=dd_type_selection)
        saved_services = [service_selection.service for service_selection in saved_service_selections]
        form_services = Service.objects.filter(name__in=form_service_names)

        to_add = set(form_services) - set(saved_services)
        to_delete = set(saved_services) - set(form_services)
        for service_to_add in to_add:
            service_selection = CompanyServiceSelection(dd_type=dd_type_selection, service=service_to_add)
            service_selection.save()

        for service_to_delete in to_delete:
            saved_service_selections.get(service=service_to_delete).delete()

        return HttpResponseRedirect(reverse('company', kwargs={"pk": company.pk}))

    return render(request, 'core/add_dd_type.html',
                  {'types': types, 'levels': levels, 'hr_form': hr_form, 'investigative_form': investigative_form,
                   "regulatory_form": regulatory_form, "business_investment_form": business_investment_form,
                   "selection_id": dd_type.id
                   })


####################################
#
# EMPLOYEE VIEWS
#
####################################
@login_required
def employee_request_detail_view(request, pk):
    current_user = request.user
    if (not is_company_employee(current_user) or not request_is_valid(pk) or not employee_has_access_to_request(
            current_user, pk)):
        return redirect_to_dashboard(current_user)

    group = get_user_group(current_user)

    #make sure request exists
    try:
        request_object = Request.objects.get(pk=pk)
    except Request.DoesNotExist:
        return render(request, '404.html')

    request_status = request_object.get_request_status()
    request_submitted_date = Status.objects.filter(request=request_object).filter(
        status=Status.NEW_STATUS).first().datetime
    real_status = Status.get_request_status_for_group(group, request_status)

    status_comments_to_display = [Status.SUBMITTED_STATUS, Status.INCOMPLETE_STATUS]
    request_statuses_with_comments = Status.objects.filter(request=request_object).filter(
        status__in=status_comments_to_display).exclude(comments__exact='').order_by("-datetime")

    form = generate_form_for_detail_view(request, group, request_status, request_object, False)
    #Not showing surcharges at this time to clients
    formset = None
    response = handle_detail_view_post(request, form, formset, request_object, 'employee_dashboard')
    services = CompanyServiceSelection.objects.filter(dd_type=request_object.request_type)

    company_logo = None
    company = None
    try:
        company = CompanyEmployee.objects.get(user=current_user).company
    except:
        pass

    try:
        company_logo = company.logo
    except:
        pass

    custom_requests = None
    try:
        custom_requests = DynamicRequestForm.objects.filter(company=company)
    except:
        pass

    is_individual = None
    try:
        is_individual = company.is_individual
    except:
        pass

    is_corporate = None
    try:
        is_corporate = company.is_corporate
    except:
        pass

    is_custom = None
    try:
        is_custom = company.is_custom
    except:
        pass

    company_logo_active = company.company_logo_active

    restrict_attachments = False
    try:
        restrict_attachments = company.restrict_attachments
    except:
        pass

    if (response is not None):
        return response

    client_attachments = request_object.attachments.all()

    return render(request, 'core/request_detail_employee.html', {
        'request': request_object,
        'status': request_status,
        'real_status': real_status,
        'form': form,
        'submitted_date': request_submitted_date,
        'group_name': group.name,
        'comments': request_statuses_with_comments,
        "services": services,
        'company_logo_active': company_logo_active,
        'company_logo': company_logo,
        'is_corporate': False,
        'is_corporate_sidebar': is_corporate,
        'is_individual': is_individual,
        'is_custom_sidebar': is_custom,
        'custom_requests': custom_requests,
        'client_attachments': client_attachments,
        'restrict_attachments': restrict_attachments
    })

@login_required
def employee_request_for_corporate_detail_view(request, pk):
    current_user = request.user
    if not is_company_employee(current_user) or not corporate_request_is_valid(
            pk) or not employee_has_access_to_request_for_corporate(current_user, pk):
        return redirect_to_dashboard(current_user)

    group = get_user_group(current_user)

    #make sure request exists
    try:
        request_object = CorporateRequest.objects.get(pk=pk)
    except CorporateRequest.DoesNotExist:
        return render(request, '404.html')

    request_status = request_object.get_request_status()
    request_submitted_date = Status.objects.filter(corporate_request=request_object).filter(
        status=Status.NEW_STATUS).first().datetime
    real_status = Status.get_request_status_for_group(group, request_status)

    status_comments_to_display = [Status.SUBMITTED_STATUS, Status.INCOMPLETE_STATUS]
    request_statuses_with_comments = Status.objects.filter(corporate_request=request_object).filter(
        status__in=status_comments_to_display).exclude(comments__exact='').order_by("-datetime")

    form = generate_form_for_detail_view(request, group, request_status, request_object, False)
    #Not showing surcharges at this time to clients
    formset = None
    response = handle_detail_view_post(request, form, formset, request_object, 'employee_dashboard')
    services = CompanyServiceSelection.objects.filter(dd_type=request_object.request_type)

    # fix the attachment name

    company_logo = None
    company = None
    try:
        company = CompanyEmployee.objects.get(user=current_user).company
    except:
        pass

    try:
        company_logo = company.logo
    except:
        pass

    custom_requests = None
    try:
        custom_requests = DynamicRequestForm.objects.filter(company=company)
    except:
        pass

    is_individual = None
    try:
        is_individual = company.is_individual
    except:
        pass

    is_corporate = None
    try:
        is_corporate = company.is_corporate
    except:
        pass

    is_custom = None
    try:
        is_custom = company.is_custom
    except:
        pass

    company_logo_active = company.company_logo_active

    if (response is not None):
        return response

    restrict_attachments = False
    try:
        restrict_attachments = company.restrict_attachments
    except:
        pass

    client_attachments = request_object.attachments.all()

    return render(request, 'core/request_detail_employee.html', {
        'request': request_object,
        'status': request_status,
        'real_status': real_status,
        'form': form,
        'submitted_date': request_submitted_date,
        'company_logo_active': company_logo_active,
        'company_logo': company_logo,
        'is_corporate': True,
        'is_corporate_sidebar': is_corporate,
        'is_individual': is_individual,
        'is_custom_sidebar': is_custom,
        'is_custom': False,
        'custom_requests':custom_requests,
        'services': services,
        'client_attachments':client_attachments,
        'restrict_attachments': restrict_attachments

    })

@login_required
def employee_custom_request_detail_view(request, pk):
    current_user = request.user
    if not is_company_employee(current_user) or not custom_request_is_valid(pk) \
            or not employee_has_access_to_custom_request(current_user, pk):
        return redirect_to_dashboard(current_user)

    group = get_user_group(current_user)

    try:
        custom_request = CustomRequest.objects.get(pk=pk)
    except CustomRequest.DoesNotExist:
        return render(request, '404.html')

    try:
        fields = CustomRequestFields.objects.filter(custom_request=custom_request)
    except CustomRequestFields.DoesNotExist:
        return render(request, '404.html')

    request_status = custom_request.get_request_status()
    request_submitted_date = Status.objects.filter(custom_request=custom_request).filter(
        status=Status.NEW_STATUS).first().datetime
    real_status = Status.get_request_status_for_group(group, request_status)

    status_comments_to_display = [Status.SUBMITTED_STATUS, Status.INCOMPLETE_STATUS]
    request_statuses_with_comments = Status.objects.filter(custom_request=custom_request).filter(
        status__in=status_comments_to_display).exclude(comments__exact='').order_by("-datetime")

    form = generate_form_for_detail_view(request, group, request_status, custom_request, False)
    #Not showing surcharges at this time to clients
    formset = None
    response = handle_detail_view_post(request, form, formset, custom_request, 'employee_dashboard')
    services = CompanyServiceSelection.objects.filter(dd_type=custom_request.request_type)

    client_attachments = custom_request.attachments.all()

    company_logo = None
    company = None
    try:
        company = CompanyEmployee.objects.get(user=current_user).company
    except:
        pass

    try:
        company_logo = company.logo
    except:
        pass

    custom_requests = None
    try:
        custom_requests = DynamicRequestForm.objects.filter(company=company)
    except:
        pass

    is_individual = None
    try:
        is_individual = company.is_individual
    except:
        pass

    is_corporate = None
    try:
        is_corporate = company.is_corporate
    except:
        pass

    is_custom = None
    try:
        is_custom = company.is_custom
    except:
        pass

    company_logo_active = company.company_logo_active

    restrict_attachments = False
    try:
        restrict_attachments = company.restrict_attachments
    except:
        pass

    if (response is not None):
        return response

    return render(request, 'core/request_detail_employee.html', {
        'request': custom_request,
        'status': request_status,
        'real_status': real_status,
        'form': form,
        'submitted_date': request_submitted_date,
        'group_name': group.name,
        'comments': request_statuses_with_comments,
        "services": services,
        'company_logo_active': company_logo_active,
        'company_logo': company_logo,
        'is_custom_sidebar': is_custom,
        'is_custom': is_custom,
        'is_individual': is_individual,
        'is_corporate_sidebar': is_corporate,
        'fields': fields,
        'custom_requests': custom_requests,
        'client_attachments': client_attachments,
        'restrict_attachments': restrict_attachments
    })

@login_required
def employee_dashboard(request):
    current_user = request.user

    if (is_company_employee(current_user)):
        employee = CompanyEmployee.objects.get(user=current_user)


        company_logo = None
        company = None
        try:
            company = CompanyEmployee.objects.get(user=current_user).company
        except:
            pass

        try:
            company_logo = company.logo
        except:
            pass

        is_corporate = None
        try:
            is_corporate = company.is_corporate
        except:
            pass

        is_individual = None
        try:
            is_individual = company.is_individual
        except:
            pass

        custom_requests = None
        try:
            custom_requests = DynamicRequestForm.objects.filter(company=company)
        except:
            pass

        is_custom = None
        try:
            is_custom = company.is_custom
        except:
            pass

        company_logo_active = company.company_logo_active

        restrict_attachments = False
        try:
            restrict_attachments = company.restrict_attachments
        except:
            pass

        #total_notifications = num_completed + num_incomplete
        return render(request, "core/employee_dashboard.html", {
            'company_logo_active': company_logo_active,
            'company_logo': company_logo,
            'is_corporate': is_corporate,
            'is_corporate_sidebar': is_corporate,
            'is_individual': is_individual,
            'is_custom': is_custom,
            'is_custom_sidebar': is_custom,
            'custom_requests': custom_requests,
            'restrict_attachments': restrict_attachments,
        })



    else:
        return redirect_to_dashboard(current_user)

@login_required
def advanced_search_employee(request):
    current_user = request.user
    employee = get_company_employee(current_user)
    company = employee.company.name



    request_types = ['request', 'customrequest', 'corporaterequest']


    if(is_company_employee(current_user)):
        company_object = CompanyEmployee.objects.get(user=current_user).company
        try:
            company_logo = CompanyEmployee.objects.get(user=current_user).company.logo
        except:
            pass

        is_corporate = None

        try:
            is_corporate = company_object.is_corporate
        except:
            pass

        is_individual = None
        try:
            is_individual = company_object.is_individual
        except:
            pass

        custom_requests = None
        try:
            custom_requests = DynamicRequestForm.objects.filter(company=employee.company)
        except:
            pass

        is_custom = None
        try:
            is_custom = company_object.is_custom
        except:
            pass

        company_logo_active = company_object.company_logo_active
        analysts = SpotLitStaff.get_analysts(True)
        statuses = Status.SUPERVISOR_REQUEST_STATUS_CHOICES
        types = CompanyDueDiligenceTypeSelection.objects.filter(company__name=company)
        dynamic_forms = DynamicRequestForm.objects.filter(company__name=company)
        fields = DynamicRequestFormFields.objects.filter(dynamic_request_form__in=dynamic_forms,dynamic_request_form__render_form=True, archive=False)

        return render(request, "core/advanced_search_employee.html", {
            'analysts': analysts,
            'company': employee.company,
            'company_logo_active': company_logo_active,
            'company_logo': company_logo,
            'custom_requests': custom_requests,
            'dynamic_forms': dynamic_forms,
            'fields': fields,
            'is_corporate': is_corporate,
            'is_corporate_sidebar': is_corporate,
            'is_custom_sidebar': is_custom,
            'is_individual': is_individual,
            'is_custom': is_custom,
            'request_types': request_types,
            'statuses': statuses,
            'types': types,
        })
    else:
        return redirect_to_dashboard(reverse_lazy('advanced_search_employee'))



class EmployeeRequestExport(EmployeeOnlyMixin,generic.View):

    def apply_filters_on_export_requests(self,filters,statuses):
        # ID
        id_search = filters["requestId"]
        if (len(id_search) > 0):
            cust_id_filt = statuses.filter(custom_request__display_id__icontains=id_search)
            corp_id_filt = statuses.filter(corporate_request__display_id__icontains=id_search)
            ind_id_filt = statuses.filter(request__display_id__icontains=id_search)
            statuses = cust_id_filt | corp_id_filt | ind_id_filt

        name_search = filters["name"]
        if len(name_search) > 0:
            cust_names = statuses.filter(custom_request__name__icontains=name_search)
            corp_names = statuses.filter(corporate_request__company_name__icontains=name_search)
            ind_first = statuses.filter(request__first_name__icontains=name_search)
            ind_last = statuses.filter(request__last_name__icontains=name_search)
            statuses = cust_names | corp_names | ind_first | ind_last



        # STATUS
        status_search = filters["statusType"]
        supervisor_search_statuses = []
        if (len(status_search) > 0):
            if int(status_search) == Status.IN_PROGRESS_STATUS:
                supervisor_search_statuses = [1, 2, 3]
            elif int(status_search) == Status.SUBMITTED_STATUS:
                supervisor_search_statuses = [Status.SUBMITTED_STATUS]
            elif int(status_search) == Status.INCOMPLETE_STATUS:
                supervisor_search_statuses = [Status.INCOMPLETE_STATUS]
            elif int(status_search) == Status.DELETED_STATUS:
                supervisor_search_statuses = [Status.DELETED_STATUS]

            statuses = statuses.filter(status__in=supervisor_search_statuses)

        # TYPE
        type_search = filters["type"]
        if (len(type_search) > 0):
            dd_type_selection = CompanyDueDiligenceTypeSelection.objects.get(id=type_search)
            if (dd_type_selection.name == ""):
                level = dd_type_selection.level
                dd_type = dd_type_selection.due_diligence_type
                cust_dd_ids = statuses.filter(custom_request__request_type__level=level).filter(
                    custom_request__request_type__due_diligence_type=dd_type).values_list('id', flat=True)

                corp_dd_ids = statuses.filter(corporate_request__request_type__level=level).filter(
                    corporate_request__request_type__due_diligence_type=dd_type).values_list('id', flat=True)

                ind_dd_ids = statuses.filter(request__request_type__level=level).filter(
                    request__request_type__due_diligence_type=dd_type).values_list('id', flat=True)

                comb_dd_ids = list(chain(cust_dd_ids, corp_dd_ids, ind_dd_ids))

                statuses = statuses.filter(id__in=comb_dd_ids)

            else:
                cust_dd_ids = statuses.filter(
                    custom_request__request_type__id=type_search).values_list('id', flat=True)

                corp_dd_ids = statuses.filter(
                    corporate_request__request_type__id=type_search).values_list('id', flat=True)

                ind_dd_ids = statuses.filter(
                    request__request_type__id=type_search).values_list('id', flat=True)

                comp_dd_ids = list(chain(cust_dd_ids, corp_dd_ids, ind_dd_ids))

                statuses = statuses.filter(id__in=comp_dd_ids)

        # START DATE
        start_end_date = filters["startEndDate"]
        if (len(start_end_date) > 3):
            array = start_end_date.split('+')
            start = fix_start(array[0])
            end = fix_end(array[1])
            statuses = statuses.filter(datetime__range=[start, end])
        
        # CUSTOM FIELD
        custom_field = filters["customFieldId"]
        if (len(custom_field) > 0):
            field_ids = list(
                CustomRequestFields.objects.filter(custom_request__dynamic_request_form__render_form=True,
                                                    form_field__id=custom_field).exclude(
                    value__isnull=True).exclude(value__exact='').values_list('custom_request__id', flat=True))

            statuses = statuses.filter(custom_request__id__in=field_ids)


        # CUSTOM FIELD VALUE
        custom_field_value = filters["customFieldValue"]
        if (len(custom_field_value) > 0):
            field_ids = list(
                CustomRequestFields.objects.filter(custom_request__dynamic_request_form__render_form=True,
                                                    value__icontains=custom_field_value).values_list(
                                                    'custom_request__id', flat=True))
            statuses = statuses.filter(custom_request__id__in=field_ids)

        # FORM NAME
        dynamic_request_form_id = filters["customFormTypeId"]
        if (len(dynamic_request_form_id) > 0):
            statuses = statuses.filter(custom_request__dynamic_request_form__id=dynamic_request_form_id)


        # REQUEST TYPE
        request_type = filters["requestType"]
        if len(request_type) > 0:
            statuses = statuses.filter(content_type__model=request_type)
        
        return statuses

    def get_populated_request_dict(self,statuses):
        populated_statuses = []
        custom_dynamic_columns = []
        for status in statuses:
            populated = {}
            main_request = None
            if status["content_type__model"] == "request":
                request = Request.objects.get(pk=status["object_id"])
                main_request= request
                populated["Display ID"] = request.display_id
                populated["Name"] = request.first_name + request.last_name
                populated["Request Type"] = request.request_type.__unicode__()


            elif status["content_type__model"] == "corporaterequest":
                corporate_request = CorporateRequest.objects.get(pk=status["object_id"])
                main_request = corporate_request
                populated["Display ID"] = corporate_request.display_id
                populated["Name"] = corporate_request.company_name
                populated["Request Type"] = corporate_request.request_type.__unicode__()
                
            elif status["content_type__model"] == "customrequest":
                custom_request = CustomRequest.objects.get(pk=status["object_id"])
                main_request = custom_request
                populated["Display ID"] = custom_request.display_id
                populated["Name"] = custom_request.name
                populated["Request Type"] = custom_request.request_type.__unicode__()
                custom_fields =  CustomRequestFields.objects.filter(custom_request=custom_request)
                for custom_field in custom_fields:
                    label = "Custom-" + custom_field.form_field.label
                    value = custom_field.value
                    
                    if label not in custom_dynamic_columns:
                        custom_dynamic_columns.append(label)
                    populated[label] = value

                
        
            if status['status'] == 1 or status['status'] == 2:
                populated['Status'] = 'New'
            elif status['status'] == 3:
                populated['Status'] = 'In Progress'
                populated['Start Date'] = formats.date_format(main_request.get_in_progress_request_status().datetime.astimezone(timezone('US/Eastern')), "SHORT_DATETIME_FORMAT")
            elif status['status'] == 4:
                populated['Status'] = 'Completed'
                populated['Start Date'] = formats.date_format(main_request.get_in_progress_request_status().datetime.astimezone(timezone('US/Eastern')), "SHORT_DATETIME_FORMAT")
            elif status['status'] == 5:
                populated['Status'] = 'Submitted'
                populated['Start Date'] = formats.date_format(main_request.get_in_progress_request_status().datetime.astimezone(timezone('US/Eastern')), "SHORT_DATETIME_FORMAT")
            elif status['status'] == 6:
                try:
                    populated['Status'] = 'In Progress'
                    populated['Start Date'] = formats.date_format(main_request.get_in_progress_request_status().datetime.astimezone(timezone('US/Eastern')), "SHORT_DATETIME_FORMAT")
                except:
                    populated['Status'] = 'New'

            else:
                populated['Status'] = Status.SUPERVISOR_STATUS_CHOICES.get(status['status'])

            
            populated_statuses.append(populated)

        return populated_statuses, custom_dynamic_columns


    def post(self,request):
        data = json.loads(request.body)
        ids = list(Status.get_all_current_ids_queryset_for_user(request.user))
        statuses = Status.objects.filter(id__in=ids).values("content_type__model","object_id","status")
        statuses = self.apply_filters_on_export_requests(data,statuses)
        statuses, custom_dynamic_columns = self.get_populated_request_dict(statuses)

        fieldnames = ["Display ID","Name","Status","Start Date","Request Type"] + custom_dynamic_columns
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="request_advanced_search.csv"'

        writer = csv.DictWriter(response, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(statuses)
        return response


####################################
#
# SUPERVISOR VIEWS
#
####################################

@login_required
def supervisor_custom_request_detail_view(request, pk):
    current_user = request.user
    supervisor = get_company_employee(current_user)
    company = supervisor.company.name
    company_object = CompanyEmployee.objects.get(user=current_user).company

    if not is_company_supervisor(supervisor) or not custom_request_is_valid(pk):
        return redirect_to_dashboard(current_user)

    group = get_user_group(current_user)

    try:
        custom_request = CustomRequest.objects.get(pk=pk)
    except CustomRequest.DoesNotExist:
        return render(request, '404.html')

    try:
        fields = CustomRequestFields.objects.filter(custom_request=custom_request)
    except CustomRequestFields.DoesNotExist:
        return render(request, '404.html')

    request_status = custom_request.get_request_status()
    request_submitted_date = Status.objects.filter(custom_request=custom_request).filter(
        status=Status.NEW_STATUS).first().datetime
    real_status = Status.get_request_status_for_group(group, request_status)

    status_comments_to_display = [Status.SUBMITTED_STATUS, Status.INCOMPLETE_STATUS]
    request_statuses_with_comments = Status.objects.filter(custom_request=custom_request).filter(
        status__in=status_comments_to_display).exclude(comments__exact='').order_by("-datetime")

    form = generate_form_for_detail_view(request, group, request_status, custom_request, False)
    #Not showing surcharges at this time to clients
    formset = None
    response = handle_detail_view_post(request, form, formset, custom_request, 'supervisor_dashboard')
    services = CompanyServiceSelection.objects.filter(dd_type=custom_request.request_type)

    client_attachments = custom_request.attachments.all()

    employees = get_company_employees(company)


    company_logo = None
    company = None
    try:
        company = CompanyEmployee.objects.get(user=current_user).company
    except:
        pass

    try:
        company_logo = company.logo
    except:
        pass

    custom_requests = None
    try:
        custom_requests = DynamicRequestForm.objects.filter(company=supervisor.company)
    except:
        pass

    is_corporate = None
    try:
        is_corporate = company.is_corporate
    except:
        pass

    is_individual = None
    try:
        is_individual = company.is_individual
    except:
        pass

    is_custom = None
    try:
        is_custom = company.is_custom
    except:
        pass

    if (response is not None):
        return response

    company_logo_active = company_object.company_logo_active

    return render(request, 'core/request_detail_supervisor.html', {
        'request': custom_request, 'status': request_status, 'real_status': real_status, 'form': form,
        'submitted_date': request_submitted_date,
        'group_name': group.name, 'comments': request_statuses_with_comments, "services": services,
        'company_logo_active': company_logo_active,
        'is_corporate': False,
        'company_logo': company_logo, 'is_custom': is_custom, 'is_individual': is_individual, 'is_corporate_sidebar':is_corporate,
        'is_custom_sidebar':is_custom,
        'fields':fields, 'custom_requests': custom_requests,
        'employees': employees, 'client_attachments': client_attachments
    })


@login_required
def supervisor_corporate_request_for_detail_view(request, pk):
    current_user = request.user
    supervisor = get_company_employee(current_user)
    company = supervisor.company.name
    company_object = CompanyEmployee.objects.get(user=current_user).company

    if not is_company_supervisor(supervisor) or not corporate_request_is_valid(
            pk):
        return redirect_to_dashboard(current_user)

    group = get_user_group(current_user)


    #make sure request exists
    try:
        request_object = CorporateRequest.objects.get(pk=pk)
    except CorporateRequest.DoesNotExist:
        return render(request, '404.html')

    request_status = request_object.get_request_status()
    request_submitted_date = Status.objects.filter(corporate_request=request_object).filter(
        status=Status.NEW_STATUS).first().datetime
    real_status = Status.get_request_status_for_group(group, request_status)

    status_comments_to_display = [Status.SUBMITTED_STATUS, Status.INCOMPLETE_STATUS]
    request_statuses_with_comments = Status.objects.filter(corporate_request=request_object).filter(
        status__in=status_comments_to_display).exclude(comments__exact='').order_by("-datetime")

    form = generate_form_for_detail_view(request, group, request_status, request_object, False)
    #Not showing surcharges at this time to clients
    formset = None
    response = handle_detail_view_post(request, form, formset, request_object, 'supervisor_dashboard')
    services = CompanyServiceSelection.objects.filter(dd_type=request_object.request_type)

    employees = get_company_employees(company)

    company_logo = None
    try:
        company_logo = CompanyEmployee.objects.get(user=current_user).company.logo
    except:
        pass

    custom_requests = None
    try:
        custom_requests = DynamicRequestForm.objects.filter(company=supervisor.company)
    except:
        pass

    is_individual = None
    try:
        is_individual = company_object.is_individual
        print is_individual
    except:
        pass

    is_corporate = None
    try:
        is_corporate = company_object.is_corporate
    except:
        pass

    is_custom = None
    try:
        is_custom = company_object.is_custom
    except:
        pass

    company_logo_active = company_object.company_logo_active

    if (response is not None):
        return response

    client_attachments = request_object.attachments.all()

    return render(request, 'core/request_detail_supervisor.html', {
        'request': request_object,
        'status': request_status,
        'real_status': real_status,
        "employees": employees,
        'form': form,
        'submitted_date': request_submitted_date,
        'group_name': group.name,
        'comments': request_statuses_with_comments,
        "services": services,
        'company_logo_active': company_logo_active,
        'company_logo': company_logo,
        'is_corporate': True,
        'is_corporate_sidebar': is_corporate,
        'is_individual': is_individual,
        'is_custom': False,
        'is_custom_sidebar': is_custom,
        'custom_requests': custom_requests,
        'client_attachments':client_attachments
    })


@login_required
def supervisor_request_detail_view(request, pk):
    current_user = request.user
    supervisor = get_company_employee(current_user)
    company = supervisor.company.name
    company_object = CompanyEmployee.objects.get(user=current_user).company

    if (not is_company_supervisor(supervisor) or not request_is_valid(pk)):
        return redirect_to_dashboard(current_user)

    group = get_user_group(current_user)

    #make sure request exists
    try:
        request_object = Request.objects.get(pk=pk)
    except Request.DoesNotExist:
        return render(request, '404.html')

    request_status = request_object.get_request_status()
    request_submitted_date = Status.objects.filter(request=request_object).filter(
        status=Status.NEW_STATUS).first().datetime
    
    real_status = Status.get_request_status_for_group(group, request_status)

    status_comments_to_display = [Status.SUBMITTED_STATUS, Status.INCOMPLETE_STATUS]
    request_statuses_with_comments = Status.objects.filter(request=request_object).filter(
        status__in=status_comments_to_display).exclude(comments__exact='').order_by("-datetime")

    form = generate_form_for_detail_view(request, group, request_status, request_object, False)
    #Not showing surcharges at this time to clients
    formset = None
    response = handle_detail_view_post(request, form, formset, request_object, 'supervisor_dashboard')
    services = CompanyServiceSelection.objects.filter(dd_type=request_object.request_type)
    employees = get_company_employees(company)


    company_logo = None
    try:
        company_logo = CompanyEmployee.objects.get(user=current_user).company.logo
    except:
        pass

    custom_requests = None
    try:
        custom_requests = DynamicRequestForm.objects.filter(company=supervisor.company)
    except:
        pass

    is_individual = None
    try:
        is_individual = company_object.is_individual
    except:
        pass

    is_corporate = None
    try:
        is_corporate = company_object.is_corporate
    except:
        pass

    is_custom = None
    try:
        is_custom = company_object.is_custom
    except:
        pass

    company_logo_active = company_object.company_logo_active


    client_attachments = request_object.attachments.all()


    if (response is not None):
        return response

    return render(request, 'core/request_detail_supervisor.html', {
        'request': request_object,
        'status': request_status,
        'real_status': real_status,
        "employees": employees,
        'form': form,
        'submitted_date': request_submitted_date,
        'group_name': group.name,
        'comments': request_statuses_with_comments,
        "services": services,
        'company_logo_active': company_logo_active,
        'company_logo': company_logo,
        'is_corporate': False,
        'is_corporate_sidebar': is_corporate,
        'is_individual': is_individual,
        'is_custom': False,
        'is_custom_sidebar': is_custom,
        'custom_requests': custom_requests,
        'client_attachments': client_attachments
    })


@login_required
def supervisor_dashboard(request):
    current_user = request.user
    supervisor = get_company_employee(current_user)
    company = supervisor.company.name
    company_object = CompanyEmployee.objects.get(user=current_user).company
    if(is_company_supervisor(supervisor)):

        try:
            company_logo = CompanyEmployee.objects.get(user=current_user).company.logo
        except:
            pass

        is_corporate = None

        try:
            is_corporate = company_object.is_corporate
        except:
            pass

        is_individual = None
        try:
            is_individual = company_object.is_individual
        except:
            pass

        custom_requests = None
        try:
            custom_requests = DynamicRequestForm.objects.filter(company=supervisor.company)
        except:
            pass

        is_custom = None
        try:
            is_custom = company_object.is_custom
        except:
            pass
        company_logo_active = company_object.company_logo_active
        analysts = SpotLitStaff.get_analysts()
        return render(request, "core/supervisor_dashboard.html", {
            'company_logo_active': company_logo_active,
            'company_logo': company_logo,
            'is_corporate': is_corporate,
            'is_corporate_sidebar': is_corporate,
            'is_custom_sidebar': is_custom,
            'is_individual': is_individual,
            'is_custom': is_custom,
            'analysts': analysts,
            'custom_requests': custom_requests,
            'supervisor': supervisor,
            'company': supervisor.company,
        })


    else:
        return redirect_to_dashboard(current_user)


@login_required
def advanced_search_supervisor(request):
    current_user = request.user
    supervisor = get_company_employee(current_user)
    company = supervisor.company.name
    company_object = CompanyEmployee.objects.get(user=current_user).company


    request_types = ['request', 'customrequest', 'corporaterequest']


    if(is_company_supervisor(supervisor)):

        try:
            company_logo = CompanyEmployee.objects.get(user=current_user).company.logo
        except:
            pass

        is_corporate = None

        try:
            is_corporate = company_object.is_corporate
        except:
            pass

        is_individual = None
        try:
            is_individual = company_object.is_individual
        except:
            pass

        custom_requests = None
        try:
            custom_requests = DynamicRequestForm.objects.filter(company=supervisor.company)
        except:
            pass

        is_custom = None
        try:
            is_custom = company_object.is_custom
        except:
            pass

        company_logo_active = company_object.company_logo_active
        statuses = Status.SUPERVISOR_REQUEST_STATUS_CHOICES
        types = CompanyDueDiligenceTypeSelection.objects.filter(company__name=company)
        dynamic_forms = DynamicRequestForm.objects.filter(company__name=company)
        fields = DynamicRequestFormFields.objects.filter(dynamic_request_form__in=dynamic_forms,dynamic_request_form__render_form=True, archive=False)



        company_employees = CompanyEmployee.get_company_employees(company)

        return render(request, "core/advanced_search_supervisor.html", {
            'company': supervisor.company,
            'company_employees':company_employees,
            'company_logo_active': company_logo_active,
            'company_logo': company_logo,
            'custom_requests': custom_requests,
            'dynamic_forms': dynamic_forms,
            'fields': fields,
            'is_corporate': is_corporate,
            'is_corporate_sidebar': is_corporate,
            'is_custom_sidebar': is_custom,
            'is_individual': is_individual,
            'is_custom': is_custom,
            'request_types': request_types,
            'supervisor': supervisor,
            'statuses': statuses,
            'types': types,
        })
    else:
        return redirect_to_dashboard(reverse_lazy('advanced_search_supervisor'))


@login_required
def supervisor_report_download(request):
    current_user = request.user
    supervisor = get_company_employee(current_user)
    company = supervisor.company.name
    company_object = CompanyEmployee.objects.get(user=current_user).company

    if (request.method == 'POST'):
        data = request.POST['requests']
        request_ids = json.loads(data)
        request_type = request.POST['request_type']

        if request_type == "customrequest":
            print "hitting supervisor_report_download"
            zip_custom_requests.delay(request_ids, supervisor)
        elif request_type == "request":
            zip_individual_requests.delay(request_ids, supervisor)
        elif request_type == "corporaterequest":
            zip_corporate_requests.delay(request_ids, supervisor)

    request_types = ['request', 'customrequest', 'corporaterequest']

    if is_company_supervisor(supervisor):

        try:
            company_logo = CompanyEmployee.objects.get(user=current_user).company.logo
        except:
            pass

        is_corporate = None

        try:
            is_corporate = company_object.is_corporate
        except:
            pass

        is_individual = None
        try:
            is_individual = company_object.is_individual
        except:
            pass

        custom_requests = None
        try:
            custom_requests = DynamicRequestForm.objects.filter(company=supervisor.company)
        except:
            pass

        is_custom = None
        try:
            is_custom = company_object.is_custom
        except:
            pass

        company_logo_active = company_object.company_logo_active
        statuses = Status.SUPERVISOR_REQUEST_STATUS_CHOICES
        types = CompanyDueDiligenceTypeSelection.objects.filter(company__name=company)
        dynamic_forms = DynamicRequestForm.objects.filter(company__name=company)
        fields = DynamicRequestFormFields.objects.filter(dynamic_request_form__in=dynamic_forms,dynamic_request_form__render_form=True, archive=False)

        company_employees = CompanyEmployee.get_company_employees(company)

        return render(request, "core/supervisor_report_download.html", {
            'company': supervisor.company,
            'company_employees': company_employees,
            'company_logo_active': company_logo_active,
            'company_logo': company_logo,
            'custom_requests': custom_requests,
            'dynamic_forms': dynamic_forms,
            'fields': fields,
            'is_corporate': is_corporate,
            'is_corporate_sidebar': is_corporate,
            'is_custom_sidebar': is_custom,
            'is_individual': is_individual,
            'is_custom': is_custom,
            'request_types': request_types,
            'supervisor': supervisor,
            'statuses': statuses,
            'types': types,
        })
    else:
        return redirect_to_dashboard(reverse_lazy('advanced_search_supervisor'))


# @login_required
# def supervisor_archives_view(request):
#     return render(request, "core/supervisor_archives_view.html")
@login_required
def supervisor_archives_view(request):
    current_user = request.user
    supervisor = get_company_employee(current_user)
    company = supervisor.company.name
    company_object = CompanyEmployee.objects.get(user=current_user).company
    if(is_company_supervisor(supervisor)):

        try:
            company_logo = CompanyEmployee.objects.get(user=current_user).company.logo
        except:
            pass

        is_corporate = None

        try:
            is_corporate = company_object.is_corporate
        except:
            pass

        is_individual = None
        try:
            is_individual = company_object.is_individual
        except:
            pass

        custom_requests = None
        try:
            custom_requests = DynamicRequestForm.objects.filter(company=supervisor.company)
        except:
            pass

        is_custom = None
        try:
            is_custom = company_object.is_custom
        except:
            pass
        company_logo_active = company_object.company_logo_active
        analysts = SpotLitStaff.get_analysts()
        return render(request, "core/supervisor_archives_view.html", {
            'company_logo_active': company_logo_active,
            'company_logo': company_logo,
            'is_corporate': is_corporate,
            'is_corporate_sidebar': is_corporate,
            'is_custom_sidebar': is_custom,
            'is_individual': is_individual,
            'is_custom': is_custom,
            'custom_requests': custom_requests,
            'supervisor': supervisor,
            'company': supervisor.company,
        })

    else:
        return redirect_to_dashboard(current_user)


@login_required
def get_supervisor_archives_json(request):
    current_user = request.user
    supervisor = get_company_employee(current_user)
    company = supervisor.company
    archives = RequestArchive.get_company_archives(company)
    archives_json = [archive.as_json() for archive in archives]
    return JsonResponse(archives_json, safe=False)




class SupervisorRequestExport(SupervisorOnlyMixin,generic.View):

    def apply_filters_on_export_requests(self,filters,statuses):
        # ID
        id_search = filters["requestId"]
        if (len(id_search) > 0):
            cust_id_filt = statuses.filter(custom_request__display_id__icontains=id_search)
            corp_id_filt = statuses.filter(corporate_request__display_id__icontains=id_search)
            ind_id_filt = statuses.filter(request__display_id__icontains=id_search)
            statuses = cust_id_filt | corp_id_filt | ind_id_filt
        
        # company
        created_by_id = filters["createdById"]
        if (len(created_by_id) > 0):
            cust_ids = statuses.filter(custom_request__created_by__user__id=created_by_id).values_list('id', flat=True)
            corp_ids = statuses.filter(corporate_request__created_by__user__id=created_by_id).values_list('id', flat=True)
            ind_ids = statuses.filter(request__created_by__user__id=created_by_id).values_list('id', flat=True)
            comb_ids = list(chain(cust_ids, corp_ids, ind_ids))
            statuses = statuses.filter(id__in=comb_ids)


        name_search = filters["name"]
        if len(name_search) > 0:
            cust_names = statuses.filter(custom_request__name__icontains=name_search)
            corp_names = statuses.filter(corporate_request__company_name__icontains=name_search)
            ind_first = statuses.filter(request__first_name__icontains=name_search)
            ind_last = statuses.filter(request__last_name__icontains=name_search)
            statuses = cust_names | corp_names | ind_first | ind_last



        # STATUS
        status_search = filters["statusType"]
        supervisor_search_statuses = []
        if (len(status_search) > 0):
            if int(status_search) == Status.IN_PROGRESS_STATUS:
                supervisor_search_statuses = [1, 2, 3]
            elif int(status_search) == Status.SUBMITTED_STATUS:
                supervisor_search_statuses = [Status.SUBMITTED_STATUS]
            elif int(status_search) == Status.INCOMPLETE_STATUS:
                supervisor_search_statuses = [Status.INCOMPLETE_STATUS]
            elif int(status_search) == Status.DELETED_STATUS:
                supervisor_search_statuses = [Status.DELETED_STATUS]

            statuses = statuses.filter(status__in=supervisor_search_statuses)

        # TYPE
        type_search = filters["type"]
        if (len(type_search) > 0):
            dd_type_selection = CompanyDueDiligenceTypeSelection.objects.get(id=type_search)
            if (dd_type_selection.name == ""):
                level = dd_type_selection.level
                dd_type = dd_type_selection.due_diligence_type
                cust_dd_ids = statuses.filter(custom_request__request_type__level=level).filter(
                    custom_request__request_type__due_diligence_type=dd_type).values_list('id', flat=True)

                corp_dd_ids = statuses.filter(corporate_request__request_type__level=level).filter(
                    corporate_request__request_type__due_diligence_type=dd_type).values_list('id', flat=True)

                ind_dd_ids = statuses.filter(request__request_type__level=level).filter(
                    request__request_type__due_diligence_type=dd_type).values_list('id', flat=True)

                comb_dd_ids = list(chain(cust_dd_ids, corp_dd_ids, ind_dd_ids))

                statuses = statuses.filter(id__in=comb_dd_ids)

            else:
                cust_dd_ids = statuses.filter(
                    custom_request__request_type__id=type_search).values_list('id', flat=True)

                corp_dd_ids = statuses.filter(
                    corporate_request__request_type__id=type_search).values_list('id', flat=True)

                ind_dd_ids = statuses.filter(
                    request__request_type__id=type_search).values_list('id', flat=True)

                comp_dd_ids = list(chain(cust_dd_ids, corp_dd_ids, ind_dd_ids))

                statuses = statuses.filter(id__in=comp_dd_ids)

        # START DATE
        start_end_date = filters["startEndDate"]
        if (len(start_end_date) > 3):
            array = start_end_date.split('+')
            start = fix_start(array[0])
            end = fix_end(array[1])
            statuses = statuses.filter(datetime__range=[start, end])
        
        # CUSTOM FIELD
        custom_field = filters["customFieldId"]
        if (len(custom_field) > 0):
            field_ids = list(
                CustomRequestFields.objects.filter(custom_request__dynamic_request_form__render_form=True,
                                                    form_field__id=custom_field).exclude(
                    value__isnull=True).exclude(value__exact='').values_list('custom_request__id', flat=True))

            statuses = statuses.filter(custom_request__id__in=field_ids)


        # CUSTOM FIELD VALUE
        custom_field_value = filters["customFieldValue"]
        if (len(custom_field_value) > 0):
            field_ids = list(
                CustomRequestFields.objects.filter(custom_request__dynamic_request_form__render_form=True,
                                                    value__icontains=custom_field_value).values_list(
                                                    'custom_request__id', flat=True))
            statuses = statuses.filter(custom_request__id__in=field_ids)

        # FORM NAME
        dynamic_request_form_id = filters["customFormTypeId"]
        if (len(dynamic_request_form_id) > 0):
            statuses = statuses.filter(custom_request__dynamic_request_form__id=dynamic_request_form_id)


        # REQUEST TYPE
        request_type = filters["requestType"]
        if len(request_type) > 0:
            statuses = statuses.filter(content_type__model=request_type)
        
        return statuses

    def get_populated_request_dict(self,statuses):
        populated_statuses = []
        custom_dynamic_columns = []
        for status in statuses:
            populated = {}
            main_request = None
            if status["content_type__model"] == "request":
                request = Request.objects.get(pk=status["object_id"])
                main_request= request
                populated["Display ID"] = request.display_id
                populated["Name"] = request.first_name + request.last_name
                populated["Request Type"] = request.request_type.__unicode__()


            elif status["content_type__model"] == "corporaterequest":
                corporate_request = CorporateRequest.objects.get(pk=status["object_id"])
                main_request = corporate_request
                populated["Display ID"] = corporate_request.display_id
                populated["Name"] = corporate_request.company_name
                populated["Request Type"] = corporate_request.request_type.__unicode__()
                
            elif status["content_type__model"] == "customrequest":
                custom_request = CustomRequest.objects.get(pk=status["object_id"])
                main_request = custom_request
                populated["Display ID"] = custom_request.display_id
                populated["Name"] = custom_request.name
                populated["Request Type"] = custom_request.request_type.__unicode__()
                custom_fields =  CustomRequestFields.objects.filter(custom_request=custom_request)
                for custom_field in custom_fields:
                    label = "Custom-" + custom_field.form_field.label
                    value = custom_field.value
                    
                    if label not in custom_dynamic_columns:
                        custom_dynamic_columns.append(label)
                    populated[label] = value

                
        
            if status['status'] == 1 or status['status'] == 2:
                populated['Status'] = 'New'
            elif status['status'] == 3:
                populated['Status'] = 'In Progress'
                populated['Start Date'] = formats.date_format(main_request.get_in_progress_request_status().datetime.astimezone(timezone('US/Eastern')), "SHORT_DATETIME_FORMAT")
            elif status['status'] == 4:
                populated['Status'] = 'Completed'
                populated['Start Date'] = formats.date_format(main_request.get_in_progress_request_status().datetime.astimezone(timezone('US/Eastern')), "SHORT_DATETIME_FORMAT")
            elif status['status'] == 5:
                populated['Status'] = 'Submitted'
                populated['Start Date'] = formats.date_format(main_request.get_in_progress_request_status().datetime.astimezone(timezone('US/Eastern')), "SHORT_DATETIME_FORMAT")
            elif status['status'] == 6:
                try:
                    populated['Status'] = 'In Progress'
                    populated['Start Date'] = formats.date_format(main_request.get_in_progress_request_status().datetime.astimezone(timezone('US/Eastern')), "SHORT_DATETIME_FORMAT")
                except:
                    populated['Status'] = 'New'

            else:
                populated['Status'] = Status.SUPERVISOR_STATUS_CHOICES.get(status['status'])

            
            populated_statuses.append(populated)

        return populated_statuses, custom_dynamic_columns


    def post(self,request):
        data = json.loads(request.body)
        supervisor = get_company_employee(request.user)
        company = supervisor.company.name
        ids = list(Status.get_all_current_ids_queryset_for_company(company))
        statuses = Status.objects.filter(id__in=ids).values("content_type__model","object_id","status")
        statuses = self.apply_filters_on_export_requests(data,statuses)
        statuses, custom_dynamic_columns = self.get_populated_request_dict(statuses)

        fieldnames = ["Display ID","Name","Status","Start Date","Request Type"] + custom_dynamic_columns
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="request_advanced_search.csv"'

        writer = csv.DictWriter(response, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(statuses)
        return response



####################################
#
# ANALYST VIEWS
#
####################################
@login_required
def analyst_request_detail_view(request, pk):
    current_user = request.user
    if (not is_analyst(current_user) or not request_is_valid(pk)):
        return redirect_to_dashboard(current_user)

    group = get_user_group(current_user)
    is_assigned = analyst_has_access_to_request(current_user,pk)
    try:
        request_object = Request.objects.get(pk=pk)
    except Request.DoesNotExist:
        return render(request, '404.html')

    request_status = request_object.get_request_status()
    request_submitted_date = Status.objects.filter(request=request_object).filter(
        status=Status.NEW_STATUS).first().datetime
    real_status = Status.get_request_status_for_group(group, request_status)

    request_statuses_with_comments = Status.objects.filter(request=request_object).exclude(
        comments__exact='').order_by("-datetime")

    if request_status == 2 or request_status == 4 or request_status == 5 or request_status == 6 or request_status == 7 or request_status == 8:
        form = generate_form_for_detail_view(request, group, request_status, request_object, False)
    else:
        form = generate_form_for_detail_view(request, group, request_status, request_object, True)


    analyst_notes_form = generate_analyst_notes_form(request,request_object)

    analyst_internal_doc_form = generate_analyst_internal_doc_form(request,request_object)

    analyst_request_detail_status_form = generate_analyst_request_detail_status_form(request,request_object)
    error_generated = False
    if request.POST:
        formset = save_surcharges(request.POST, request_object)
        analyst_request_status_response = handle_analyst_request_detail_status_form(request_object,request.POST,analyst_request_detail_status_form)
        if analyst_request_status_response is None:
            error_generated = True
    else:
        formset = generate_surcharge_formset_for_detail_view(request, request_object)

    response = None
    if not error_generated:
        response = handle_detail_view_post(request, form, formset, request_object, 'analyst_dashboard')

    if request.POST and not error_generated:
        internal_doc_response = save_analyst_internal_doc(request,request_object,analyst_internal_doc_form)
        if not internal_doc_response:
            error_generated = True
        else:
            save_analyst_notes(request_object,request.POST)

    if response is not None and not error_generated:
        return response

    client_attachments =  request_object.attachments.all()

    company_logo = None
    try:
        company_logo = CompanyEmployee.objects.get(user=current_user).company.logo
    except:
        pass

    print request_object.analyst_internal_doc

    return render(request, 'core/request_detail_analyst.html', {
        'request': request_object, 'status': request_status, 'real_status': real_status, 'form': form,
        'submitted_date': request_submitted_date,
        'group_name': group.name, 'comments': request_statuses_with_comments, 'company_logo': company_logo,
        'is_corporate': False, 'client_attachments': client_attachments, 'formset': formset,
        'is_assigned':is_assigned,"analyst_notes_form":analyst_notes_form,
        "analyst_request_detail_status_form":analyst_request_detail_status_form,
        'analyst_internal_doc_form': analyst_internal_doc_form
    })

@login_required
def analyst_request_for_corporate_detail_view(request, pk):
    current_user = request.user
    if (not is_analyst(current_user) or not corporate_request_is_valid(
            pk)):
        return redirect_to_dashboard(current_user)

    group = get_user_group(current_user)
    is_assigned = analyst_has_access_to_request_for_corporate(current_user, pk)
    try:
        request_object = CorporateRequest.objects.get(pk=pk)
    except CorporateRequest.DoesNotExist:
        return render(request, '404.html')

    request_status = request_object.get_request_status()
    request_submitted_date = Status.objects.filter(corporate_request=request_object).filter(
        status=Status.NEW_STATUS).first().datetime
    real_status = Status.get_request_status_for_group(group, request_status)

    request_statuses_with_comments = Status.objects.filter(corporate_request=request_object).exclude(
        comments__exact='').order_by("-datetime");

    if request_status == 2 or request_status == 4 or request_status == 5 or request_status == 6 or request_status == 7 or request_status == 8:
        form = generate_form_for_detail_view(request, group, request_status, request_object, False)
    else:
        form = generate_form_for_detail_view(request, group, request_status, request_object, True)

    analyst_notes_form = generate_analyst_notes_form(request,request_object)

    analyst_internal_doc_form = generate_analyst_internal_doc_form(request,request_object)

    analyst_request_detail_status_form = generate_analyst_request_detail_status_form(request,request_object)
    error_generated = False
    if request.POST:
        formset = save_surcharges(request.POST, request_object)
        analyst_request_status_response = handle_analyst_request_detail_status_form(request_object,request.POST,analyst_request_detail_status_form)
        if analyst_request_status_response is None:
            error_generated = True
    else:
        formset = generate_surcharge_formset_for_detail_view(request, request_object)

    response = None
    if not error_generated:
        response = handle_detail_view_post(request, form, formset, request_object, 'analyst_dashboard')

    if request.POST and not error_generated:
        internal_doc_response = save_analyst_internal_doc(request,request_object,analyst_internal_doc_form)
        if not internal_doc_response:
            error_generated = True
        else:
            save_analyst_notes(request_object,request.POST)

    if response is not None and not error_generated:
        return response

    company_logo = None
    try:
        company_logo = CompanyEmployee.objects.get(user=current_user).company.logo
    except:
        pass

    client_attachments = request_object.attachments.all()

    return render(request, 'core/request_detail_analyst.html', {
        'request': request_object, 'status': request_status, 'real_status': real_status, 'form': form,
        'submitted_date': request_submitted_date,
        'group_name': group.name, 'comments': request_statuses_with_comments, 'company_logo': company_logo,
        'is_corporate': True, 'client_attachments':client_attachments, 'formset': formset,
        'is_assigned':is_assigned,"analyst_notes_form":analyst_notes_form,
        "analyst_request_detail_status_form":analyst_request_detail_status_form,
        'analyst_internal_doc_form': analyst_internal_doc_form

    })

@login_required
def analyst_request_for_custom_detail_view(request, pk):
    current_user = request.user
    if (not is_analyst(current_user) or not custom_request_is_valid(
            pk)):
        return redirect_to_dashboard(current_user)

    group = get_user_group(current_user)
    is_assigned = analyst_has_access_to_request_for_custom(current_user, pk)
    try:
        custom_request = CustomRequest.objects.get(pk=pk)
    except CustomRequest.DoesNotExist:
        print "could not get custom request for id = %d" % pk
        return render(request, '404.html')

    try:
        fields = CustomRequestFields.objects.filter(custom_request=custom_request)
    except CustomRequestFields.DoesNotExist:
        print "could not find all custom request fields"
        return render(request, '404.html')

    request_status = custom_request.get_request_status()
    request_submitted_date = Status.objects.filter(custom_request=custom_request).filter(
        status=Status.NEW_STATUS).first().datetime
    real_status = Status.get_request_status_for_group(group, request_status)

    request_statuses_with_comments = Status.objects.filter(custom_request=custom_request).exclude(
        comments__exact='').order_by("-datetime")

    if request_status == 2 or request_status == 4 or request_status == 5 or request_status == 6 or request_status == 7 or request_status == 8:
        form = generate_form_for_detail_view(request, group, request_status, custom_request, False)
    else:
        form = generate_form_for_detail_view(request, group, request_status, custom_request, True)

    analyst_notes_form = generate_analyst_notes_form(request,custom_request)

    analyst_internal_doc_form = generate_analyst_internal_doc_form(request,custom_request)

    analyst_request_detail_status_form = generate_analyst_request_detail_status_form(request,custom_request)
    error_generated = False
    if request.POST:
        formset = save_surcharges(request.POST, custom_request)
        analyst_request_status_response = handle_analyst_request_detail_status_form(custom_request,request.POST,analyst_request_detail_status_form)
        if analyst_request_status_response is None:
            error_generated = True
    else:
        formset = generate_surcharge_formset_for_detail_view(request, custom_request)

    response = None
    if not error_generated:
        response = handle_detail_view_post(request, form, formset, custom_request, 'analyst_dashboard')

    if request.POST and not error_generated:
        internal_doc_response = save_analyst_internal_doc(request,custom_request,analyst_internal_doc_form)
        if not internal_doc_response:
            error_generated = True
        else:
            save_analyst_notes(custom_request,request.POST)

    if response is not None and not error_generated:
        return response

    client_attachments = custom_request.attachments.all()

    company_logo = None
    company = None
    try:
        company = CompanyEmployee.objects.get(user=current_user).company
    except:
        pass

    try:
        company_logo = company.logo
    except:
        pass


    return render(request, 'core/request_detail_analyst.html', {
        'request': custom_request, 'status': request_status, 'real_status': real_status, 'form': form,
        'submitted_date': request_submitted_date, 'group_name': group.name, 'comments': request_statuses_with_comments,
        'company_logo': company_logo, 'is_custom': True, "fields": fields, 'client_attachments': client_attachments,
        'formset': formset, 'is_assigned':is_assigned,"analyst_notes_form":analyst_notes_form,
        "analyst_request_detail_status_form":analyst_request_detail_status_form,
        'analyst_internal_doc_form': analyst_internal_doc_form
    })

@login_required
def analyst_dashboard(request):
    current_user = request.user
    new_new_returned = Status.get_all_requests_by_statuses_for_analyst(
        [Status.ASSIGNED_STATUS, Status.NEW_RETURNED_STATUS], current_user)

    in_progress_statuses = Status.get_all_requests_by_statuses_for_analyst(
        [Status.IN_PROGRESS_STATUS], current_user)

    ids = list(Status.get_all_current_ids_queryset())
    all_count = len(ids)
    # GET COMPLETED COUNT
    completed_count = Status.objects.filter(id__in=ids, status=Status.COMPLETED_STATUS).count()

    # GET NEW COUNT
    new_count = Status.get_num_new_requests_x_days_for_manager(1)

    # GET IN_PROGRESS COUNT
    in_progress_count = Status.get_num_in_progess_statuses()

    # GET UNASSIGNED COUNT
    unassigned_count = Status.objects.filter(id__in=ids, status__in=[Status.NEW_STATUS]).count()

    if (is_analyst(current_user)):
        return render(request, "core/analyst_dashboard.html", {
            'new_new_returned':new_new_returned,
            'in_progress_statuses':in_progress_statuses,
            'completed_count': completed_count,
            'new_count': new_count,
            'unassigned_count': unassigned_count,
            'in_progress_count': in_progress_count,
            'all_count': all_count
        })
    else:
        return redirect_to_dashboard(current_user)

@login_required
def analyst_advanced_search(request):
    current_user = request.user
    types = CompanyDueDiligenceTypeSelection.objects.all()
    companies = Company.objects.order_by("name")
    statuses = Status.REQUEST_STATUS_CHOICES
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
    reordered_statuses = []
    for reordered in reordered_statuses_preference:
        for status in statuses:
            if reordered == status[0]:
                reordered_statuses.append(status)
    
    ids = list(Status.get_all_current_ids_queryset())
    all_count = len(ids)
    # GET COMPLETED COUNT
    completed_count = Status.objects.filter(id__in=ids, status=Status.COMPLETED_STATUS).count()

    # GET NEW COUNT
    new_count = Status.get_num_new_requests_x_days_for_manager(1)

    # GET IN_PROGRESS COUNT
    in_progress_count = Status.get_num_in_progess_statuses()

    # GET UNASSIGNED COUNT
    unassigned_count = Status.objects.filter(id__in=ids, status__in=[Status.NEW_STATUS]).count()

    analysts = SpotLitStaff.get_analysts(True)

    if (is_analyst(current_user)):
        return render(request, "core/analyst_advanced_search.html", {
            "companies": companies,
            "request_types": types,
            "analysts":analysts,
            "statuses": reordered_statuses,
            'completed_count': completed_count,
            'new_count': new_count,
            'unassigned_count': unassigned_count,
            'in_progress_count': in_progress_count,
            'all_count': all_count

        })
    else:
        return redirect_to_dashboard(current_user)

@login_required
def analyst_new_requests(request):
    current_user = request.user
    if(is_analyst(current_user)):
        ids = list(Status.get_all_current_ids_queryset())

        all_count = len(ids)

        # completed status count
        completed_count = Status.objects.filter(id__in=ids, status__in=[Status.COMPLETED_STATUS]).count()

        # new status count
        new_count = Status.get_num_new_requests_x_days_for_manager(1)

        #un-assigned count
        unassigned_count = Status.objects.filter(id__in=ids, status__in=[Status.NEW_STATUS]).count()

        # GET IN_PROGRESS COUNT
        in_progress_count = Status.get_num_in_progess_statuses()

        return render(request, "core/analyst_new_requests.html", {
            "all_count": all_count,
            "completed_count": completed_count,
            "new_count": new_count,
            "unassigned_count": unassigned_count,
            "in_progress_count": in_progress_count
        })
    else:
        return redirect_to_dashboard(current_user)


@login_required
def analyst_completed_requests(request):
    current_user = request.user
    if (is_analyst(current_user)):

        company_logo = None
        try:
            company_logo = CompanyEmployee.objects.get(user=current_user).company.logo
        except:
            pass
        analysts = SpotLitStaff.get_analysts()
        statuses = Status.REQUEST_STATUS_CHOICES

        ids = list(Status.get_all_current_ids_queryset())

        all_count = len(ids)

        completed_count = Status.objects.filter(id__in=ids, status=Status.COMPLETED_STATUS).count()

        new_count = Status.get_num_new_requests_x_days_for_manager(1)

        # unassigned count
        unassigned_count = Status.objects.filter(id__in=ids, status__in=[Status.NEW_STATUS]).count()

        # GET IN_PROGRESS COUNT
        in_progress_count = Status.get_num_in_progess_statuses()

        statuses = Status.objects.filter(id__in=ids, status__in=[Status.COMPLETED_STATUS])

        # total_notifications = num_completed + num_rejected
        return render(request, "core/analyst_completed_requests.html", {
            'all_count': all_count,
            'completed_count': completed_count,
            'in_progress_count': in_progress_count,
            'new_count': new_count,
            'unassigned_count': unassigned_count,
            'statuses':statuses


        })

    return redirect_to_dashboard(current_user)

@login_required
def analyst_in_progress_requests(request):
    current_user = request.user
    if(is_analyst(current_user)):
        ids = list(Status.get_all_current_ids_queryset())

        all_count = len(ids)

        # completed status count
        completed_count = Status.objects.filter(id__in=ids, status__in=[Status.COMPLETED_STATUS]).count()

        # new status count
        new_count = Status.get_num_new_requests_x_days_for_manager(1)

        # unassigned request count
        unassigned_count = Status.objects.filter(id__in=ids, status__in=[Status.NEW_STATUS]).count()

        # rejected status count
        rejected_count = Status.objects.filter(id__in=ids, status__in=[Status.IN_PROGRESS_STATUS,
                                                                       Status.ASSIGNED_STATUS]).count()

        statuses = Status.objects.filter(id__in=ids, status__in=[Status.IN_PROGRESS_STATUS, Status.ASSIGNED_STATUS,
                                                                 Status.NEW_RETURNED_STATUS, Status.REVIEW_STATUS])

        # GET IN_PROGRESS COUNT
        in_progress_count  = Status.get_num_in_progess_statuses()

        return render(request, "core/analyst_in_progress_requests.html", {
            "all_count": all_count,
            "completed_count": completed_count,
            "in_progress_count": in_progress_count,
            "new_count": new_count,
            "unassigned_count": unassigned_count,
            "rejected_count": rejected_count,
            "statuses":statuses
        })


    else:
        return redirect_to_dashboard(current_user)


class AnalystRequestExport(AnalystOnlyMixin,generic.View):

    def apply_filters_on_export_requests(self,filters,statuses):
        # ID
        id_search = filters["requestId"]
        if (len(id_search) > 0):
            cust_id_filt = statuses.filter(custom_request__display_id__icontains=id_search)
            corp_id_filt = statuses.filter(corporate_request__display_id__icontains=id_search)
            ind_id_filt = statuses.filter(request__display_id__icontains=id_search)
            statuses = cust_id_filt | corp_id_filt | ind_id_filt
        
        # company
        company_search = filters["companyId"]
        if (len(company_search) > 0):
            cust_company_name = statuses.filter(custom_request__created_by__company=company_search)
            corp_company_name = statuses.filter(corporate_request__created_by__company=company_search)
            ind_company_name = statuses.filter(request__created_by__company=company_search)
            statuses = cust_company_name | corp_company_name | ind_company_name


        name_search = filters["name"]
        if len(name_search) > 0:
            cust_names = statuses.filter(custom_request__name__icontains=name_search)
            corp_names = statuses.filter(corporate_request__company_name__icontains=name_search)
            ind_first = statuses.filter(request__first_name__icontains=name_search)
            ind_last = statuses.filter(request__last_name__icontains=name_search)
            statuses = cust_names | corp_names | ind_first | ind_last



        # STATUS
        status_search = filters["statusType"]
        if (status_search != "null" and len(status_search) > 0):
            statuses = statuses.filter(status__in=status_search)

        # TYPE
        type_search = filters["type"]
        if (len(type_search) > 0):
            dd_type_selection = CompanyDueDiligenceTypeSelection.objects.get(id=type_search)
            if (dd_type_selection.name == ""):
                level = dd_type_selection.level
                dd_type = dd_type_selection.due_diligence_type
                cust_dd_ids = statuses.filter(custom_request__request_type__level=level).filter(
                    custom_request__request_type__due_diligence_type=dd_type).values_list('id', flat=True)

                corp_dd_ids = statuses.filter(corporate_request__request_type__level=level).filter(
                    corporate_request__request_type__due_diligence_type=dd_type).values_list('id', flat=True)

                ind_dd_ids = statuses.filter(request__request_type__level=level).filter(
                    request__request_type__due_diligence_type=dd_type).values_list('id', flat=True)

                comb_dd_ids = list(chain(cust_dd_ids, corp_dd_ids, ind_dd_ids))

                statuses = statuses.filter(id__in=comb_dd_ids)

            else:
                cust_dd_ids = statuses.filter(
                    custom_request__request_type__id=type_search).values_list('id', flat=True)

                corp_dd_ids = statuses.filter(
                    corporate_request__request_type__id=type_search).values_list('id', flat=True)

                ind_dd_ids = statuses.filter(
                    request__request_type__id=type_search).values_list('id', flat=True)

                comp_dd_ids = list(chain(cust_dd_ids, corp_dd_ids, ind_dd_ids))

                statuses = statuses.filter(id__in=comp_dd_ids)

        # Assigned To
        assigned_to_id = filters["assignmentId"]
        if (len(assigned_to_id) > 0):
            cust_ids = statuses.filter(custom_request__assignment=assigned_to_id).values_list('id', flat=True)
            corp_ids = statuses.filter(corporate_request__assignment=assigned_to_id).values_list('id', flat=True)
            ind_ids = statuses.filter(request__assignment=assigned_to_id).values_list('id', flat=True)
            comb_ids = list(chain(cust_ids, corp_ids, ind_ids))
            statuses = statuses.filter(id__in=comb_ids)
        
        return statuses

    def get_populated_request_dict(self,statuses):
        populated_statuses = []
        request_detail_choices_dict = dict(BaseRequestDetailStatus.REQUEST_DETAIL_STATUS_CHOICES)
        for status in statuses:
            populated = {}
            main_request = None
            if status["content_type__model"] == "request":
                request = Request.objects.get(pk=status["object_id"])
                main_request= request
                populated["Display ID"] = request.display_id
                populated["Name"] = request.first_name + request.last_name
                populated["Company Name"] = request.created_by.company.name
                populated["Assignment"] = request.assignment.user.username if request.reviewer else None
                populated["Reviewer"] = request.reviewer.user.username if request.assignment else None
                

                request_detail_statuses_data = RequestDetailStatus.objects.order_by("status").filter(request=request).values("status","reason")

                request_detail_statuses = [ request_detail_choices_dict[x["status"]] for x in request_detail_statuses_data]
                if len(request_detail_statuses) != 0 and request_detail_statuses[-1] == "Other":
                    request_detail_other_text = [ x["reason"] for x in request_detail_statuses_data if x["status"] == RequestDetailStatus.OTHER]
                    request_detail_other_text = request_detail_other_text[0] if(len(request_detail_other_text) > 0 and request_detail_other_text[0] is not None) else ""
                    request_detail_statuses[-1] +=  "({})".format(request_detail_other_text)
                populated["Analyst Status"] = "\n".join(request_detail_statuses)

            elif status["content_type__model"] == "corporaterequest":
                corporate_request = CorporateRequest.objects.get(pk=status["object_id"])
                main_request = corporate_request
                populated["Display ID"] = corporate_request.display_id
                populated["Name"] = corporate_request.company_name
                populated["Company Name"] = corporate_request.created_by.company.name
                populated["Assignment"] = corporate_request.assignment.user.username if corporate_request.assignment else None
                populated["Reviewer"] = corporate_request.reviewer.user.username if corporate_request.reviewer else None

                request_detail_statuses_data = CorporateRequestDetailStatus.objects.order_by("status").filter(request=corporate_request).values("status","reason")

                request_detail_statuses = [ request_detail_choices_dict[x["status"]] for x in request_detail_statuses_data]
                if len(request_detail_statuses) != 0 and request_detail_statuses[-1] == "Other":
                    request_detail_other_text = [ x["reason"] for x in request_detail_statuses_data if x["status"] == RequestDetailStatus.OTHER]
                    request_detail_other_text = request_detail_other_text[0] if(len(request_detail_other_text) > 0 and request_detail_other_text[0] is not None) else ""
                    request_detail_statuses[-1] +=  "({})".format(request_detail_other_text)
                populated["Analyst Status"] = "\n".join(request_detail_statuses)

            elif status["content_type__model"] == "customrequest":
                custom_request = CustomRequest.objects.get(pk=status["object_id"])
                main_request = custom_request
                populated["Display ID"] = custom_request.display_id
                populated["Name"] = custom_request.name
                populated["Company Name"] = custom_request.created_by.company.name
                populated["Assignment"] = custom_request.assignment.user.username if custom_request.assignment else None
                populated["Reviewer"] = custom_request.reviewer.user.username if custom_request.reviewer else None


                request_detail_statuses_data = CustomRequestDetailStatus.objects.order_by("status").filter(request=custom_request).values("status","reason")

                request_detail_statuses = [ request_detail_choices_dict[x["status"]] for x in request_detail_statuses_data]
                if len(request_detail_statuses) != 0 and request_detail_statuses[-1] == "Other":
                    request_detail_other_text = [ x["reason"] for x in request_detail_statuses_data if x["status"] == RequestDetailStatus.OTHER]
                    request_detail_other_text = request_detail_other_text[0] if(len(request_detail_other_text) > 0 and request_detail_other_text[0] is not None) else ""
                    request_detail_statuses[-1] +=  "({})".format(request_detail_other_text)
                populated["Analyst Status"] = "\n".join(request_detail_statuses)
        
            if status['status'] == 1 or status['status'] == 2:
                populated['Status'] = 'New'
            elif status['status'] == 3:
                populated['Status'] = 'In Progress'
                populated['Date'] = formats.date_format(main_request.get_in_progress_request_status().datetime.astimezone(timezone('US/Eastern')), "SHORT_DATETIME_FORMAT")
            elif status['status'] == 4:
                populated['Status'] = 'Completed'
                populated['Date'] = formats.date_format(main_request.get_in_progress_request_status().datetime.astimezone(timezone('US/Eastern')), "SHORT_DATETIME_FORMAT")
            elif status['status'] == 5:
                populated['Status'] = 'Submitted'
                populated['Date'] = formats.date_format(main_request.get_in_progress_request_status().datetime.astimezone(timezone('US/Eastern')), "SHORT_DATETIME_FORMAT")
            elif status['status'] == 6:
                try:
                    populated['Status'] = 'In Progress'
                    populated['Date'] = formats.date_format(main_request.get_in_progress_request_status().datetime.astimezone(timezone('US/Eastern')), "SHORT_DATETIME_FORMAT")
                except:
                    populated['Status'] = 'New'

            else:
                populated['Status'] = Status.SUPERVISOR_STATUS_CHOICES.get(status['status'])

            
            populated_statuses.append(populated)

        return populated_statuses


    def post(self,request):
        current_user = request.user
        data = json.loads(request.body)
        ids = list(Status.get_all_current_ids_queryset())
        statuses = Status.objects.filter(id__in=ids).values("content_type__model","object_id","status")
        # for i in statuses:
        statuses = self.apply_filters_on_export_requests(data,statuses)
        statuses = self.get_populated_request_dict(statuses)

        fieldnames = ["Display ID","Name","Status","Analyst Status","Date","Company Name","Assignment","Reviewer"]
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="request_advanced_search.csv"'

        writer = csv.DictWriter(response, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(statuses)
        return response

####################################
#
# MANAGER VIEWS
#
####################################
@login_required
def manager_request_detail_view(request, pk):
    current_user = request.user
    if (not is_manager(current_user) or not request_is_valid(pk)):
        return redirect_to_dashboard(current_user)

    group = get_user_group(current_user)

    try:
        request_object = Request.objects.get(pk=pk)
    except Request.DoesNotExist:
        return render(request, '404.html')

    try:
        service_statuses = RequestServiceStatus.objects.filter(request=request_object)
    except Exception, e:
        service_statuses = []

    request_status = request_object.get_request_status()
    request_submitted_date = Status.objects.filter(request=request_object).filter(
        status=Status.NEW_STATUS).first().datetime
    real_status = Status.get_request_status_for_group(group, request_status)
    form = generate_form_for_detail_view(request, group, request_status, request_object, False)

    request_statuses_with_comments = Status.objects.filter(request=request_object).exclude(
        comments__exact='').order_by("-datetime")
    
    
    statuses = Status.REQUEST_STATUS_CHOICES

    analysts = []

    analysts = SpotLitStaff.get_analysts(True)

    reviewers = SpotLitStaff.get_reviewers(True)

    if request.POST:
        formset = save_surcharges(request.POST, request_object)
    else:
        formset = generate_surcharge_formset_for_detail_view(request, request_object)

    response = handle_detail_view_post(request, form, formset, request_object, 'manager_dashboard')

    if (response is not None):
        return response

    company_logo = None
    try:
        company_logo = CompanyEmployee.objects.get(user=current_user).company.logo
    except:
        pass

    supervisors = CompanyEmployee.objects.filter(company=request_object.created_by.company)

    client_attachments = request_object.attachments.all()

    return render(request, 'core/request_detail_manager.html', {
        'request': request_object,
        'status': request_status,
        'real_status': real_status,
        'analysts': analysts,
        'form': form,
        'submitted_date': request_submitted_date,
        'group_name': group.name,
        'comments': request_statuses_with_comments,
        'company_logo': company_logo,
        'is_corporate': False,
        'is_custom': False,
        'is_individual': True,
        'reviewers': reviewers,
        'statuses': statuses,
        'client_attachments': client_attachments,
        'formset': formset,
        'supervisors':supervisors
    })

@login_required
def manager_request_for_corporate_detail_view(request, pk):
    current_user = request.user
    if (not is_manager(current_user) or not corporate_request_is_valid(pk)):
        return redirect_to_dashboard(current_user)

    group = get_user_group(current_user)

    try:
        request_object = CorporateRequest.objects.get(pk=pk)
    except CorporateRequest.DoesNotExist:
        return render(request, '404.html')

    try:
        service_statuses = CorporateRequestServiceStatus.objects.filter(request=request_object)
    except Exception, e:
        service_statuses = []

    request_status = request_object.get_request_status()
    request_submitted_date = Status.objects.filter(corporate_request=request_object).filter(
        status=Status.NEW_STATUS).first().datetime
    real_status = Status.get_request_status_for_group(group, request_status)
    form = generate_form_for_detail_view(request, group, request_status, request_object, False)

    request_statuses_with_comments = Status.objects.filter(corporate_request=request_object).exclude(
        comments__exact='').order_by("-datetime")


    statuses = Status.REQUEST_STATUS_CHOICES

    analysts = []

    analysts = SpotLitStaff.get_analysts(True)

    reviewers = SpotLitStaff.get_reviewers(True)

    if request.POST:
        formset = save_surcharges(request.POST, request_object)
    else:
        formset = generate_surcharge_formset_for_detail_view(request, request_object)

    response = handle_detail_view_post(request, form, formset, request_object, 'manager_dashboard')

    if (response is not None):
        return response

    company_logo = None
    try:
        company_logo = CompanyEmployee.objects.get(user=current_user).company.logo
    except:
        pass

    supervisors = CompanyEmployee.objects.filter(company=request_object.created_by.company)

    client_attachments = request_object.attachments.all()


    return render(request, 'core/request_detail_manager.html', {
        'request': request_object, 'status': request_status, 'real_status': real_status,
        'analysts': analysts, 'form': form, 'submitted_date': request_submitted_date, 'group_name': group.name,
        'comments': request_statuses_with_comments,
        'company_logo': company_logo, 'is_corporate': True,'is_custom':False,
        'statuses': statuses, 'reviewers': reviewers, 'client_attachments': client_attachments, 'formset': formset,
        'supervisors':supervisors
    })

@login_required
def manager_request_for_custom_detail_view(request, pk):
    current_user = request.user
    if (not is_manager(current_user) or not custom_request_is_valid(pk)):
        return redirect_to_dashboard(current_user)

    group = get_user_group(current_user)

    try:
        custom_request = CustomRequest.objects.get(pk=pk)
    except CustomRequest.DoesNotExist:
        return render(request, '404.html')

    try:
        fields = CustomRequestFields.objects.filter(custom_request=custom_request)
    except CustomRequestFields.DoesNotExist:
        return render(request, '404.html')

    try:
        service_statuses = CustomRequestServiceStatus.objects.filter(request=custom_request)
    except Exception, e:
        service_statuses = []

    request_status = custom_request.get_request_status()
    request_submitted_date = Status.objects.filter(custom_request=custom_request).filter(
        status=Status.NEW_STATUS).first().datetime
    real_status = Status.get_request_status_for_group(group, request_status)
    request_statuses_with_comments = Status.objects.filter(custom_request=custom_request).exclude(
        comments__exact='').order_by("-datetime")


    form = generate_form_for_detail_view(request, group, request_status, custom_request, False)
    statuses = Status.REQUEST_STATUS_CHOICES


    analysts = []
    analysts = SpotLitStaff.get_analysts(True)

    reviewers = SpotLitStaff.get_reviewers(True)

    if request.POST:
        formset = save_surcharges(request.POST, custom_request)
    else:
        formset = generate_surcharge_formset_for_detail_view(request, custom_request)

    response = handle_detail_view_post(request, form, formset, custom_request, 'manager_dashboard')

    if (response is not None):
        return response

    client_attachments = custom_request.attachments.all()

    company_logo = None
    company = None
    try:
        company = CompanyEmployee.objects.get(user=current_user).company
    except:
        pass

    try:
        company_logo = company.logo
    except:
        pass

    custom_requests = None
    try:
        custom_requests = DynamicRequestForm.objects.filter(company=company)
    except:
        pass

    supervisors = CompanyEmployee.objects.filter(company=custom_request.created_by.company)

    etrade_reporting_period_form = EtradeReportingPeriodForm

    return render(request, 'core/request_detail_manager.html', {
        'etrade_reporting_period_form': etrade_reporting_period_form,
        'request': custom_request, 'status': request_status, 'real_status': real_status,
        'analysts': analysts, 'form': form, 'submitted_date': request_submitted_date, 'group_name': group.name,
        'comments': request_statuses_with_comments,  'is_custom': True, 'fields':fields,
        'custom_requests':custom_requests, 'company_logo': company_logo, 'statuses': statuses, 'reviewers':reviewers,
        'client_attachments': client_attachments, 'formset': formset, 'supervisors':supervisors
    })

@login_required
def manager_dashboard(request):
    current_user = request.user
    if (is_manager(current_user)):
        ids = list(Status.get_all_current_ids_queryset())
        all_count = len(ids)
        # GET COMPLETED COUNT
        completed_count = Status.objects.filter(id__in=ids, status=Status.COMPLETED_STATUS).count()

        # GET NEW COUNT
        new_count = Status.get_num_new_requests_x_days_for_manager(1)

        # GET IN_PROGRESS COUNT
        in_progress_count = Status.get_num_in_progess_statuses()

        # GET UNASSIGNED COUNT
        unassigned_count = Status.objects.filter(id__in=ids, status__in=[Status.NEW_STATUS]).count()

        # TODO GET all etrade requests in the last 60 hours

        etrade_status_ids = Status.get_all_current_ids_queryset_for_company('E*TRADE')

        fifty_hours_ago = datetime.datetime.now() - datetime.timedelta(minutes=3000)
        sixty_hours_ago = datetime.datetime.now() - datetime.timedelta(minutes=3600)

        etrade_statuses = Status.objects.filter(
            id__in=etrade_status_ids, status__in=[Status.IN_PROGRESS_STATUS, Status.COMPLETED_STATUS],
            custom_request__in_progress_status__datetime__lte=fifty_hours_ago).order_by('custom_request__in_progress_status__datetime')


        return render(request, "core/manager_dash.html", {
            'etrade_statuses':etrade_statuses,
            'completed_count': completed_count,
            'new_count': new_count,
            'unassigned_count': unassigned_count,
            'in_progress_count': in_progress_count,
            'all_count': all_count
        })
    else:
        return redirect_to_dashboard(current_user)

@login_required
def manager_new_requests(request):
    current_user = request.user
    if(is_manager(current_user)):
        ids = list(Status.get_all_current_ids_queryset())

        all_count = len(ids)

        # completed status count
        completed_count = Status.objects.filter(id__in=ids, status__in=[Status.COMPLETED_STATUS]).count()

        # new status count
        new_count = Status.get_num_new_requests_x_days_for_manager(1)

        #un-assigned count
        unassigned_count = Status.objects.filter(id__in=ids, status__in=[Status.NEW_STATUS]).count()

        # GET IN_PROGRESS COUNT
        in_progress_count = Status.get_num_in_progess_statuses()

        return render(request, "core/manager_new_requests.html", {
            "all_count": all_count,
            "completed_count": completed_count,
            "new_count": new_count,
            "unassigned_count": unassigned_count,
            "in_progress_count": in_progress_count
        })
    else:
        return redirect_to_dashboard(current_user)

@login_required
def manager_in_progress_requests(request):
    current_user = request.user
    if(is_manager(current_user)):
        ids = list(Status.get_all_current_ids_queryset())

        all_count = len(ids)

        # completed status count
        completed_count = Status.objects.filter(id__in=ids, status__in=[Status.COMPLETED_STATUS]).count()

        # new status count
        new_count = Status.get_num_new_requests_x_days_for_manager(1)

        # unassigned request count
        unassigned_count = Status.objects.filter(id__in=ids, status__in=[Status.NEW_STATUS]).count()

        # rejected status count
        rejected_count = Status.objects.filter(id__in=ids, status__in=[Status.IN_PROGRESS_STATUS,
                                                                       Status.ASSIGNED_STATUS]).count()

        statuses = Status.objects.filter(id__in=ids, status__in=[Status.IN_PROGRESS_STATUS, Status.ASSIGNED_STATUS,
                                                                 Status.NEW_RETURNED_STATUS, Status.REVIEW_STATUS])

        # GET IN_PROGRESS COUNT
        in_progress_count  = Status.get_num_in_progess_statuses()

        return render(request, "core/manager_in_progress_requests.html", {
            "all_count": all_count,
            "completed_count": completed_count,
            "in_progress_count": in_progress_count,
            "new_count": new_count,
            "unassigned_count": unassigned_count,
            "rejected_count": rejected_count,
            "statuses":statuses
        })


    else:
        return redirect_to_dashboard(current_user)

@login_required
def manager_advanced_search(request):
    current_user = request.user
    if(is_manager(current_user)):
        ids = list(Status.get_all_current_ids_queryset())

        all_count = len(ids)

        # completed status count
        completed_count = Status.objects.filter(id__in=ids, status__in=[Status.COMPLETED_STATUS]).count()

        # new status count
        new_count = Status.get_num_new_requests_x_days_for_manager(1)

        # unassigned request count
        unassigned_count = Status.objects.filter(id__in=ids, status__in=[Status.NEW_STATUS]).count()

        # GET IN_PROGRESS COUNT
        in_progress_count = Status.get_num_in_progess_statuses()

        analysts = SpotLitStaff.get_analysts(True)
        types = CompanyDueDiligenceTypeSelection.objects.all()
        fields = DynamicRequestFormFields.objects.filter(dynamic_request_form__render_form=True, archive=False)
        dynamic_forms = DynamicRequestForm.objects.all()
        statuses = Status.REQUEST_STATUS_CHOICES
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
        reordered_statuses = []
        for reordered in reordered_statuses_preference:
            for status in statuses:
                if reordered == status[0]:
                    reordered_statuses.append(status)

        request_types = ['request', 'customrequest', 'corporaterequest']
        companies = Company.objects.order_by("name")
        return render(request, "core/advanced_search_manager.html", {
            "all_count": all_count,
            "analysts": analysts,
            "companies": companies,
            "completed_count": completed_count,
            "dynamic_forms": dynamic_forms,
            "fields": fields,
            "new_count": new_count,
            "unassigned_count": unassigned_count,
            "in_progress_count": in_progress_count,
            "request_types": request_types,
            "statuses": reordered_statuses,
            "types": types,
        })
    else:
        return redirect_to_dashboard(current_user)

@login_required
def manager_completed_requests(request):
    current_user = request.user
    if (is_manager(current_user)):

        company_logo = None
        try:
            company_logo = CompanyEmployee.objects.get(user=current_user).company.logo
        except:
            pass
        analysts = SpotLitStaff.get_analysts()
        statuses = Status.REQUEST_STATUS_CHOICES

        ids = list(Status.get_all_current_ids_queryset())

        all_count = len(ids)

        completed_count = Status.objects.filter(id__in=ids, status=Status.COMPLETED_STATUS).count()

        new_count = Status.get_num_new_requests_x_days_for_manager(1)

        # unassigned count
        unassigned_count = Status.objects.filter(id__in=ids, status__in=[Status.NEW_STATUS]).count()

        # GET IN_PROGRESS COUNT
        in_progress_count = Status.get_num_in_progess_statuses()

        statuses = Status.objects.filter(id__in=ids, status__in=[Status.COMPLETED_STATUS])

        # total_notifications = num_completed + num_rejected
        return render(request, "core/manager_completed_requests.html", {
            'all_count': all_count,
            'completed_count': completed_count,
            'in_progress_count': in_progress_count,
            'new_count': new_count,
            'unassigned_count': unassigned_count,
            'statuses':statuses


        })

    return redirect_to_dashboard(current_user)

## Public Packages Dashboard

@login_required()
def package_dashboard(request):
    current_user = request.user
    if (is_manager(current_user)):
        type_selection = get_public_selections_in_dict()
        return render(request, 'core/package_dashboard.html', {
            'types': type_selection
        })
    return redirect_to_dashboard(current_user)

## Add/Update Public Packages

@login_required()
def add_package(request):
    current_user = request.user
    if (not is_manager(current_user)):
        return redirect_to_dashboard(current_user)

    types = DueDiligenceType.objects.all()
    levels = CompanyDueDiligenceTypeSelection.TYPE_LEVEL_CHOICES

    hr_form = HumanResourcesTypeSelectionForm()
    investigative_form = InvestigativeTypeSelectionForm()
    regulatory_form = RegulatoryTypeSelectionForm()
    business_investment_form = BusinessInvestmentTypeSelectionForm()

    if (request.method == 'POST'):
        valid = False
        dd_type = None
        form = None
        if ('human_resources' in request.POST):
            dd_type = DueDiligenceType.objects.get(name="Pre-Employment")
            hr_form = HumanResourcesTypeSelectionForm(request.POST)
            form = hr_form
            if (hr_form.is_valid()):
                valid = True
        elif ('investigative' in request.POST):
            investigative_form = InvestigativeTypeSelectionForm(request.POST)
            form = investigative_form
            dd_type = DueDiligenceType.objects.get(name="Third Party")
            if (investigative_form.is_valid()):
                valid = True
        elif ('regulatory' in request.POST):
            regulatory_form = RegulatoryTypeSelectionForm(request.POST)
            form = regulatory_form
            dd_type = DueDiligenceType.objects.get(name="Background Investigations")
            if (regulatory_form.is_valid()):
                valid = True
        elif ('business_investment' in request.POST):
            business_investment_form = BusinessInvestmentTypeSelectionForm(request.POST)
            form = business_investment_form
            dd_type = DueDiligenceType.objects.get(name="Know Your Customer")
            if (business_investment_form.is_valid()):
                valid = True

        if (valid):
            name = form.cleaned_data['name']
            if name is None:
                name = ""
            services = form.cleaned_data['services']
            level = form.cleaned_data['levels']
            #comments = form.cleaned_data['comments']
            comments = ""
            price = form.cleaned_data['price']
            invoice_instructions = form.cleaned_data['invoice_instructions']
            is_active = form.cleaned_data['is_active']

            type_selection = CompanyDueDiligenceTypeSelection(is_public=True,due_diligence_type=dd_type, name=name,
                                                              comments=comments, level=level, price=price,
                                                              invoice_instructions=invoice_instructions,
                                                              is_active=is_active)
            type_selection.save()

            for service_name in services:
                service = Service.objects.get(name=service_name)
                service_selection = CompanyServiceSelection(dd_type=type_selection, service=service)
                service_selection.save()

            return HttpResponseRedirect(reverse('package_dashboard'))

        return render(request, 'core/add_package.html',
                      {'types': types,'levels': levels, 'hr_form': hr_form, 'investigative_form': investigative_form,
                       "regulatory_form": regulatory_form, "business_investment_form": business_investment_form,
                       "selection_id": dd_type.id
                       })

    return render(request, 'core/add_package.html',
                  {'types': types,'levels': levels, 'hr_form': hr_form, 'investigative_form': investigative_form,
                   "regulatory_form": regulatory_form, "business_investment_form": business_investment_form,
                   "selection_id": None
                   })

@login_required()
def update_package(request,dd_pk):
    current_user = request.user
    if (not is_manager(current_user) or not public_dd_type_is_valid(dd_pk)):
        return redirect_to_dashboard(current_user)

    dd_type_selection = get_object_or_404(CompanyDueDiligenceTypeSelection, pk=dd_pk)
    types = DueDiligenceType.objects.all()
    levels = CompanyDueDiligenceTypeSelection.TYPE_LEVEL_CHOICES

    hr_form = HumanResourcesTypeSelectionForm()
    investigative_form = InvestigativeTypeSelectionForm()
    regulatory_form = RegulatoryTypeSelectionForm()
    business_investment_form = BusinessInvestmentTypeSelectionForm()

    valid = False
    dd_type = dd_type_selection.due_diligence_type
    form = None
    if (dd_type.name == 'Pre-Employment'):
        hr_form = HumanResourcesTypeSelectionForm(request.POST or None, instance=dd_type_selection)
        form = hr_form
        if (hr_form.is_valid()):
            valid = True
    elif (dd_type.name == 'Third Party'):
        investigative_form = InvestigativeTypeSelectionForm(request.POST or None, instance=dd_type_selection)
        form = investigative_form
        if (investigative_form.is_valid()):
            valid = True
    elif (dd_type.name == 'Background Investigations'):
        regulatory_form = RegulatoryTypeSelectionForm(request.POST or None, instance=dd_type_selection)
        form = regulatory_form
        if (regulatory_form.is_valid()):
            valid = True
    elif (dd_type.name == 'Know Your Customer'):
        business_investment_form = BusinessInvestmentTypeSelectionForm(request.POST or None, instance=dd_type_selection)
        form = business_investment_form
        if (business_investment_form.is_valid()):
            valid = True

    if (valid):
        name = form.cleaned_data['name']
        form_service_names = form.cleaned_data['services']
        level = form.cleaned_data['levels']
        #comments = form.cleaned_data['comments']
        comments = ""
        price = form.cleaned_data['price']
        invoice_instructions = form.cleaned_data['invoice_instructions']
        is_active = form.cleaned_data['is_active']

        dd_type_selection.name = name
        dd_type_selection.level = level
        dd_type_selection.comments = comments
        dd_type_selection.price = price
        dd_type_selection.invoice_intructions = invoice_instructions
        dd_type_selection.is_active = is_active
        dd_type_selection.save()

        saved_service_selections = CompanyServiceSelection.objects.filter(dd_type=dd_type_selection)
        saved_services = [service_selection.service for service_selection in saved_service_selections]
        form_services = Service.objects.filter(name__in=form_service_names)

        to_add = set(form_services) - set(saved_services)
        to_delete = set(saved_services) - set(form_services)
        for service_to_add in to_add:
            service_selection = CompanyServiceSelection(dd_type=dd_type_selection, service=service_to_add)
            service_selection.save()

        for service_to_delete in to_delete:
            saved_service_selections.get(service=service_to_delete).delete()

        return HttpResponseRedirect(reverse('package_dashboard'))

    return render(request, 'core/add_dd_type.html',
                  {'types': types, 'levels': levels, 'hr_form': hr_form, 'investigative_form': investigative_form,
                   "regulatory_form": regulatory_form, "business_investment_form": business_investment_form,
                   "selection_id": dd_type.id
                   })


####################################
#
# REVIEWER VIEWS
#
####################################

@login_required
def advanced_search_reviewer(request):
    current_user = request.user
    types = CompanyDueDiligenceTypeSelection.objects.all()
    companies = Company.objects.order_by("name")
    statuses = Status.REQUEST_STATUS_CHOICES

    if (is_reviewer(current_user)):
        return render(request, "core/advanced_search_reviewer.html", {
            "companies": companies,
            "request_types": types,
            "statuses": statuses

        })
    else:
        return redirect_to_dashboard(current_user)

@login_required
def reviewer_dashboard(request):
    current_user = request.user
    if is_reviewer(current_user):
        review_statuses = Status.get_statuses_for_reviewer_by_status([Status.REVIEW_STATUS], current_user)
        in_progress_statuses = Status.get_statuses_for_reviewer_by_status([Status.IN_PROGRESS_STATUS, Status.ASSIGNED_STATUS, Status.NEW_RETURNED_STATUS], current_user)

        etrade_status_ids = Status.get_all_current_ids_queryset_for_company('E*TRADE')

        fifty_hours_ago = datetime.datetime.now() - datetime.timedelta(minutes=3000)

        etrade_statuses = Status.objects.filter(
            id__in=etrade_status_ids, status__in=[Status.IN_PROGRESS_STATUS, Status.COMPLETED_STATUS],
            custom_request__in_progress_status__datetime__lte=fifty_hours_ago).order_by('custom_request__in_progress_status__datetime')

        return render(request, "core/reviewer_dashboard.html", {
            'review_statuses': review_statuses, 'in_progress_statuses': in_progress_statuses,
            'etrade_statuses' : etrade_statuses
        })
    else:
        return redirect_to_dashboard(current_user)

@login_required
def reviewer_request_detail_view(request, pk):
    current_user = request.user
    if not is_reviewer(current_user) or not request_is_valid(pk):
        return redirect_to_dashboard(current_user)

    group = get_user_group(current_user)

    try:
        request_object = Request.objects.get(pk=pk)
    except Request.DoesNotExist:
        return render(request, '404.html')

    request_status = request_object.get_request_status()
    request_submitted_date = Status.objects.filter(request=request_object).filter(
        status=Status.NEW_STATUS).first().datetime
    real_status = Status.get_request_status_for_group(group, request_status)

    request_statuses_with_comments = Status.objects.filter(request=request_object).exclude(
        comments__exact='').order_by("-datetime")

    if request_object.get_request_status() == Status.REVIEW_STATUS:
        form = generate_form_for_detail_view(request, group, request_status, request_object, True)
    else:
        form = generate_form_for_detail_view(request, group, request_status, request_object, False)

    if request.POST:
        formset = save_surcharges(request.POST, request_object)
    else:
        formset = generate_surcharge_formset_for_detail_view(request, request_object)

    response = handle_detail_view_post(request, form, formset, request_object, 'reviewer_dashboard')

    if (response is not None):
        return response


    client_attachments = request_object.attachments.all()


    company_logo = None
    try:
        company_logo = CompanyEmployee.objects.get(user=current_user).company.logo
    except:
        pass

    analysts = []

    analysts = SpotLitStaff.get_analysts()

    analyst_notes_form = generate_analyst_notes_form(request,request_object)


    return render(request, 'core/request_detail_reviewer.html', {
        'analysts': analysts, 'request': request_object, 'status': request_status, 'real_status': real_status,
        'form': form, 'submitted_date': request_submitted_date, 'group_name': group.name,
        'comments': request_statuses_with_comments, 'company_logo': company_logo,'is_corporate': False,
        'client_attachments': client_attachments, 'formset': formset,
        'analyst_notes_form':analyst_notes_form,'is_reviewer':True
    })

@login_required
def reviewer_custom_request_detail_view(request, pk):
    current_user = request.user

    if not is_reviewer(current_user) or not custom_request_is_valid(pk):
        return redirect_to_dashboard(current_user)

    group = get_user_group(current_user)

    try:
        request_object = CustomRequest.objects.get(pk=pk)
    except Request.DoesNotExist:
        return render(request, '404.html')

    try:
        fields = CustomRequestFields.objects.filter(custom_request=request_object)
    except CustomRequestFields.DoesNotExist:
        return render(request, '404.html')

    request_status = request_object.get_request_status()
    request_submitted_date = Status.objects.filter(custom_request=request_object).filter(
        status=Status.NEW_STATUS).first().datetime
    real_status = Status.get_request_status_for_group(group, request_status)

    request_statuses_with_comments = Status.objects.filter(custom_request=request_object).exclude(
        comments__exact='').order_by("-datetime")

    if request_object.get_request_status() == Status.REVIEW_STATUS:
        form = generate_form_for_detail_view(request, group, request_status, request_object, True)
    else:
        form = generate_form_for_detail_view(request, group, request_status, request_object, False)

    if request.POST:
        formset = save_surcharges(request.POST, request_object)
    else:
        formset = generate_surcharge_formset_for_detail_view(request, request_object)

    response = handle_detail_view_post(request, form, formset, request_object, 'reviewer_dashboard')

    if (response is not None):
        return response

    # fix the attachment name
    if request_object.client_attachment:
        attachment_file_name = os.path.basename(request_object.client_attachment.name)
    else:
        attachment_file_name = ''

    company_logo = None
    try:
        company_logo = CompanyEmployee.objects.get(user=current_user).company.logo
    except:
        pass

    analysts = []

    analysts = SpotLitStaff.get_analysts()

    client_attachments = request_object.attachments.all()

    analyst_notes_form = generate_analyst_notes_form(request,request_object)

    return render(request, 'core/request_detail_reviewer.html', {
        'analysts': analysts,'fields':fields, 'request': request_object, 'status': request_status,
        'real_status': real_status, 'form': form, 'submitted_date': request_submitted_date, 'group_name': group.name,
        'comments': request_statuses_with_comments, 'company_logo': company_logo,
        'is_custom': True, 'client_attachments': client_attachments, 'formset': formset,
        'analyst_notes_form':analyst_notes_form,'is_reviewer':True
    })

@login_required
def reviewer_corporate_request_detail_view(request, pk):
    current_user = request.user
    if not is_reviewer(current_user) or not corporate_request_is_valid(pk):
        return redirect_to_dashboard(current_user)

    group = get_user_group(current_user)

    try:
        request_object = CorporateRequest.objects.get(pk=pk)
    except Request.DoesNotExist:
        return render(request, '404.html')

    request_status = request_object.get_request_status()
    request_submitted_date = Status.objects.filter(corporate_request=request_object).filter(
        status=Status.NEW_STATUS).first().datetime


    real_status = Status.get_request_status_for_group(group, request_status)

    request_statuses_with_comments = Status.objects.filter(corporate_request=request_object).exclude(
        comments__exact='').order_by("-datetime")



    if request_object.get_request_status() == Status.REVIEW_STATUS:
        form = generate_form_for_detail_view(request, group, request_status, request_object, True)
    else:
        form = generate_form_for_detail_view(request, group, request_status, request_object, False)

    if request.POST:
        formset = save_surcharges(request.POST, request_object)
    else:
        formset = generate_surcharge_formset_for_detail_view(request, request_object)

    response = handle_detail_view_post(request, form, formset, request_object, 'reviewer_dashboard')

    if (response is not None):
        return response

    client_attachments = request_object.attachments.all()

    company_logo = None
    try:
        company_logo = CompanyEmployee.objects.get(user=current_user).company.logo
    except:
        pass

    analysts = []

    analysts = SpotLitStaff.get_analysts()

    analyst_notes_form = generate_analyst_notes_form(request,request_object)


    return render(request, 'core/request_detail_reviewer.html', {
        'analysts': analysts,'request': request_object, 'status': request_status, 'real_status': real_status,
        'form': form, 'submitted_date': request_submitted_date, 'group_name': group.name,
        'comments': request_statuses_with_comments, 'company_logo': company_logo,'is_corporate': True,
        'client_attachments': client_attachments, 'formset': formset,
        'analyst_notes_form':analyst_notes_form,'is_reviewer':True
    })




####################################
#
# DETAIL VIEW HELPERS
#
####################################

def generate_analyst_internal_doc_form(request,request_object):
    analyst_internal_doc = None
    if request_object.analyst_internal_doc is not None:
        analyst_internal_doc = request_object.analyst_internal_doc
    
    form = AnalystInternalDocForm(analyst_internal_doc=analyst_internal_doc)

    return form

def generate_analyst_notes_form(request,request_object):
    analyst_notes = ""
    if len(request_object.analyst_notes) > 0:
        analyst_notes = request_object.analyst_notes
    
    form = AnalystNotesForm(analyst_notes=analyst_notes)

    return form

def generate_analyst_request_detail_status_form(request,request_object):
    request_detail_statuses=[]
    if isinstance(request_object, Request):
            request_detail_statuses = RequestDetailStatus.objects.filter(request=request_object).values("status","reason")
    elif isinstance(request_object, CustomRequest):
        request_detail_statuses = CustomRequestDetailStatus.objects.filter(request=request_object).values("status","reason")
    else:
        request_detail_statuses = CorporateRequestDetailStatus.objects.filter(request=request_object).values("status","reason")

    request_detail_other_text = [ x["reason"] for x in request_detail_statuses if x["status"] == RequestDetailStatus.OTHER]
    request_detail_other_text = request_detail_other_text[0] if len(request_detail_other_text) > 0 else ""
    request_detail_statuses = [ x["status"] for x in request_detail_statuses]
    
    form = AnalystRequestDetailStatusForm(request.POST or None,request_detail_statuses=request_detail_statuses,request_detail_other_text=request_detail_other_text)

    return form

def generate_form_for_detail_view(request, group, request_status, request_object, render_rich_text):
    try:
        if isinstance(request_object, Request):
            service_statuses = RequestServiceStatus.objects.filter(request=request_object)
        elif isinstance(request_object, CustomRequest):
            service_statuses = CustomRequestServiceStatus.objects.filter(request=request_object)
        else:
            service_statuses = CorporateRequestServiceStatus.objects.filter(request=request_object)
    except Exception, e:
        service_statuses = []

    service_selections = CompanyServiceSelection.get_service_selections_for_request(request_object)

    analyst_butons = False
    reviewer_buttons = False
    pending = False

    if isinstance(request_object,Request) and request_object.pending == False:
        pending= True

    if isinstance(request_object, Request) or isinstance(request_object, CustomRequest) or\
            isinstance(request_object, CorporateRequest):
        if (group.name == SPOTLIT_ANALYST_GROUP) and (request_status == Status.IN_PROGRESS_STATUS):
            analyst_butons = True
        elif (group.name == REVIEWER) and (request_status == Status.REVIEW_STATUS):
            reviewer_buttons = True



    attachment = None
    if request_object.attachment is not None and request_object.attachment.name is not None and len(
            request_object.attachment.name) > 0:
        attachment = request_object.attachment

    executive_summary = ""
    if len(request_object.executive_summary) > 0:
        executive_summary = request_object.executive_summary

    form = ServicesForm(request.POST or None, file=attachment, initial=service_selections,
                        analyst_buttons=analyst_butons, reviewer_buttons=reviewer_buttons, render_rich_text=render_rich_text,
                        service_statuses=service_statuses, executive_summary=executive_summary,pending=pending)

    return form

def generate_surcharge_formset_for_detail_view(request, request_object):
    formset_factory =  modelformset_factory(Surcharge, form=SurchargeForm, can_delete=True, extra=0)

    try:
        if isinstance(request_object, Request):
            surcharges = Surcharge.objects.filter(request_id=request_object.display_id, request_type="Request")
        elif isinstance(request_object, CustomRequest):
            surcharges = Surcharge.objects.filter(request_id=request_object.display_id, request_type="Custom Request")
        else:
            surcharges = Surcharge.objects.filter(request_id=request_object.display_id, request_type="Corporate Request")
    except Exception, e:
        surcharges  = None

    formset = formset_factory(queryset=surcharges)

    return formset

def save_attachment(request, request_object, data):
    save_successful = True
    clear = False
    if 'attachment-clear' in data:
        clear_value = data['attachment-clear']
        if clear_value == 'on':
            clear = True
    if clear:
        request_object.attachment = None
    elif 'attachment' in request.FILES:
        attachment = request.FILES['attachment']
        if (correct_file_type(attachment)):
            request_object.attachment = attachment
        else:
            save_successful = False
    request_object.save()
    return save_successful


def save_executive_summary(request_object, data):
    if 'executive_summary' in data:
        executive_summary = data['executive_summary']
        if executive_summary != request_object.executive_summary:
            request_object.executive_summary = executive_summary
            request_object.save()

def save_analyst_notes(request_object, request_post):
    if 'analyst_notes' in request_post:
        analyst_notes = request_post['analyst_notes']
        if analyst_notes != request_object.analyst_notes:
            request_object.analyst_notes = analyst_notes
            request_object.save()

def save_analyst_internal_doc(request, request_object,form):
    if 'analyst_internal_doc' not in request.FILES:
        return True

    if 'analyst_internal_doc-clear' in request.POST:
        request_object.analyst_internal_doc = None
        request_object.save()
        return True

    elif 'analyst_internal_doc' in request.FILES:
        analyst_internal_doc = request.FILES['analyst_internal_doc']
        if (correct_file_type(analyst_internal_doc)):
            request_object.analyst_internal_doc = analyst_internal_doc
            request_object.save()
            return True
        else:
            form._errors = {}
            form._errors['analyst_internal_doc'] = ["File must be PDF, Zip or Microsoft Word File."]
            return False

def correct_file_type(attachment):
    is_good_type = False
    file_type = magic.from_buffer(attachment.read(1024))
    match = r'PDF document|Microsoft Office Document|Zip archive data'
    good_type = re.search(match, file_type)
    if good_type is not None:
        is_good_type = True
    return is_good_type


def handle_detail_view_post(request, form, formset, request_object, redirect_to):
    if (request.method == 'POST'):
        if ('save_services' in request.POST):
            data = form.data
            save_request_statuses(data, request_object)
            save_executive_summary(request_object, data)
            save_successful = save_attachment(request, request_object, data)
            if not formset.is_valid():
                return None
            if (save_successful):
                if isinstance(request_object, Request):
                    return HttpResponseRedirect(reverse('request_analyst', kwargs={"pk": request_object.pk}))
                elif isinstance(request_object, CustomRequest):
                    return HttpResponseRedirect(reverse('request_analyst_for_custom', kwargs={"pk": request_object.pk}))
                else:
                    return HttpResponseRedirect(
                        reverse('request_analyst_for_corporate', kwargs={"pk": request_object.pk}))
            else:
                form._errors = {}
                form._errors['attachment'] = ["File must be PDF, Zip or Microsoft Word File."]
                return None

        elif 'save_services_reviewer' in request.POST:
            data = form.data
            save_request_statuses(data, request_object)
            save_executive_summary(request_object, data)
            save_successful = save_attachment(request, request_object, data)
            if not formset.is_valid():
                return None
            if (save_successful):
                if isinstance(request_object, Request):
                    return HttpResponseRedirect(reverse('request_reviewer', kwargs={"pk": request_object.pk}))
                elif isinstance(request_object, CustomRequest):
                    return HttpResponseRedirect(reverse('request_reviewer_for_custom', kwargs={"pk": request_object.pk}))
                else:
                    return HttpResponseRedirect(
                        reverse('request_reviewer_for_corporate', kwargs={"pk": request_object.pk}))
            else:
                form._errors = {}
                form._errors['attachment'] = ["File must be PDF, Zip or Microsoft Word File."]
                return None

        elif 'submit_as_pending' in request.POST:
            if not formset.is_valid():
                return None
            if (form.is_valid()):
                data = form.cleaned_data
                errors = check_for_required_comments(form, data)
                if not errors:
                    send_status_change_email(request_object, request_object.reviewer.user, Status.REVIEW_STATUS)
                    save_request_statuses(data, request_object)
                    save_executive_summary(request_object, data)
                    save_successful = save_attachment(request, request_object, data)
                    if (save_successful):
                        request_object.pending=True
                        request_object.save()
                        request_status = Status.add_request_status(request_object, Status.REVIEW_STATUS, "")
                        return HttpResponseRedirect(reverse_lazy(redirect_to))
                    else:
                        if (form._errors is None):
                            form._errors = {}
                        form._errors['attachment'] = ["File must be PDF, Zip file or Microsoft Word File."]
                        return None

        elif ('submit_request_for_review' in request.POST):
            # the analyst submits to the reviewer
            if not formset.is_valid():
                return None
            if (form.is_valid()):
                data = form.cleaned_data
                errors = check_for_required_comments(form, data)
                if not errors:
                    if isinstance(request_object, Request):
                        send_status_change_email(request_object, request_object.reviewer.user, Status.REVIEW_STATUS)
                    elif isinstance(request_object, CustomRequest):
                        send_status_change_email_for_custom(request_object, request_object.reviewer.user, Status.REVIEW_STATUS)
                    else:
                        send_status_change_email_for_corporate(request_object, request_object.reviewer.user, Status.REVIEW_STATUS)

                    save_request_statuses(data, request_object)
                    save_executive_summary(request_object, data)
                    save_successful = save_attachment(request, request_object, data)
                    if (save_successful):
                        request_status = Status.add_request_status(request_object, Status.REVIEW_STATUS, "")
                        return HttpResponseRedirect(reverse_lazy(redirect_to))
                    else:
                        if (form._errors is None):
                            form._errors = {}
                        form._errors['attachment'] = ["File must be PDF, Zip file or Microsoft Word File."]
                        return None



        elif ('submit_request' in request.POST):
            # the reviewer submits to the manager
            if not formset.is_valid():
                return None
            if (form.is_valid()):
                data = form.cleaned_data
                errors = check_for_required_comments(form, data)

                if (not errors):
                    save_request_statuses(data, request_object)
                    save_executive_summary(request_object, data)
                    save_successful = save_attachment(request, request_object, data)

                    #send email to manager, to inform that request was completed
                    if (save_successful):
                        request_manager_user = User.objects.get(username=settings.REQUEST_VOYINT_MANAGER_USERNAME)
                        if isinstance(request_object, Request):
                            request_status = Status.add_request_status(request_object,
                                                                              Status.COMPLETED_STATUS, "")

                            send_status_change_email(request_object, request_manager_user, Status.COMPLETED_STATUS)
                            request_object.completed_status = request_status
                            request_object.save()
                        elif isinstance(request_object, CustomRequest):
                            request_status = Status.add_request_status(request_object,
                                                                              Status.COMPLETED_STATUS, "")

                            #send email to manager, to inform that request was completed
                            send_status_change_email_for_custom(request_object, request_manager_user, Status.COMPLETED_STATUS)


                            request_object.completed_status = request_status
                            request_object.save()

                        else:
                            request_status = Status.add_request_status(request_object,
                                                                                       Status.COMPLETED_STATUS,
                                                                                       "")

                            #send email to manager, to inform that request was completed
                            send_status_change_email_for_corporate(request_object,
                                                                   request_manager_user,
                                                                   Status.COMPLETED_STATUS)

                            request_object.completed_status = request_status
                            request_object.save()
                        return HttpResponseRedirect(reverse_lazy(redirect_to))
                    else:
                        if (form._errors is None):
                            form._errors = {}
                        form._errors['attachment'] = ["File must be PDF, Zip file or Microsoft Word File."]
                        return None

    return None


def check_for_required_comments(form, data):
    return_val = False
    for field in data:
        if 'selection' in field:
            selection = data[field]
            if (selection == 'True'):
                index = field[field.find("_") + 1:len(field)]
                comments = data["comment_" + index]
                if len(comments) == 0:
                    form._errors[field] = ['Comments required.']
                    return_val = True
    return return_val

def handle_analyst_request_detail_status_form(request_object,request_post,form):
    if "save_services" in request_post or "submit_as_pending" in request_post:
        request_detail_statuses = request_post.getlist("request_analyst_status")
        if len(request_detail_statuses) == 0:
            form._errors = {}
            form._errors['request_analyst_status'] = ["At least one status should be marked"]
            return None
        request_detail_other_text = request_post["request_analyst_status_other_text"]
        if str(BaseRequestDetailStatus.OTHER) in request_detail_statuses and (request_detail_other_text == "" or request_detail_other_text is None):
            form._errors = {}
            form._errors['request_analyst_status_other_text'] = ["Please mention other status"]
            return None
        save_request_detail_statuses(request_detail_statuses,request_object,request_detail_other_text)

    elif "submit_request_for_review" in request_post:
        request_detail_statuses = request_post.getlist("request_analyst_status")
        if str(BaseRequestDetailStatus.OTHER) in request_detail_statuses:
            request_detail_statuses.remove(str(BaseRequestDetailStatus.OTHER))
        if len(request_detail_statuses) != 6:
            form._errors = {}
            form._errors['request_analyst_status'] = ["All statuses should be marked(except 'Other')"]
            return None
        save_request_detail_statuses(request_detail_statuses,request_object)
    
    return True

def save_request_detail_statuses(request_detail_statuses,request_object,reason = None):
    if isinstance(request_object,Request):
        RequestDetailStatus.objects.filter(request=request_object).delete()
    elif isinstance(request_object,CorporateRequest):
        CorporateRequestDetailStatus.objects.filter(request=request_object).delete()
    else :
        CustomRequestDetailStatus.objects.filter(request=request_object).delete()
    
    for status in request_detail_statuses:
        if int(status) == BaseRequestDetailStatus.OTHER:
            if isinstance(request_object,Request):
                RequestDetailStatus(request=request_object,status=status,reason=reason,datetime=datetime.datetime.now()).save()
            elif isinstance(request_object,CorporateRequest):
                CorporateRequestDetailStatus(request=request_object,status=status,reason=reason,datetime=datetime.datetime.now()).save()
            else :
                CustomRequestDetailStatus(request=request_object,status=status,reason=reason,datetime=datetime.datetime.now()).save()
        else:
            if isinstance(request_object,Request):
                RequestDetailStatus(request=request_object,status=status,datetime=datetime.datetime.now()).save()
            elif isinstance(request_object,CorporateRequest):
                CorporateRequestDetailStatus(request=request_object,status=status,datetime=datetime.datetime.now()).save()
            else :
                CustomRequestDetailStatus(request=request_object,status=status,datetime=datetime.datetime.now()).save()


def save_request_statuses(data, request_object):
    for field in data:
        if 'selection' in field:
            index = field[field.find("_") + 1:len(field)]
            comments = data["comment_" + index]
            result = data[field]
            if (result == 'False'):
                comments = ""
            service_selection = CompanyServiceSelection.objects.get(pk=index)
            if isinstance(request_object, Request):
                RequestServiceStatus.save_request_service_status(request_object, service_selection, result, comments)
            elif isinstance(request_object, CustomRequest):
                CustomRequestServiceStatus.save_request_service_status(request_object, service_selection, result, comments)
            else:
                CorporateRequestServiceStatus.save_request_service_status(request_object, service_selection, result,
                                                                          comments)

def save_surcharges(request_post, request_object):
    formset_factory =  modelformset_factory(Surcharge, form=SurchargeForm, can_delete=True, extra=1)


    request_type = ''
    #Get Request Type
    if isinstance(request_object, Request):
        request_type = "Request"
    elif isinstance(request_object, CustomRequest):
        request_type = "Custom Request"
    else:
        request_type = "Corporate Request"

    formset = formset_factory(request_post, Surcharge.objects.all())

    if formset.is_valid():
        for form in formset:
            if form.is_valid():
                if form.cleaned_data != {}:
                    if form.cleaned_data["id"]:
                        sur = Surcharge.objects.get(pk=form.cleaned_data["id"].pk)
                        sur.request_id = request_object.display_id
                        sur.request_type = request_type
                        sur.ref_number = form.cleaned_data.get('ref_number')
                        sur.estimated_cost = form.cleaned_data.get('estimated_cost')
                        sur.charge_type = form.cleaned_data.get('charge_type')
                        sur.source = form.cleaned_data.get('source')
                        sur.order_number = form.cleaned_data.get('order_number')
                        sur.processing_fee = form.cleaned_data.get('processing_fee')
                        sur.save()
                    else:
                        sur = Surcharge(request_id=request_object.display_id, request_type=request_type, \
                            ref_number=form.cleaned_data.get('ref_number'), estimated_cost=form.cleaned_data.get('estimated_cost'), \
                                charge_type=form.cleaned_data.get('charge_type'),source=form.cleaned_data.get('source'), \
                                    order_number=form.cleaned_data.get('order_number'),processing_fee=form.cleaned_data.get('processing_fee'))
                        sur.save()

        #Get forms that were marked to be deleted
        marked_for_delete = formset.deleted_forms
        for form in marked_for_delete:
            data = form.cleaned_data
            #Only delete forms with data in them
            #Blank forms marked for delte will have an id of None
            if data["id"]:
                data["id"].delete()



    return formset

####################################
#
# REQUEST ACTIONS
#
####################################

@login_required
def assign_staff(request, pk):
    current_user = request.user
    if (not is_manager(current_user) or not request_is_valid(pk)):
        return redirect_to_dashboard(current_user)

    request_object = get_object_or_404(Request, pk=pk)

    status = request_object.get_request_status()
    if (status is not Status.NEW_STATUS and status is not Status.AWAITING_DATA_FORM_APPROVAL):
        return redirect_to_dashboard(current_user)
    try:
        selected_analyst = SpotLitStaff.objects.get(pk=request.POST['analyst'])
    except (KeyError, SpotLitStaff.DoesNotExist):
        return HttpResponseServerError("Invalid analyst selection.")

    try:
        selected_reviewer = SpotLitStaff.objects.get(pk=request.POST['reviewer'])
    except (KeyError, SpotLitStaff.DoesNotExist):
        return HttpResponseServerError("Invalid reviewer selection")


    else:
        comments = ""
        if 'comments' in request.POST:
            comments = request.POST['comments']
        request_object.assignment = selected_analyst
        request_object.reviewer = selected_reviewer
        due_date = request.POST["due_date"]
        request_object.due_date = due_date
        request_object.save()
        request_status = Status(content_object=request_object, status=Status.ASSIGNED_STATUS, comments=comments,
                                       datetime=datetime.datetime.now())
        request_status.save()

        #send email to analyst, to inform that request was assigned to them
        send_status_change_email(request_object, request_object.assignment.user, Status.ASSIGNED_STATUS)

        return HttpResponse("Successful assignment")


@login_required
def assign_corporate_staff(request, pk):
    current_user = request.user
    if (not is_manager(current_user) or not corporate_request_is_valid(pk)):
        return redirect_to_dashboard(current_user)

    request_object = get_object_or_404(CorporateRequest, pk=pk)

    status = request_object.get_request_status()
    if (status is not Status.NEW_STATUS and status is not Status.AWAITING_DATA_FORM_APPROVAL):
        return redirect_to_dashboard(current_user)

    try:
        selected_analyst = SpotLitStaff.objects.get(pk=request.POST['analyst'])
    except (KeyError, SpotLitStaff.DoesNotExist):
        return HttpResponseServerError("Invalid analyst selection.")
    try:
        selected_reviewer = SpotLitStaff.objects.get(pk=request.POST['reviewer'])
    except (KeyError, SpotLitStaff.DoesNotExist):
        return HttpResponseServerError("Invalid reviewer selection")


    else:
        comments = ""
        if 'comments' in request.POST:
            comments = request.POST['comments']
        request_object.assignment = selected_analyst
        request_object.reviewer = selected_reviewer
        due_date = request.POST["due_date"]
        request_object.due_date = due_date
        request_object.save()
        request_status = Status(content_object=request_object,
                                                status=Status.ASSIGNED_STATUS, comments=comments,
                                                datetime=datetime.datetime.now())
        request_status.save()

        #send email to analyst, to inform that request was assigned to them
        send_status_change_email_for_corporate(request_object, request_object.assignment.user,
                                               Status.ASSIGNED_STATUS)

        return HttpResponse("Successful assignment")


@login_required
def assign_custom_staff(request, pk):

    current_user = request.user
    if (not is_manager(current_user) or not custom_request_is_valid(pk)):
        return redirect_to_dashboard(current_user)

    custom_request = get_object_or_404(CustomRequest, pk=pk)

    status = custom_request.get_request_status()
    if (status is not Status.NEW_STATUS and status is not Status.AWAITING_DATA_FORM_APPROVAL):
        return redirect_to_dashboard(current_user)

    try:
        selected_analyst = SpotLitStaff.objects.get(pk=request.POST['analyst'])
    except (KeyError, SpotLitStaff.DoesNotExist):
        return HttpResponseServerError("Invalid analyst selection.")

    try:
        selected_reviewer = SpotLitStaff.objects.get(pk=request.POST['reviewer'])
    except (KeyError, SpotLitStaff.DoesNotExist):
        return HttpResponseServerError("Invalid reviewer selection")


    else:
        comments = ""
        if 'comments' in request.POST:
            comments = request.POST['comments']
        custom_request.assignment = selected_analyst
        custom_request.reviewer = selected_reviewer
        due_date = request.POST["due_date"]
        custom_request.due_date = due_date
        custom_request.save()

        request_status = Status(content_object=custom_request, status=Status.ASSIGNED_STATUS, comments=comments,
                                datetime=datetime.datetime.now())
        request_status.save()

        #send email to analyst, to inform that request was assigned to them
        send_status_change_email(custom_request, custom_request.assignment.user, Status.ASSIGNED_STATUS)

        return HttpResponse("Successful assignment")


@login_required
def begin_request(request, pk):
    current_user = request.user
    if (not is_analyst(current_user) or not request_is_valid(pk)):
        return redirect_to_dashboard(current_user)

    request_object = get_object_or_404(Request, pk=pk)

    status = request_object.get_request_status()

    if (status is not Status.ASSIGNED_STATUS and status is not Status.NEW_RETURNED_STATUS):
        return redirect_to_dashboard(current_user)

    request_status = Status(content_object=request_object, status=Status.IN_PROGRESS_STATUS,
                                   datetime=datetime.datetime.now())
    request_status.save()

    if request_object.in_progress_status is None:
        request_object.in_progress_status = request_status
        request_object.save()

    return HttpResponse("Begin request")


@login_required
def begin_corporate_request(request, pk):
    current_user = request.user
    if (not is_analyst(current_user) or not corporate_request_is_valid(pk)):
        return redirect_to_dashboard(current_user)

    request_object = get_object_or_404(CorporateRequest, pk=pk)

    status = request_object.get_request_status()

    if (status is not Status.ASSIGNED_STATUS and status is not Status.NEW_RETURNED_STATUS):
        return redirect_to_dashboard(current_user)

    request_status = Status(content_object=request_object,
                                            status=Status.IN_PROGRESS_STATUS,
                                            datetime=datetime.datetime.now())
    request_status.save()


    if request_object.in_progress_status is None:

        request_object.in_progress_status = request_status
        request_object.save()



    return HttpResponse("Begin request")


@login_required
def begin_custom_request(request, pk):
    current_user = request.user
    if (not is_analyst(current_user) or not custom_request_is_valid(pk)):
        return redirect_to_dashboard(current_user)

    custom_request = get_object_or_404(CustomRequest, pk=pk)

    status = custom_request.get_request_status()

    if (status is not Status.ASSIGNED_STATUS and status is not Status.NEW_RETURNED_STATUS):
        return redirect_to_dashboard(current_user)

    request_status = Status(content_object=custom_request, status=Status.IN_PROGRESS_STATUS,
                            datetime=datetime.datetime.now())


    request_status.save()

    if custom_request.in_progress_status is None:
        custom_request.in_progress_status = request_status
        custom_request.save()
    return HttpResponse("Begin request")


@login_required
def reject_request(request, pk):
    current_user = request.user
    if (not is_analyst(current_user) or not request_is_valid(pk)):
        return redirect_to_dashboard(current_user)

    request_object = get_object_or_404(Request, pk=pk)

    status = request_object.get_request_status()
    if (status is not Status.IN_PROGRESS_STATUS and status is not Status.ASSIGNED_STATUS
        and status is not Status.NEW_RETURNED_STATUS):
        return HttpResponse("Rejection Failed")

    if (request.method == 'POST'):
        comments = ""
        if 'comments' in request.POST:
            comments = request.POST['comments']
        request_status = Status(content_object=request_object, status=Status.REJECTED_STATUS, comments=comments,
                                       datetime=datetime.datetime.now())
        request_status.save()

        #send email to manager, to inform that request was rejected by analyst
        send_status_change_email(request_object, User.objects.get(username=settings.MANAGER_USERNAME),
                                 Status.REJECTED_STATUS)

        return HttpResponse("Rejection Successful")
    return HttpResponse("Rejection Failed")


@login_required
def reject_corporate_request(request, pk):
    current_user = request.user
    if (not is_analyst(current_user) or not corporate_request_is_valid(pk)):
        return redirect_to_dashboard(current_user)

    request_object = get_object_or_404(CorporateRequest, pk=pk)

    status = request_object.get_request_status()
    if (status is not Status.IN_PROGRESS_STATUS and status is not Status.ASSIGNED_STATUS
        and status is not Status.NEW_RETURNED_STATUS):
        return HttpResponse("Rejection Failed")

    if (request.method == 'POST'):
        comments = ""
        if 'comments' in request.POST:
            comments = request.POST['comments']
        request_status = Status(content_object=request_object,
                                                status=Status.REJECTED_STATUS, comments=comments,
                                                datetime=datetime.datetime.now())
        request_status.save()

        #send email to manager, to inform that request was rejected by analyst
        send_status_change_email_for_corporate(request_object, User.objects.get(username=settings.MANAGER_USERNAME),
                                               Status.REJECTED_STATUS)

        return HttpResponse("Rejection Successful")
    return HttpResponse("Rejection Failed")


@login_required
def reject_custom_request(request, pk):
    current_user = request.user
    if (not is_analyst(current_user) or not custom_request_is_valid(pk)):
        return redirect_to_dashboard(current_user)

    custom_request = get_object_or_404(CustomRequest, pk=pk)

    status = custom_request.get_request_status()
    if (status is not Status.IN_PROGRESS_STATUS and status is not Status.ASSIGNED_STATUS
        and status is not Status.NEW_RETURNED_STATUS):
        return HttpResponse("Rejection Failed")

    if (request.method == 'POST'):
        comments = ""
        if 'comments' in request.POST:
            comments = request.POST['comments']


        request_status = Status(content_object=custom_request, status=Status.REJECTED_STATUS, comments=comments,
                                datetime=datetime.datetime.now())
        request_status.save()

        #send email to manager, to inform that request was rejected by analyst
        send_status_change_email(custom_request, User.objects.get(username=settings.MANAGER_USERNAME),
                                 Status.REJECTED_STATUS)

        return HttpResponse("Rejection Successful")
    return HttpResponse("Rejection Failed")


@login_required
def incomplete_request(request, pk):
    current_user = request.user
    if (not is_manager(current_user) or not request_is_valid(pk)):
        return redirect_to_dashboard(current_user)

    request_object = get_object_or_404(Request, pk=pk)

    status = request_object.get_request_status()
    if (status is Status.SUBMITTED_STATUS or status is Status.DELETED_STATUS
        or status is Status.INCOMPLETE_STATUS):
        return HttpResponse("Incomplete Failed")

    if (request.method == 'POST'):
        comments = ""
        if 'comments' in request.POST:
            comments = request.POST['comments']
        request_status = Status(content_object=request_object, status=Status.INCOMPLETE_STATUS,
                                       comments=comments, datetime=datetime.datetime.now())
        request_status.save()

        #send email to company employee, to inform that request was marked incomplete
        send_status_change_email(request_object, request_object.created_by.user, Status.INCOMPLETE_STATUS)

        return HttpResponse("Incomplete Successful")
    return HttpResponse("Incomplete failed")


@login_required
def incomplete_corporate_request(request, pk):
    current_user = request.user
    if (not is_manager(current_user) or not corporate_request_is_valid(pk)):
        return redirect_to_dashboard(current_user)

    request_object = get_object_or_404(CorporateRequest, pk=pk)

    status = request_object.get_request_status()
    if (status is Status.SUBMITTED_STATUS or status is Status.DELETED_STATUS
        or status is Status.INCOMPLETE_STATUS):
        return HttpResponse("Incomplete Failed")

    if (request.method == 'POST'):
        comments = ""
        if 'comments' in request.POST:
            comments = request.POST['comments']
        request_status = Status(content_object=request_object,
                                                status=Status.INCOMPLETE_STATUS, comments=comments,
                                                datetime=datetime.datetime.now())
        request_status.save()

        #send email to company employee, to inform that request was marked incomplete
        send_status_change_email_for_corporate(request_object, request_object.created_by.user,
                                               Status.INCOMPLETE_STATUS)

        return HttpResponse("Incomplete Successful")
    return HttpResponse("Incomplete failed")


@login_required
def incomplete_custom_request(request, pk):
    current_user = request.user
    if (not is_manager(current_user) or not custom_request_is_valid(pk)):
        return redirect_to_dashboard(current_user)

    custom_request = get_object_or_404(CustomRequest, pk=pk)

    status = custom_request.get_request_status()
    if (status is Status.SUBMITTED_STATUS or status is Status.DELETED_STATUS
        or status is Status.INCOMPLETE_STATUS):
        return HttpResponse("Incomplete Failed")

    if (request.method == 'POST'):
        comments = ""
        if 'comments' in request.POST:
            comments = request.POST['comments']

        request_status = Status(content_object=custom_request, status=Status.INCOMPLETE_STATUS, comments=comments,
                                datetime=datetime.datetime.now())
        request_status.save()

        #send email to company employee, to inform that request was marked incomplete
        send_status_change_email(custom_request, custom_request.created_by.user, Status.INCOMPLETE_STATUS)

        return HttpResponse("Incomplete Successful")
    return HttpResponse("Incomplete failed")


@login_required
def submit_request(request, pk):
    current_user = request.user
    if (not is_manager(current_user) or not request_is_valid(pk)):
        return redirect_to_dashboard(current_user)

    request_object = get_object_or_404(Request, pk=pk)

    status = request_object.get_request_status()
    if (status is not Status.COMPLETED_STATUS):
        return HttpResponse("Submit Failed")

    if (request.method == 'POST'):
        comments = ""
        supervisors = []
        if 'comments' in request.POST:
            comments = request.POST['comments']
        
        if 'supervisors' in request.POST:
            supervisors = json.loads(request.POST['supervisors'])
        
        request_status = Status(content_object=request_object, status=Status.SUBMITTED_STATUS, comments=comments,
                                       datetime=datetime.datetime.now())
        request_status.save()

        #Save Individual Request Report
        display_archive_individual_report(request_object, True)

        #send email to company employee to let them know the request is complete
        if len(supervisors) != 0:
            employees = CompanyEmployee.objects.filter(pk__in=supervisors)
            for employee in employees:
                try:
                    RequestSelectedSupervisor.objects.get(supervisor=employee)
                except: 
                    RequestSelectedSupervisor.objects.create(supervisor=employee, request= request_object)
                send_status_change_email(request_object, employee.user, Status.SUBMITTED_STATUS)      
        else:
            send_status_change_email(request_object, request_object.created_by.user, Status.SUBMITTED_STATUS)

        if request_object.submitted_status is None:
            request_object.submitted_status = request_status
            request_object.save()

        return HttpResponse("Submit successful")
    return HttpResponse("Submit failed")


@login_required
def submit_corporate_request(request, pk):
    current_user = request.user
    if (not is_manager(current_user) or not corporate_request_is_valid(pk)):
        return redirect_to_dashboard(current_user)

    request_object = get_object_or_404(CorporateRequest, pk=pk)

    status = request_object.get_request_status()
    if (status is not Status.COMPLETED_STATUS):
        return HttpResponse("Submit Failed")

    if (request.method == 'POST'):
        comments = ""
        supervisors = []
        if 'comments' in request.POST:
            comments = request.POST['comments']
        
        if 'supervisors' in request.POST:
            supervisors = json.loads(request.POST['supervisors'])
            
        request_status = Status(content_object=request_object,
                                                status=Status.SUBMITTED_STATUS, comments=comments,
                                                datetime=datetime.datetime.now())
        request_status.save()

        #Save Corporate Request Report
        display_archive_corporate_report(request_object, True)

        #send email to company employee to let them know the request is complete
        if len(supervisors) != 0:
            employees = CompanyEmployee.objects.filter(pk__in=supervisors)
            for employee in employees:
                try:
                    CorporateRequestSelectedSupervisor.objects.get(supervisor=employee)
                except: 
                    CorporateRequestSelectedSupervisor.objects.create(supervisor=employee, corporate_request= request_object)
                send_status_change_email_for_corporate(request_object, employee.user, Status.SUBMITTED_STATUS)      
        else:
            send_status_change_email_for_corporate(request_object, request_object.created_by.user, Status.SUBMITTED_STATUS)


        if request_object.submitted_status is None:
            request_object.submitted_status = request_status
            request_object.save()

        return HttpResponse("Submit successful")
    return HttpResponse("Submit failed")


@login_required
def submit_custom_request(request, pk):
    current_user = request.user
    if (not is_manager(current_user) or not custom_request_is_valid(pk)):
        return redirect_to_dashboard(current_user)

    custom_request = get_object_or_404(CustomRequest, pk=pk)

    status = custom_request.get_request_status()
    if (status is not Status.COMPLETED_STATUS):
        return HttpResponse("Submit Failed")

    if (request.method == 'POST'):
        # Reporting_period is a field specific to E*TRADE
        if 'reporting_period' in request.POST:
            reporting_period = request.POST['reporting_period']

            # get dynamic request form from custom request..
            dynamic_request_form = custom_request.dynamic_request_form
            # get dynamic form field that name==Reporting Period and dynamic request == dynamic request
            try:
                dynamic_form_field = DynamicRequestFormFields.objects.get(
                        dynamic_request_form=dynamic_request_form, label="Reporting Period")

                custom_request_field, created = CustomRequestFields.objects.update_or_create(
                        custom_request=custom_request, form_field=dynamic_form_field, defaults={"value":reporting_period})
            except:
                return HttpResponse("Submit Failed")
        comments = ""
        supervisors = []
        if 'comments' in request.POST:
            comments = request.POST['comments']

        if 'supervisors' in request.POST:
            supervisors = json.loads(request.POST['supervisors'])

        request_status = Status(content_object=custom_request, status=Status.SUBMITTED_STATUS, comments=comments,
                                datetime=datetime.datetime.now())
        request_status.save()

        try:
            fields = CustomRequestFields.objects.filter(custom_request=custom_request)
        except CustomRequestFields.DoesNotExist:
            return HttpResponse("Submit Failed")

        #Save Individual Request Report
        display_archive_custom_report(custom_request, fields, True)


        # on submit we create a pdf and save it
        '''
        pdf = generate_pdf_file(request, custom_request.report_url)
        custom_request.pdf_report.save(custom_request.report_url+".pdf", pdf)
        '''
        #send email to company employee to let them know the request is complete
        if len(supervisors) != 0:
            employees = CompanyEmployee.objects.filter(pk__in=supervisors)
            for employee in employees:
                try:
                    CustomRequestSelectedSupervisor.objects.get(supervisor=employee)
                except: 
                    CustomRequestSelectedSupervisor.objects.create(supervisor=employee, custom_request= custom_request)
                send_status_change_email(custom_request, employee.user, Status.SUBMITTED_STATUS)      
        else:
            send_status_change_email(custom_request, custom_request.created_by.user, Status.SUBMITTED_STATUS)
        
        if custom_request.submitted_status is None:
            custom_request.submitted_status = request_status
            custom_request.save()

        return HttpResponse("Submit successful")
    return HttpResponse("Submit failed")


@login_required
def return_request(request, pk):
    current_user = request.user
    if not request_is_valid(pk):
        return redirect_to_dashboard(current_user)

    if not is_manager(current_user) and not is_reviewer(current_user):
        return redirect_to_dashboard(current_user)

    request_object = get_object_or_404(Request, pk=pk)

    status = request_object.get_request_status()
    if (status is not Status.REJECTED_STATUS and status is not Status.COMPLETED_STATUS and status is not Status.REVIEW_STATUS):
        return HttpResponse("Return Failed")

    if (request.method == 'POST'):
        comments = ""
        if 'comments' in request.POST:
            comments = request.POST['comments']
        request_status = Status(content_object=request_object, status=Status.NEW_RETURNED_STATUS,
                                       comments=comments, datetime=datetime.datetime.now())
        request_status.save()

        #send email to analyst to informt them the requst was returned by manager
        send_status_change_email(request_object, request_object.assignment.user, Status.NEW_RETURNED_STATUS)

        return HttpResponse("Return Success")
    return HttpResponse("Return Failed")


@login_required
def return_request_reviewer(request, pk):
    current_user = request.user
    if not request_is_valid(pk):
        return redirect_to_dashboard(current_user)

    if not is_manager(current_user):
        return redirect_to_dashboard(current_user)

    request_object = get_object_or_404(Request, pk=pk)

    status = request_object.get_request_status()
    if (status is not Status.REJECTED_STATUS and status is not Status.COMPLETED_STATUS):
        return HttpResponse("Return Failed")

    if (request.method == 'POST'):
        comments = ""
        if 'comments' in request.POST:
            comments = request.POST['comments']
        request_status = Status(content_object=request_object, status=Status.REVIEW_STATUS,
                                       comments=comments, datetime=datetime.datetime.now())
        request_status.save()

        return HttpResponse("Return Success")
    return HttpResponse("Return Failed")


@login_required
def return_corporate_request(request, pk):
    current_user = request.user
    if not corporate_request_is_valid(pk):
        return redirect_to_dashboard(current_user)

    if not is_manager(current_user) and not is_reviewer(current_user):
        return redirect_to_dashboard(current_user)

    request_object = get_object_or_404(CorporateRequest, pk=pk)

    status = request_object.get_request_status()
    if (status is not Status.REJECTED_STATUS and status is not Status.COMPLETED_STATUS and
                status is not Status.REVIEW_STATUS):
        return HttpResponse("Return Failed")

    if (request.method == 'POST'):
        comments = ""
        if 'comments' in request.POST:
            comments = request.POST['comments']
        request_status = Status(content_object=request_object,
                                                status=Status.NEW_RETURNED_STATUS, comments=comments,
                                                datetime=datetime.datetime.now())
        request_status.save()

        #send email to analyst to informt them the requst was returned by manager
        send_status_change_email_for_corporate(request_object, request_object.assignment.user,
                                               Status.NEW_RETURNED_STATUS)

        return HttpResponse("Return Success")
    return HttpResponse("Return Failed")


@login_required
def return_corporate_request_reviewer(request, pk):
    current_user = request.user
    if not corporate_request_is_valid(pk):
        return redirect_to_dashboard(current_user)

    if not is_manager(current_user):
        return redirect_to_dashboard(current_user)

    request_object = get_object_or_404(CorporateRequest, pk=pk)

    status = request_object.get_request_status()
    if (status is not Status.REJECTED_STATUS and status is not Status.COMPLETED_STATUS):
        return HttpResponse("Return Failed")

    if (request.method == 'POST'):

        comments = ""
        if 'comments' in request.POST:
            comments = request.POST['comments']
        request_status = Status(content_object=request_object,
                                status=Status.REVIEW_STATUS, comments=comments,
                                datetime=datetime.datetime.now())
        request_status.save()

        return HttpResponse("Return Success")
    return HttpResponse("Return Failed")


@login_required
def return_custom_request(request, pk):
    current_user = request.user
    if not custom_request_is_valid(pk):
        return redirect_to_dashboard(current_user)

    if not is_manager(current_user) and not is_reviewer(current_user):
        return redirect_to_dashboard(current_user)


    custom_request = get_object_or_404(CustomRequest, pk=pk)

    status = custom_request.get_request_status()
    if (status is not Status.REJECTED_STATUS and status is not Status.COMPLETED_STATUS and status is not Status.REVIEW_STATUS):
        return HttpResponse("Return Failed")

    if (request.method == 'POST'):
        comments = ""
        if 'comments' in request.POST:
            comments = request.POST['comments']
        request_status = Status(content_object=custom_request, status=Status.NEW_RETURNED_STATUS,
                                       comments=comments, datetime=datetime.datetime.now())
        request_status.save()

        #send email to analyst to informt them the requst was returned by manager
        send_status_change_email(custom_request, custom_request.assignment.user, Status.NEW_RETURNED_STATUS)

        return HttpResponse("Return Success")
    return HttpResponse("Return Failed")


@login_required
def return_custom_request_reviewer(request, pk):
    current_user = request.user
    if not custom_request_is_valid(pk):
        return redirect_to_dashboard(current_user)

    if not is_manager(current_user):
        return redirect_to_dashboard(current_user)


    custom_request = get_object_or_404(CustomRequest, pk=pk)

    status = custom_request.get_request_status()
    if (status is not Status.REJECTED_STATUS and status is not Status.COMPLETED_STATUS):
        return HttpResponse("Return Failed")

    if (request.method == 'POST'):
        comments = ""
        if 'comments' in request.POST:
            comments = request.POST['comments']
        request_status = Status(content_object=custom_request, status=Status.REVIEW_STATUS,
                                       comments=comments, datetime=datetime.datetime.now())
        request_status.save()
        return HttpResponse("Return Success")
    return HttpResponse("Return Failed")


@login_required
def delete_request(request, pk):
    current_user = request.user
    if (not is_company_employee(current_user) or not request_is_valid(pk)):
        return redirect_to_dashboard(current_user)

    request_object = get_object_or_404(Request, pk=pk)

    status = request_object.get_request_status()
    if (status is not Status.INCOMPLETE_STATUS):
        return HttpResponse("Incomplete Failed")

    request_status = Status(content_object=request_object, status=Status.DELETED_STATUS,
                                   datetime=datetime.datetime.now())
    request_status.save()

    #send email to manager, to inform that request was deleted
    send_status_change_email(request_object, User.objects.get(username=settings.MANAGER_USERNAME),
                             Status.DELETED_STATUS)

    return HttpResponse("Deleted request")


@login_required
def delete_corporate_request(request, pk):
    current_user = request.user
    if (not is_company_employee(current_user) or not corporate_request_is_valid(pk)):
        return redirect_to_dashboard(current_user)

    request_object = get_object_or_404(CorporateRequest, pk=pk)

    status = request_object.get_request_status()
    if (status is not Status.INCOMPLETE_STATUS):
        return HttpResponse("Incomplete Failed")

    request_status = Status(content_object=request_object,
                                            status=Status.DELETED_STATUS,
                                            datetime=datetime.datetime.now())
    request_status.save()

    #send email to manager, to inform that request was deleted
    send_status_change_email_for_corporate(request_object, User.objects.get(username=settings.MANAGER_USERNAME),
                                           Status.DELETED_STATUS)

    return HttpResponse("Deleted request")


@login_required
def delete_custom_request(request, pk):
    current_user = request.user
    if (not is_company_employee(current_user) or not custom_request_is_valid(pk)):
        return redirect_to_dashboard(current_user)

    custom_request = get_object_or_404(CustomRequest, pk=pk)

    status = custom_request.get_request_status()
    if (status is not Status.INCOMPLETE_STATUS):
        return HttpResponse("Delete Failed")

    request_status = Status(content_object=custom_request, status=Status.DELETED_STATUS,
                                   datetime=datetime.datetime.now())
    request_status.save()

    #send email to manager, to inform that request was deleted
    send_status_change_email(custom_request, User.objects.get(username=settings.MANAGER_USERNAME),
                             Status.DELETED_STATUS)

    return HttpResponse("Deleted custom request")


@login_required
def archive_request(request, pk):
    current_user = request.user
    if ((not is_company_supervisor_mixin_check(current_user) and not is_company_employee(current_user) ) or not request_is_valid(pk)):
        return redirect_to_dashboard(current_user)
    

    request_object = get_object_or_404(Request, pk=pk)

    status = request_object.get_request_status()
    if (status is not Status.COMPLETED_STATUS and status is not Status.SUBMITTED_STATUS):
        return HttpResponse("Archive Failed")

    if (request.method == 'POST'):
        request_status = Status(content_object=request_object, status=Status.ARCHIVED_STATUS, datetime=datetime.datetime.now())
        request_status.save()

        return HttpResponse("Archive Successful")
    return HttpResponse("Archive Failed")

@login_required
def archive_bulk_request(request):
    if (request.method == 'POST'): 
        data = json.loads(request.body)
        requests = data['requests']
        if len(requests) != 0:
            for req in requests:
                if req['type'] == 'individual':
                    archive_request(request,req['id'])
                elif req['type'] == 'custom':
                    archive_custom_request(request,req['id'])
                elif req['type'] == 'corporate':
                    archive_corporate_request(request,req['id'])
        return HttpResponse("Bulk Archive Successful")


@login_required
def archive_bulk_page(request):
    current_user = request.user
    if(is_company_supervisor_mixin_check(current_user) or is_company_employee(current_user)):

        supervisor = get_company_employee(current_user)
        company = supervisor.company.name
        ids = list(Status.get_all_current_ids_queryset_for_company(company))

        submitted_custom_request_ids = Status.objects.filter(
            id__in=ids, status=Status.SUBMITTED_STATUS).values_list('custom_request__id', flat=True)

        submitted_corporate_request_ids = Status.objects.filter(
            id__in=ids, status=Status.SUBMITTED_STATUS).values_list("corporate_request__id", flat=True)

        submitted_individual_request_ids = Status.objects.filter(
            id__in=ids, status=Status.SUBMITTED_STATUS).values_list("request__id", flat=True)


        completed_custom_statuses = Status.objects.filter(
            custom_request__id__in=submitted_custom_request_ids, status=Status.COMPLETED_STATUS).order_by(
            'custom_request__id', '-datetime').distinct('custom_request__id').values_list("id", flat=True)
        completed_corp_statuses = Status.objects.filter(
            corporate_request__id__in=submitted_corporate_request_ids, status=Status.COMPLETED_STATUS).order_by(
            'corporate_request__id', '-datetime').distinct('corporate_request__id').values_list("id", flat=True)

        completed_ind_statuses = Status.objects.filter(
            request__id__in=submitted_individual_request_ids, status=Status.COMPLETED_STATUS).order_by(
            'request__id', '-datetime').distinct('request__id').values_list("id", flat=True)

        status_ids = list(chain(completed_custom_statuses, completed_corp_statuses, completed_ind_statuses))

        statuses = Status.objects.filter(id__in=status_ids).order_by('-datetime')

        print "STATUSSSESSSS -> ", statuses[0].content_object.display_id


        return render(request, "core/bulk_archive.html", {
            'statuses':statuses
            # 'company_logo_active': company_logo_active,
            # 'company_logo': company_logo,
            # 'is_corporate': is_corporate,
            # 'is_corporate_sidebar': is_corporate,
            # 'is_custom_sidebar': is_custom,
            # 'is_individual': is_individual,
            # 'is_custom': is_custom,
            # 'analysts': analysts,
            # 'custom_requests': custom_requests,
            # 'supervisor': supervisor,
            # 'company': supervisor.company,
        })


    else:
        return redirect_to_dashboard(current_user)


@login_required
def archive_corporate_request(request, pk):
    current_user = request.user
    if ((not is_company_supervisor_mixin_check(current_user) and not is_company_employee(current_user) ) or not corporate_request_is_valid(pk)):
        return redirect_to_dashboard(current_user)

    request_object = get_object_or_404(CorporateRequest, pk=pk)

    status = request_object.get_request_status()
    if (status is not Status.COMPLETED_STATUS and status is not Status.SUBMITTED_STATUS):
        return HttpResponse("Archive Failed")

    if (request.method == 'POST'):
        request_status = Status(content_object=request_object,
                                                status=Status.ARCHIVED_STATUS,
                                                datetime=datetime.datetime.now())
        request_status.save()

        return HttpResponse("Archive Successful")
    return HttpResponse("Archive Failed")


@login_required
def archive_custom_request(request, pk):
    current_user = request.user
    if ((not is_company_supervisor_mixin_check(current_user) and not is_company_employee(current_user) ) or not custom_request_is_valid(pk)):
        return redirect_to_dashboard(current_user)

    custom_request = get_object_or_404(CustomRequest, pk=pk)

    status = custom_request.get_request_status()
    if (status is not Status.COMPLETED_STATUS and status is not Status.SUBMITTED_STATUS):
        return HttpResponse("Archive Failed")

    if (request.method == 'POST'):
        request_status = Status(content_object=custom_request, status=Status.ARCHIVED_STATUS, datetime=datetime.datetime.now())
        request_status.save()

        return HttpResponse("Archive Successful")
    return HttpResponse("Archive Failed")

#PDF Generation **************************************
@login_required
def generate_report_view(request, company_date_id):
    current_user = request.user

    cheese = company_date_id.split("_")
    index = len(cheese) - 1
    request_display_id = cheese[index]
    request_object = get_object_or_404(Request, display_id=request_display_id)

    status = request_object.get_request_status()
    if (status is not Status.SUBMITTED_STATUS and is_company_employee(current_user)):
        return HttpResponse("PDF Generation Failed.")
    elif ((status == Status.NEW_STATUS or status == Status.ASSIGNED_STATUS) and not is_company_employee(
            current_user)):
        return HttpResponse("PDF Generation Failed.")
    elif (not is_company_employee(current_user) and not is_analyst(current_user) and not
            is_manager(current_user) and not is_reviewer(current_user)):
            return HttpResponse("PDF Generation Failed.")

    return display_archive_individual_report(request_object, False)


def display_archive_individual_report(request_object, toArchive):
    service_statuses = RequestServiceStatus.objects.filter(request=request_object).order_by(
        'service__service__display_order')

    start_date = "Unknown"
    submit_date = "Unknown"

    try:
        start_date = \
            Status.objects.filter(request=request_object).filter(status=Status.NEW_STATUS).values(
                'datetime').first()['datetime']
        submit_date = \
            Status.objects.filter(request=request_object).filter(status=Status.SUBMITTED_STATUS).values(
                'datetime').first()['datetime']
    except Exception, e:
        print "Error generating dates."

    template = 'reports/core.html'
    template = get_template_type(request_object)
    company = CompanyEmployee.objects.get(user=request_object.created_by.user).company

    report_logo = None
    try:
        report_logo = company.report_logo
    except:
        pass

    report_logo = settings.MEDIA_URL + str(report_logo)
    report_logo_active = company.report_logo_active



    if toArchive:
        return archive_pdf(template, request_object,
                           {'logo': settings.COMPLY_LOGO_FOR_PDF, 'ashtree_logo': settings.ASHTREE_LOGO_FOR_PDF,
                            'voyint_logo': settings.VOYINT_LOGO, 'voyint_last_page': settings.VOYINT_LAST_PAGE,
                            'voyint_bullet': settings.VOYINT_BULLET, 'voyint_line': settings.VOYINT_HORIZONTAL_LINE,
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
    else:
        return generate_pdf(template,
                            {'logo': settings.COMPLY_LOGO_FOR_PDF, 'ashtree_logo': settings.ASHTREE_LOGO_FOR_PDF,
                             'voyint_logo': settings.VOYINT_LOGO, 'voyint_last_page': settings.VOYINT_LAST_PAGE,
                             'voyint_bullet': settings.VOYINT_BULLET, 'voyint_line': settings.VOYINT_HORIZONTAL_LINE,
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


@login_required
def generate_custom_report_view(request, company_date_id):
    current_user = request.user

    cheese = company_date_id.split("_")
    index = len(cheese) - 1
    request_display_id = cheese[index]
    custom_request = get_object_or_404(CustomRequest, display_id=request_display_id)

    status = custom_request.get_request_status()
    if (status is not Status.SUBMITTED_STATUS and is_company_employee(current_user)):
        return HttpResponse("PDF Generation Failed.")
    elif ((status == Status.NEW_STATUS or status == Status.ASSIGNED_STATUS) and not is_company_employee(
            current_user)):
        return HttpResponse("PDF Generation Failed.")
    elif (not is_company_employee(current_user) and not is_analyst(current_user)
          and not is_manager(current_user) and not is_reviewer(current_user)):
        return HttpResponse("PDF Generation Failed.")

    try:
        fields = CustomRequestFields.objects.filter(custom_request=custom_request)
    except CustomRequestFields.DoesNotExist:
        return HttpResponse("PDF Generation Failed.")

    return display_archive_custom_report(custom_request, fields, False)


def display_archive_custom_report(custom_request, fields, toArchive):
    service_statuses = CustomRequestServiceStatus.objects.filter(request=custom_request).order_by(
        'service__service__display_order')

    start_date = "Unknown"
    submit_date = "Unknown"

    try:
        start_date = \
            Status.objects.filter(custom_request=custom_request, status=Status.IN_PROGRESS_STATUS).values('datetime', 'id').order_by('id').first()['datetime']

        submit_date = \
            Status.objects.filter(custom_request=custom_request).filter(status=Status.SUBMITTED_STATUS).values('datetime').first()['datetime']
    except:
        pass

    template = 'reports/comply.html'
    template = get_template_type(custom_request)
    company = CompanyEmployee.objects.get(user=custom_request.created_by.user).company

    report_logo = None
    try:
        report_logo = company.report_logo
    except:
        pass

    report_logo = settings.MEDIA_URL + str(report_logo)
    report_logo_active = company.report_logo_active

    if toArchive:
        return archive_pdf(template, custom_request,
                           {'logo': settings.COMPLY_LOGO_FOR_PDF, 'ashtree_logo': settings.ASHTREE_LOGO_FOR_PDF,
                            'voyint_logo': settings.VOYINT_LOGO, 'voyint_last_page': settings.VOYINT_LAST_PAGE,
                            'voyint_bullet': settings.VOYINT_BULLET, 'voyint_line': settings.VOYINT_HORIZONTAL_LINE,
                            'report_logo_active': report_logo_active, 'report_logo': report_logo,
                            'watermark_ashtree': settings.WATERMARK_ASHTREE, 'line': settings.HORIZONTAL_LINE,
                            'green_line': settings.HORIZONTAL_LINE_ASHTREE,
                            'last_page': settings.LAST_PAGE, 'last_page_ashtree': settings.LAST_PAGE_ASHTREE,
                            'last_page_client': settings.LAST_PAGE_CLIENT,
                            'flag': settings.FLAG, 'yellow_flag':settings.YELLOW_FLAG,
                            'request': custom_request, "start_date": start_date, "submit_date": submit_date,
                            "service_statuses": service_statuses, "font_url": settings.FONT_DIR,
                            "bullet": settings.BULLET, "bullet_ashtree": settings.BULLET_ASHTREE, 'x': settings.X,
                            'prescient': settings.PRESCIENT, 'no_red_flag': settings.NO_RED_FLAG, 'fields':fields})
    else:
        return generate_pdf(template,
                            {'logo': settings.COMPLY_LOGO_FOR_PDF, 'ashtree_logo': settings.ASHTREE_LOGO_FOR_PDF,
                             'voyint_logo': settings.VOYINT_LOGO, 'voyint_last_page': settings.VOYINT_LAST_PAGE,
                             'voyint_bullet': settings.VOYINT_BULLET, 'voyint_line': settings.VOYINT_HORIZONTAL_LINE,
                             'report_logo_active': report_logo_active, 'report_logo': report_logo,
                             'watermark_ashtree': settings.WATERMARK_ASHTREE, 'line': settings.HORIZONTAL_LINE,
                             'green_line': settings.HORIZONTAL_LINE_ASHTREE,
                             'last_page': settings.LAST_PAGE, 'last_page_ashtree': settings.LAST_PAGE_ASHTREE,
                             'last_page_client': settings.LAST_PAGE_CLIENT,
                             'flag': settings.FLAG, 'yellow_flag':settings.YELLOW_FLAG,
                             'request': custom_request, "start_date": start_date, "submit_date": submit_date,
                             "service_statuses": service_statuses, "font_url": settings.FONT_DIR,
                             "bullet": settings.BULLET, "bullet_ashtree": settings.BULLET_ASHTREE, 'x': settings.X,
                             'prescient': settings.PRESCIENT, 'no_red_flag': settings.NO_RED_FLAG, 'fields':fields})


@login_required
def generate_corporate_report_view(request, company_date_id):
    current_user = request.user

    split = company_date_id.split("_")
    index = len(split) - 1
    request_display_id = split[index]
    request_object = get_object_or_404(CorporateRequest, display_id=request_display_id)

    status = request_object.get_request_status()
    if (status is not Status.SUBMITTED_STATUS and is_company_employee(current_user)):
        return HttpResponse("PDF Generation Failed.")
    elif ((status == Status.NEW_STATUS or status == Status.ASSIGNED_STATUS)
          and not is_company_employee(current_user)):
        return HttpResponse("PDF Generation Failed.")
    elif (not is_company_employee(current_user) and not is_analyst(current_user) and not is_manager(current_user) and not is_reviewer(current_user)):
        return HttpResponse("PDF Generation Failed.")

    return display_archive_corporate_report(request_object, False)


def display_archive_corporate_report(request_object, toArchive):
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

    if toArchive:
        return archive_pdf(template, request_object,
                           {'logo': settings.COMPLY_LOGO_FOR_PDF, 'ashtree_logo': settings.ASHTREE_LOGO_FOR_PDF,
                            'voyint_logo': settings.VOYINT_LOGO, 'voyint_last_page': settings.VOYINT_LAST_PAGE,
                            'voyint_bullet': settings.VOYINT_BULLET, 'voyint_line': settings.VOYINT_HORIZONTAL_LINE,
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
    else:
        return generate_pdf(template,
                            {'logo': settings.COMPLY_LOGO_FOR_PDF, 'ashtree_logo': settings.ASHTREE_LOGO_FOR_PDF,
                             'voyint_logo': settings.VOYINT_LOGO, 'voyint_last_page': settings.VOYINT_LAST_PAGE,
                             'voyint_bullet': settings.VOYINT_BULLET, 'voyint_line': settings.VOYINT_HORIZONTAL_LINE,
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

# Request CSV Export View

class ManagerRequestExport(ManagerOnlyMixin,generic.View):

    def apply_filters_on_export_requests(self,filters,statuses):
        # ID
        id_search = filters["requestId"]
        if (len(id_search) > 0):
            cust_id_filt = statuses.filter(custom_request__display_id__icontains=id_search)
            corp_id_filt = statuses.filter(corporate_request__display_id__icontains=id_search)
            ind_id_filt = statuses.filter(request__display_id__icontains=id_search)
            statuses = cust_id_filt | corp_id_filt | ind_id_filt
        
        # company
        company_search = filters["companyId"]
        if (len(company_search) > 0):
            cust_company_name = statuses.filter(custom_request__created_by__company=company_search)
            corp_company_name = statuses.filter(corporate_request__created_by__company=company_search)
            ind_company_name = statuses.filter(request__created_by__company=company_search)
            statuses = cust_company_name | corp_company_name | ind_company_name


        # Assigned To
        assigned_to_id = filters["assignmentId"]
        if (len(assigned_to_id) > 0):
            cust_ids = statuses.filter(custom_request__assignment=assigned_to_id).values_list('id', flat=True)
            corp_ids = statuses.filter(corporate_request__assignment=assigned_to_id).values_list('id', flat=True)
            ind_ids = statuses.filter(request__assignment=assigned_to_id).values_list('id', flat=True)
            comb_ids = list(chain(cust_ids, corp_ids, ind_ids))
            statuses = statuses.filter(id__in=comb_ids)


        
        name_search = filters["name"]


        if len(name_search) > 0:
            cust_names = statuses.filter(custom_request__name__icontains=name_search)
            corp_names = statuses.filter(corporate_request__company_name__icontains=name_search)
            ind_first = statuses.filter(request__first_name__icontains=name_search)
            ind_last = statuses.filter(request__last_name__icontains=name_search)
            statuses = cust_names | corp_names | ind_first | ind_last



        # STATUS
        status_search = filters["statusType"]
        if (status_search != "null" and len(status_search) > 0):
            statuses = statuses.filter(status__in=status_search)


        
        # TYPE
        type_search = filters["type"]
        if (len(type_search) > 0):
            dd_type_selection = CompanyDueDiligenceTypeSelection.objects.get(id=type_search)
            if (dd_type_selection.name == ""):
                level = dd_type_selection.level
                dd_type = dd_type_selection.due_diligence_type
                cust_dd_ids = statuses.filter(custom_request__request_type__level=level).filter(
                    custom_request__request_type__due_diligence_type=dd_type).values_list('id', flat=True)

                corp_dd_ids = statuses.filter(corporate_request__request_type__level=level).filter(
                    corporate_request__request_type__due_diligence_type=dd_type).values_list('id', flat=True)

                ind_dd_ids = statuses.filter(request__request_type__level=level).filter(
                    request__request_type__due_diligence_type=dd_type).values_list('id', flat=True)

                comb_dd_ids = list(chain(cust_dd_ids, corp_dd_ids, ind_dd_ids))

                statuses = statuses.filter(id__in=comb_dd_ids)

            else:
                cust_dd_ids = statuses.filter(
                    custom_request__request_type__id=type_search).values_list('id', flat=True)

                corp_dd_ids = statuses.filter(
                    corporate_request__request_type__id=type_search).values_list('id', flat=True)

                ind_dd_ids = statuses.filter(
                    request__request_type__id=type_search).values_list('id', flat=True)

                comp_dd_ids = list(chain(cust_dd_ids, corp_dd_ids, ind_dd_ids))

                statuses = statuses.filter(id__in=comp_dd_ids)

        # START DATE
        start_end_date = filters["startEndDate"]
        if (len(start_end_date) > 3):
            array = start_end_date.split('+')
            start = fix_start(array[0])
            end = fix_end(array[1])
            statuses = statuses.filter(datetime__range=[start, end])


        # CUSTOM FIELD
        custom_field = filters["customFieldId"]
        if (len(custom_field) > 0):
            field_ids = list(
                CustomRequestFields.objects.filter(custom_request__dynamic_request_form__render_form=True,
                                                    form_field__id=custom_field).exclude(
                    value__isnull=True).exclude(value__exact='').values_list('custom_request__id', flat=True))

            statuses = statuses.filter(custom_request__id__in=field_ids)


        # CUSTOM FIELD VALUE
        custom_field_value = filters["customFieldValue"]
        if (len(custom_field_value) > 0):
            field_ids = list(
                CustomRequestFields.objects.filter(custom_request__dynamic_request_form__render_form=True,
                                                    value__icontains=custom_field_value).values_list(
                                                    'custom_request__id', flat=True))
            statuses = statuses.filter(custom_request__id__in=field_ids)

        # FORM NAME
        dynamic_request_form_id = filters["customFormTypeId"]
        if (len(dynamic_request_form_id) > 0):
            statuses = statuses.filter(custom_request__dynamic_request_form__id=dynamic_request_form_id)


        # REQUEST TYPE
        request_type = filters["requestType"]
        if len(request_type) > 0:
            statuses = statuses.filter(content_type__model=request_type)
        
        return statuses

    def get_populated_request_dict(self,statuses):
        populated_statuses = []
        request_detail_choices_dict = dict(BaseRequestDetailStatus.REQUEST_DETAIL_STATUS_CHOICES)
        for status in statuses:
            populated = {}
            main_request = None
            if status["content_type__model"] == "request":
                request = Request.objects.get(pk=status["object_id"])
                main_request= request
                populated["Display ID"] = request.display_id
                populated["Name"] = request.first_name + request.last_name
                populated["Company Name"] = request.created_by.company.name
                populated["Request Type"] = request.request_type.__unicode__()
                populated["Assignment"] = request.assignment.user.username if request.assignment is not None else ""
                populated["Reviewer"] = request.reviewer.user.username if request.reviewer is not None else ""
                if request.request_type.price:
                    price = request.request_type.price
                else:
                    price = 0
                populated["Request Price"] = price
                surcharges = Surcharge.objects.filter(request_type="Request", request_id=request.display_id)
                total_surcharges = 0
                surcharge_list = []
                for s in surcharges:
                    surcharge_title = "Reference no. {} - Charge Type: {} - Source: {} - Order no. {} - Processing Fee {} - Estimated Cost {}".format(s.ref_number.encode("utf-8"),s.charge_type.name,s.source,s.order_number.encode("utf-8"),s.processing_fee,s.estimated_cost)
                    surcharge_list.append(surcharge_title)
                    total_surcharges = total_surcharges + s.estimated_cost
                
                populated["Surcharges"] = " | ".join(surcharge_list)
                populated["Surcharge Total"] = total_surcharges

                request_detail_statuses_data = RequestDetailStatus.objects.order_by("status").filter(request=request).values("status","reason")

                request_detail_statuses = [ request_detail_choices_dict[x["status"]] for x in request_detail_statuses_data]
                if len(request_detail_statuses) != 0 and request_detail_statuses[-1] == "Other":
                    request_detail_other_text = [ x["reason"] for x in request_detail_statuses_data if x["status"] == RequestDetailStatus.OTHER]
                    request_detail_other_text = request_detail_other_text[0] if(len(request_detail_other_text) > 0 and request_detail_other_text[0] is not None) else ""
                    request_detail_statuses[-1] +=  "({})".format(request_detail_other_text)
                populated["Analyst Status"] = "\n".join(request_detail_statuses)

            elif status["content_type__model"] == "corporaterequest":
                corporate_request = CorporateRequest.objects.get(pk=status["object_id"])
                main_request = corporate_request
                populated["Display ID"] = corporate_request.display_id
                populated["Name"] = corporate_request.company_name
                populated["Company Name"] = corporate_request.created_by.company.name
                populated["Request Type"] = corporate_request.request_type.__unicode__()
                populated["Assignment"] = corporate_request.assignment.user.username if corporate_request.assignment is not None else ""
                populated["Reviewer"] = corporate_request.reviewer.user.username if corporate_request.reviewer is not None else ""
                if corporate_request.request_type.price:
                    price = corporate_request.request_type.price
                else:
                    price = 0
                populated["Request Price"] = price
                surcharges = Surcharge.objects.filter(request_type="CorporateRequest", request_id=corporate_request.display_id)
                total_surcharges = 0
                surcharge_list = []
                for s in surcharges:
                    surcharge_title = "Reference # {} - Charge Type: {} - Source: {} - Order # {} - Processing Fee $ {} - Estimated Cost $ {}".format(s.ref_number,s.charge_type.name,s.source,s.order_number,s.processing_fee,s.estimated_cost)
                    surcharge_list.append(surcharge_title)
                    total_surcharges = total_surcharges + s.estimated_cost
                
                populated["Surcharges"] = " | ".join(surcharge_list)
                populated["Surcharge Total"] = total_surcharges

                request_detail_statuses_data = CorporateRequestDetailStatus.objects.order_by("status").filter(request=corporate_request).values("status","reason")

                request_detail_statuses = [ request_detail_choices_dict[x["status"]] for x in request_detail_statuses_data]
                if len(request_detail_statuses) != 0 and request_detail_statuses[-1] == "Other":
                    request_detail_other_text = [ x["reason"] for x in request_detail_statuses_data if x["status"] == RequestDetailStatus.OTHER]
                    request_detail_other_text = request_detail_other_text[0] if(len(request_detail_other_text) > 0 and request_detail_other_text[0] is not None) else ""
                    request_detail_statuses[-1] +=  "({})".format(request_detail_other_text)
                populated["Analyst Status"] = "\n".join(request_detail_statuses)

            elif status["content_type__model"] == "customrequest":
                custom_request = CustomRequest.objects.get(pk=status["object_id"])
                main_request = custom_request
                populated["Display ID"] = custom_request.display_id
                populated["Name"] = custom_request.name
                populated["Company Name"] = custom_request.created_by.company.name
                populated["Request Type"] = custom_request.request_type.__unicode__()
                populated["Assignment"] = custom_request.assignment.user.username if custom_request.assignment is not None else ""
                populated["Reviewer"] = custom_request.reviewer.user.username if custom_request.reviewer is not None else ""
                if custom_request.request_type.price:
                    price = custom_request.request_type.price
                else:
                    price = 0
                populated["Request Price"] = price
                surcharges = Surcharge.objects.filter(request_type="CustomRequest", request_id=custom_request.display_id)
                total_surcharges = 0
                surcharge_list = []
                for s in surcharges:
                    surcharge_title = "Reference # {} - Charge Type: {} - Source: {} - Order # {} - Processing Fee {} - Estimated Cost {}".format(s.ref_number,s.charge_type.name,s.source,s.order_number,s.processing_fee,s.estimated_cost)
                    surcharge_list.append(surcharge_title)
                    total_surcharges = total_surcharges + s.estimated_cost
                
                populated["Surcharges"] = " | ".join(surcharge_list)
                populated["Surcharge Total"] = total_surcharges

                request_detail_statuses_data = CustomRequestDetailStatus.objects.order_by("status").filter(request=custom_request).values("status","reason")

                request_detail_statuses = [ request_detail_choices_dict[x["status"]] for x in request_detail_statuses_data]
                if len(request_detail_statuses) != 0 and request_detail_statuses[-1] == "Other":
                    request_detail_other_text = [ x["reason"] for x in request_detail_statuses_data if x["status"] == RequestDetailStatus.OTHER]
                    request_detail_other_text = request_detail_other_text[0] if(len(request_detail_other_text) > 0 and request_detail_other_text[0] is not None) else ""
                    request_detail_statuses[-1] +=  "({})".format(request_detail_other_text)
                populated["Analyst Status"] = "\n".join(request_detail_statuses)

        
            if status['status'] == 1 or status['status'] == 2:
                populated['Status'] = 'New'
            elif status['status'] == 3:
                populated['Status'] = 'In Progress'
                populated['Start Date'] = formats.date_format(main_request.get_in_progress_request_status().datetime.astimezone(timezone('US/Eastern')), "SHORT_DATETIME_FORMAT")
            elif status['status'] == 4:
                populated['Status'] = 'Completed'
                populated['Start Date'] = formats.date_format(main_request.get_in_progress_request_status().datetime.astimezone(timezone('US/Eastern')), "SHORT_DATETIME_FORMAT")
            elif status['status'] == 5:
                populated['Status'] = 'Submitted'
                populated['Start Date'] = formats.date_format(main_request.get_in_progress_request_status().datetime.astimezone(timezone('US/Eastern')), "SHORT_DATETIME_FORMAT")
            elif status['status'] == 6:
                try:
                    populated['Status'] = 'In Progress'
                    populated['Start Date'] = formats.date_format(main_request.get_in_progress_request_status().datetime.astimezone(timezone('US/Eastern')), "SHORT_DATETIME_FORMAT")
                except:
                    populated['Status'] = 'New'

            else:
                populated['Status'] = Status.SUPERVISOR_STATUS_CHOICES.get(status['status'])

            
            populated_statuses.append(populated)

        return populated_statuses


    def post(self,request):
        current_user = request.user
        data = json.loads(request.body)
        ids = list(Status.get_all_current_ids_queryset())
        statuses = Status.objects.filter(id__in=ids).values("content_type__model","object_id","status")
        # for i in statuses:
        statuses = self.apply_filters_on_export_requests(data,statuses)
        statuses = self.get_populated_request_dict(statuses)

        fieldnames = ["Display ID","Name","Status","Analyst Status","Company Name","Start Date","Request Type",\
            "Assignment","Reviewer","Surcharges","Surcharge Total","Request Price"]
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="request_advanced_search.csv"'

        writer = csv.DictWriter(response, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(statuses)
        return response



# Archived Reports View
@login_required
def archived_reports(request):
    current_user = request.user
    if (is_manager(current_user)):
        reports = Reports.objects.all()
        companies = Company.objects.all()
        return render(request, "core/reports_dashboard.html", {"reports": reports, "companies": companies})
    else:
        return redirect_to_dashboard(current_user)


@login_required
def generate_archived_report_view(request, archived_report_id, report_name):
    report = get_object_or_404(Reports, id=archived_report_id)
    return generate_archived_pdf(report.data)


# Archived Reports Eztable
# Used for Manager's All Reports to display all archived reports and filter by different categories


# There are three ajax calls because only the ID is being passed in.
# The object has to be defined in the code not inferred from the program
def ajax_change_created_by_employee(request):
    response = {}
    if request.is_ajax() and request.method == 'POST':
        employee_id = request.POST['employee']
        request_id = request.POST['requestID']
        employee = CompanyEmployee.objects.get(pk=employee_id)
        request = Request.objects.get(pk=request_id)
        request.created_by = employee
        request.save()
        send_created_by_change_email(request, employee.user)
        employee_name = employee.user.first_name + " " + employee.user.last_name
        response['name'] = employee_name
        return HttpResponse(json.dumps(response))

    else:
        return HttpResponse('Bad Request')

def ajax_change_created_by_employee_corporate(request):
    response = {}
    if request.is_ajax() and request.method == 'POST':
        employee_id = request.POST['employee']
        request_id = request.POST['requestID']
        employee = CompanyEmployee.objects.get(pk=employee_id)
        corporate_request = CorporateRequest.objects.get(pk=request_id)
        corporate_request.created_by = employee
        corporate_request.save()
        send_created_by_change_email(corporate_request, employee.user)
        employee_name = employee.user.first_name + " " + employee.user.last_name
        response['name'] = employee_name
        return HttpResponse(json.dumps(response))

    else:
        return HttpResponse('Bad Request')


def ajax_change_created_by_employee_custom(request):
    response = {}
    if request.is_ajax() and request.method == 'POST':
        employee_id = request.POST['employee']
        request_id = request.POST['requestID']
        employee = CompanyEmployee.objects.get(pk=employee_id)
        custom_request = CustomRequest.objects.get(pk=request_id)
        custom_request.created_by = employee
        custom_request.save()
        send_created_by_change_email(custom_request, employee.user)
        employee_name = employee.user.first_name + " " + employee.user.last_name
        response['name'] = employee_name
        return HttpResponse(json.dumps(response))

    else:
        return HttpResponse('Bad Request')


# There are three ajax calls because only the ID is being passed in.
# The object has to be defined in the code not inferred from the program
def ajax_change_analyst(request):
    if request.is_ajax() and request.method == 'POST':
        analyst_id = request.POST['analyst']
        request_id = request.POST['requestID']
        analyst = SpotLitStaff.objects.get(pk=analyst_id)
        individual_request = Request.objects.get(pk=request_id)
        if 'notes' in request.POST:
            notes = request.POST['notes']
        else:
            notes = individual_request.reassigned_analyst_notes
        individual_request.assignment = analyst
        individual_request.reassigned_analyst_notes = notes
        if 'due_date' in request.POST:
            individual_request.due_date = request.POST['due_date']
        individual_request.save()
        request_status = Status(content_object=individual_request,
                                   status=Status.ASSIGNED_STATUS,
                                   datetime=datetime.datetime.now(),
                                   comments=notes)
        request_status.save()
        send_analyst_change_email(individual_request, analyst.user)
        return HttpResponse('The request has been reassigned to' + str(analyst))

    else:
        return HttpResponseServerError("Change Analyst Failed")

def ajax_change_analyst_corporate(request):
    if request.is_ajax() and request.method == 'POST':
        analyst_id = request.POST['analyst']
        request_id = request.POST['requestID']
        analyst = SpotLitStaff.objects.get(pk=analyst_id)
        corporate_request = CorporateRequest.objects.get(pk=request_id)
        if 'notes' in request.POST:
            notes = request.POST['notes']
        else:
            notes = corporate_request.reassigned_analyst_notes
        corporate_request.assignment = analyst
        corporate_request.reassigned_analyst_notes = notes
        if 'due_date' in request.POST:
            corporate_request.due_date = request.POST['due_date']
        corporate_request.save()
        request_status = Status(content_object=corporate_request,
                                   status=Status.ASSIGNED_STATUS,
                                   datetime=datetime.datetime.now(),
                                   comments=notes)
        request_status.save()
        send_analyst_change_email(corporate_request, analyst.user)
        return HttpResponse('The request has been reassigned to' + str(analyst))

    else:
        return HttpResponseServerError("Change Analyst For Corporate Failed")


def ajax_change_analyst_custom(request):
    if request.is_ajax() and request.method == 'POST':
        analyst_id = request.POST['analyst']
        request_id = request.POST['requestID']
        analyst = SpotLitStaff.objects.get(pk=analyst_id)
        custom_request = CustomRequest.objects.get(pk=request_id)
        if 'notes' in request.POST:
            notes = request.POST['notes']
        else:
            notes = custom_request.reassigned_analyst_notes
        custom_request.assignment = analyst
        custom_request.reassigned_analyst_notes = notes
        if 'due_date' in request.POST:
            custom_request.due_date = request.POST['due_date']
        custom_request.save()
        request_status = Status(content_object=custom_request,
                                   status=Status.ASSIGNED_STATUS,
                                   datetime=datetime.datetime.now(),
                                   comments=notes)
        request_status.save()
        send_analyst_change_email(custom_request, analyst.user)
        return HttpResponse('The request has been reassigned to' + str(analyst))

    else:
        return HttpResponseServerError("Change Analyst for custom Failed")

# AJAX call to change reviewer for a individual request
@csrf_protect
def ajax_change_reviewer(request):
    if request.is_ajax() and request.method == 'POST':
        reviewer_id = request.POST['reviewer']
        request_id = request.POST['requestID']
        notes = request.POST['notes']
        reviewer = SpotLitStaff.objects.get(pk=reviewer_id)
        request = Request.objects.get(pk=request_id)
        request.reviewer = reviewer
        request.reassigned_reviewer_notes = notes
        request.save()
        request_status = Status(content_object=request,
                                   status=Status.ASSIGNED_STATUS,
                                   datetime=datetime.datetime.now(),
                                   comments=notes)
        request_status.save()
        return HttpResponse('The request has been reassigned')
    else:
        return HttpResponseServerError("Change Reviewer Failed")

# AJAX call to change reviewer for a custom request
@csrf_protect
def ajax_change_reviewer_custom(request):
    if request.is_ajax() and request.method == 'POST':
        reviewer_id = request.POST['reviewer']
        request_id = request.POST['requestID']
        notes = request.POST['notes']
        reviewer = SpotLitStaff.objects.get(pk=reviewer_id)
        request = CustomRequest.objects.get(pk=request_id)
        request.reviewer = reviewer
        request.reassigned_reviewer_notes = notes
        request.save()
        request_status = Status(content_object=request,
                                   status=Status.ASSIGNED_STATUS,
                                   datetime=datetime.datetime.now(),
                                   comments=notes)
        request_status.save()
        return HttpResponse("The request has been reassigned")
    else:
        return HttpResponseServerError("Change Reviewer For Custom Failed")


# AJAX call to change reviewer for a corprorate request
@csrf_protect
def ajax_change_reviewer_corporate(request):
    if request.is_ajax() and request.method == 'POST':
        reviewer_id = request.POST['reviewer']
        request_id = request.POST['requestID']
        notes = request.POST['notes']
        reviewer = SpotLitStaff.objects.get(pk=reviewer_id)
        request = CorporateRequest.objects.get(pk=request_id)
        request.reviewer = reviewer
        request.reassigned_reviewer_notes = notes
        request.save()
        request_status = Status(content_object=request,
                                   status=Status.ASSIGNED_STATUS,
                                   datetime=datetime.datetime.now(),
                                   comments=notes)
        request_status.save()
        return HttpResponse('The request has been reassigned')
    else:
        return HttpResponseServerError("Change Reviewer For Corporate Failed")


# Recall
def recall_request(request, pk):
    request = Request.objects.get(pk=pk)
    request_status = Status(content_object=request,
                                   status=Status.COMPLETED_STATUS,
                                   datetime=datetime.datetime.now())
    request_status.save()

    return HttpResponseRedirect(reverse_lazy('request_manager', kwargs={'pk': pk}))


def recall_corporate_request(request, pk):
    request = CorporateRequest.objects.get(pk=pk)
    request_status = Status(content_object=request,
                                            status=Status.COMPLETED_STATUS,
                                            datetime=datetime.datetime.now())
    request_status.save()


    return HttpResponseRedirect(reverse_lazy('corporate_request_manager', kwargs={'pk': pk}))


def recall_custom_request(request, pk):
    request = CustomRequest.objects.get(pk=pk)
    request_status = Status(content_object=request,
                                         status=Status.COMPLETED_STATUS,
                                         datetime=datetime.datetime.now())

    request_status.save()

    return HttpResponseRedirect(reverse_lazy('custom_request_manager', kwargs={'pk': pk}))


# Recall & Reassign

def recall_reassign_request(request, pk, analyst_id):
    request = Request.objects.get(pk=pk)
    request_status = Status(content_object=request,
                                   status=Status.ASSIGNED_STATUS,
                                   datetime=datetime.datetime.now())
    request_status.save()

    analyst = SpotLitStaff.objects.get(pk=analyst_id)
    request = Request.objects.get(pk=request.id)
    request.assignment = analyst
    request.save()

    send_status_change_email(request, analyst.user, Status.ASSIGNED_STATUS)
    send_analyst_change_email(request, analyst.user)

    return HttpResponseRedirect(reverse_lazy('request_manager', kwargs={'pk': pk}))


def recall_reassign_corporate_request(request, pk, analyst_id):
    request = CorporateRequest.objects.get(pk=pk)
    request_status = Status(content_object=request,
                                            status=Status.ASSIGNED_STATUS,
                                            datetime=datetime.datetime.now())
    request_status.save()

    analyst = SpotLitStaff.objects.get(pk=analyst_id)
    request = CorporateRequest.objects.get(pk=request.id)
    request.assignment = analyst
    request.save()


    send_status_change_email_for_corporate(request, analyst.user, Status.ASSIGNED_STATUS)
    send_analyst_change_email(request, analyst.user)

    return HttpResponseRedirect(reverse_lazy('corporate_request_manager', kwargs={'pk': pk}))


def recall_reassign_custom_request(request, pk, analyst_id):
    request = CustomRequest.objects.get(pk=pk)
    request_status = Status(content_object=request,
                                         status=Status.ASSIGNED_STATUS,
                                         datetime=datetime.datetime.now())
    request_status.save()

    analyst = SpotLitStaff.objects.get(pk=analyst_id)
    request = CustomRequest.objects.get(pk=request.id)
    request.assignment = analyst
    request.save()

    send_status_change_email_for_custom(request, analyst.user, Status.ASSIGNED_STATUS)
    send_analyst_change_email(request, analyst.user)

    return HttpResponseRedirect(reverse_lazy('custom_request_manager', kwargs={'pk': pk}))


def batch_upload(request, dynamic_request_pk):
    # Handle document upload
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        request_type_pk = request.POST['batch_custom_form_type']
        request_type = CompanyDueDiligenceTypeSelection.objects.get(pk=request_type_pk)
        if form.is_valid():
            user = request.user
            created_by = get_company_employee(request.user)
            newdoc = BatchFile(docfile=request.FILES['docfile'], created_by=created_by)
            newdoc.save()
            batch_thread = BatchUploadThread(newdoc, dynamic_request_pk, request_type_pk, created_by, user)
            batch_thread.start()
        else:
            print "batch_upload: Invalid form..."
    # Render list page with the documents and the form
    return HttpResponseRedirect(reverse_lazy('supervisor_dashboard'))




####################################
#
# EXPORT CSV
#
####################################


# CUSTOM REQUESTS
@login_required
def get_all_custom_request_statuses_for_supervisor_csv(request):
    if not(is_company_supervisor_mixin_check(request.user)):
        return redirect_to_dashboard(request.user)
    report_generator = CsvReportGenerator(request)
    report_generator.start()
    return HttpResponseRedirect(reverse_lazy('supervisor_dashboard'))

@login_required
def get_all_custom_request_statuses_for_supervisor_excel(request):
    if not(is_company_supervisor_mixin_check(request.user)):
        return redirect_to_dashboard(request.user)
    report_generator = ExcelReportGenerator(request)
    report_generator.start()
    return HttpResponseRedirect(reverse_lazy('supervisor_dashboard'))


# INDIVIDUAL REQUESTS
@login_required
def get_all_individual_request_statuses_for_supervisor_csv(request):
    if not(is_company_supervisor_mixin_check(request.user)):
        return redirect_to_dashboard(request.user)

    current_user = request.user
    supervisor = get_company_employee(current_user)
    company = supervisor.company
    ids = list(Status.get_all_current_ids_queryset())
    statuses = Status.objects.filter(id__in=ids, request__created_by__company=company).values(
        'request__id', 'request__display_id', 'request__first_name', 'request__middle_name', 'request__last_name'
        , 'request__citizenship', 'request__ssn', 'request__birthdate', 'request__phone_number', 'request__email'
        , 'request__request_type__name', 'request__created_by__user__last_name', 'request__address__street',
        'request__address__street2', 'request__address__city', 'request__address__state', 'request__address__zipcode'
        , 'status'
    ).order_by('status')

    fieldnames = ['request__id', 'request__display_id', 'request__first_name', 'request__middle_name', 'request__last_name'
        , 'request__citizenship', 'request__ssn', 'request__birthdate', 'request__phone_number', 'request__email'
        , 'request__request_type__name', 'request__created_by__user__last_name','request__address__street',
        'request__address__street2', 'request__address__city', 'request__address__state', 'request__address__zipcode'
        , 'status', 'Start Date', 'Completed Date']

    for status in statuses:
        id = status['request__id']
        request = Request.objects.get(pk=id)
        status['request__ssn'] = request.ssn


        if status['status'] == 1 or status['status'] == 2:
            status['status'] = 'New'
        elif status['status'] == 3:
            status['status'] = 'In Progress'
            status['Start Date'] = formats.date_format(request.get_in_progress_request_status().datetime.astimezone(timezone('US/Eastern')), "SHORT_DATETIME_FORMAT")
        elif status['status'] == 4:
            status['status'] = 'Completed'
            status['Start Date'] = formats.date_format(request.get_in_progress_request_status().datetime.astimezone(timezone('US/Eastern')), "SHORT_DATETIME_FORMAT")
        elif status['status'] == 5:
            status['status'] = 'Submitted'
            status['Start Date'] = formats.date_format(request.get_in_progress_request_status().datetime.astimezone(timezone('US/Eastern')), "SHORT_DATETIME_FORMAT")
            status['Completed Date'] = formats.date_format(request.get_complete_request_status().datetime.astimezone(timezone('US/Eastern')), "SHORT_DATETIME_FORMAT")
        elif status['status'] == 6:
            try:
                status['status'] = 'In Progress'
                status['Start Date'] = formats.date_format(request.get_in_progress_request_status().datetime.astimezone(timezone('US/Eastern')), "SHORT_DATETIME_FORMAT")
            except:
                status['status'] = 'New'

        else:
            status['status'] = Status.SUPERVISOR_STATUS_CHOICES.get(status['status'])

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="individual_request_status_report.csv"'

    writer = csv.DictWriter(response, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(statuses)

    return response

@login_required
def get_all_individual_request_statuses_for_supervisor_excel(request):
    if not(is_company_supervisor_mixin_check(request.user)):
        return redirect_to_dashboard(request.user)

    current_user = request.user
    supervisor = get_company_employee(current_user)
    company = supervisor.company
    ids = list(Status.get_all_current_ids_queryset())

    fields = ['request__display_id', 'request__first_name', 'request__middle_name', 'request__last_name'
        , 'request__citizenship', 'request__ssn', 'request__birthdate', 'request__phone_number', 'request__email'
        , 'request__request_type__name', 'request__created_by__user__first_name', 'request__created_by__user__last_name'
        , 'request__address__street', 'request__address__street2', 'request__address__city', 'request__address__state',
              'request__address__zipcode', 'status']

    statuses = Status.objects.filter(id__in=ids, request__created_by__company=company).values(*fields)
    headers = ['Display ID', 'First Name', 'Middle Name', 'Last Name', 'Citizenship', 'SSN', 'Birthday', 'Phone Number',
               'Email', 'Request Type', 'Created By First Name', 'Created By Last Name', 'Street Address', 'Street Address 2', 'City', 'State',
               'Zip Code', 'Status']

    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="IndividualRequests.xls"'
    workbook = xlwt.Workbook(encoding='ascii')
    worksheet = workbook.add_sheet('My Worksheet')
    row_index = 0
    col_index = 0
    for header in headers:
        worksheet.write(row_index, col_index, header)
        col_index += 1
    row_index = 1
    col_index = 0
    for row in statuses:
        if row['status'] == 1 or row['status'] == 2:
            row['status'] = 'New'
        elif row['status'] == 3:
            row['status'] = 'In Progress'
        elif row['status'] == 4:
            row['status'] = 'Completed'
        elif row['status'] == 5:
            row['status'] = 'Submitted'
        elif row['status'] == 6:
            row['status'] = 'In Progress'
        else:
            row['status'] = Status.SUPERVISOR_STATUS_CHOICES.get(row['status'])
        for col in row:
            worksheet.write(row_index, col_index, row[fields[col_index]])
            col_index += 1
        col_index = 0
        row_index += 1
    workbook.save(response)
    return response


# CORPORATE REQUESTS
@login_required
def get_all_corporate_request_statuses_for_supervisor_csv(request):
    if not(is_company_supervisor_mixin_check(request.user)):
        return redirect_to_dashboard(request.user)

    current_user = request.user
    supervisor = get_company_employee(current_user)
    company = supervisor.company
    ids = list(Status.get_all_current_ids_queryset())
    statuses = Status.objects.filter(id__in=ids, corporate_request__created_by__company=company).values(
        'corporate_request__id', 'corporate_request__display_id', 'corporate_request__company_name',
        'corporate_request__duns', 'corporate_request__registration',
        'corporate_request__website', 'corporate_request__name_variant', 'corporate_request__parent_company_name',
        'corporate_request__recipient', 'corporate_request__street', 'corporate_request__dependent_locality',
        'corporate_request__locality', 'corporate_request__postalcode', 'corporate_request__country',
        'corporate_request__phone_number', 'corporate_request__email', 'corporate_request__created_by__user__last_name',
        'status'
    )

    fieldnames = ['corporate_request__id', 'corporate_request__display_id', 'corporate_request__company_name',
        'corporate_request__duns', 'corporate_request__registration',
        'corporate_request__website', 'corporate_request__name_variant', 'corporate_request__parent_company_name',
        'corporate_request__recipient', 'corporate_request__street', 'corporate_request__dependent_locality',
        'corporate_request__locality', 'corporate_request__postalcode', 'corporate_request__country',
        'corporate_request__phone_number', 'corporate_request__email', 'corporate_request__created_by__user__last_name',
        'status', 'Start Date', 'Completed Date']



    for status in statuses:
        id = status['corporate_request__id']
        corporate_request = CorporateRequest.objects.get(pk=id)

        if status['status'] == 1 or status['status'] == 2:
            status['status'] = 'New'
        elif status['status'] == 3:
            status['status'] = 'In Progress'
            status['Start Date'] = formats.date_format(corporate_request.get_in_progress_request_status().datetime.astimezone(timezone('US/Eastern')), "SHORT_DATETIME_FORMAT")
        elif status['status'] == 4:
            status['status'] = 'Completed'
            status['Start Date'] = formats.date_format(corporate_request.get_in_progress_request_status().datetime.astimezone(timezone('US/Eastern')), "SHORT_DATETIME_FORMAT")
        elif status['status'] == 5:
            status['status'] = 'Submitted'
            status['Start Date'] = formats.date_format(corporate_request.get_in_progress_request_status().datetime.astimezone(timezone('US/Eastern')), "SHORT_DATETIME_FORMAT")
            status['Completed Date'] = formats.date_format(corporate_request.get_complete_request_status().datetime.astimezone(timezone('US/Eastern')), "SHORT_DATETIME_FORMAT")
        elif status['status'] == 6:
            try:
                status['status'] = 'In Progress'
                status['Start Date'] = formats.date_format(corporate_request.get_in_progress_request_status().datetime.astimezone(timezone('US/Eastern')), "SHORT_DATETIME_FORMAT")
            except:
                status['status'] = 'New'

        else:
            status['status'] = Status.SUPERVISOR_STATUS_CHOICES.get(status['status'])

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="corporate_request_status_report.csv"'

    writer = csv.DictWriter(response, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(statuses)

    return response

@login_required
def get_all_corporate_request_statuses_for_supervisor_excel(request):
    if not(is_company_supervisor_mixin_check(request.user)):
        return redirect_to_dashboard(request.user)

    current_user = request.user
    supervisor = get_company_employee(current_user)
    company = supervisor.company
    ids = list(Status.get_all_current_ids_queryset())

    fields = ['corporate_request__display_id', 'corporate_request__company_name',
        'corporate_request__duns', 'corporate_request__registration',
        'corporate_request__website', 'corporate_request__name_variant', 'corporate_request__parent_company_name',
        'corporate_request__recipient', 'corporate_request__street', 'corporate_request__dependent_locality',
        'corporate_request__locality', 'corporate_request__postalcode', 'corporate_request__country',
        'corporate_request__phone_number', 'corporate_request__email', 'corporate_request__created_by__user__last_name',
        'status']

    statuses = Status.objects.filter(
        id__in=ids, corporate_request__created_by__company=company).values(*fields)

    headers = ['Display ID', 'Company Name', 'Duns', 'Registration', 'Website', 'Name Variant', 'Parent Company Name',
               'Recipient', 'Street Address', 'Dependent Locality', 'Locality', 'Postal Code', 'Country', 'Phone Number'
               , 'Email', 'Created By', 'Status']

    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="CorporateRequests.xls"'
    workbook = xlwt.Workbook(encoding='ascii')
    worksheet = workbook.add_sheet('My Worksheet')
    row_index = 0
    col_index = 0
    for header in headers:
        worksheet.write(row_index, col_index, header)
        col_index += 1

    row_index = 1
    col_index = 0

    for row in statuses:
        if row['status'] == 1 or row['status'] == 2:
            row['status'] = 'New'
        elif row['status'] == 3:
            row['status'] = 'In Progress'
        elif row['status'] == 4:
            row['status'] = 'Completed'
        elif row['status'] == 5:
            row['status'] = 'Submitted'
        elif row['status'] == 6:
            row['status'] = 'In Progress'
        else:
            row['status'] = Status.SUPERVISOR_STATUS_CHOICES.get(row['status'])
        for col in row:
            worksheet.write(row_index, col_index, row[fields[col_index]])
            col_index += 1
        col_index = 0
        row_index += 1
    workbook.save(response)
    return response


def manager_average_request_time_json(request):
    submitted_statuses = Status.get_all_requests_by_status(Status.SUBMITTED_STATUS).values(
        'custom_request__in_progress_status__datetime',
        'custom_request__completed_status__datetime',
        'custom_request__request_type__due_diligence_type__name',
        'corporate_request__in_progress_status__datetime',
        'corporate_request__completed_status__datetime',
        'corporate_request__request_type__due_diligence_type__name',
        'request__in_progress_status__datetime',
        'request__completed_status__datetime',
        'request__request_type__due_diligence_type__name',
    )


    average = []

    count = {}
    count['Pre-Employment'] = 0
    count['Third Party'] = 0
    count['Background Investigations'] = 0
    count['Know Your Customer'] = 0

    time = {}
    time['Pre-Employment'] = None
    time['Third Party'] = None
    time['Background Investigations'] = None
    time['Know Your Customer'] = None

    cust_count = 0
    cust_hours = 0
    corp_count = 0
    corp_hours = 0
    ind_count = 0
    ind_hours = 0

    for status in submitted_statuses:
        if status['custom_request__request_type__due_diligence_type__name']:
            count[status['custom_request__request_type__due_diligence_type__name']] += 1

            if time[status['custom_request__request_type__due_diligence_type__name']] is not None:
                time[status['custom_request__request_type__due_diligence_type__name']] +=\
                    (status['custom_request__completed_status__datetime'] -
                     status['custom_request__in_progress_status__datetime'])
            else:
                time[status['custom_request__request_type__due_diligence_type__name']]\
                    = (status['custom_request__completed_status__datetime'] -
                       status['custom_request__in_progress_status__datetime'])

        if status['corporate_request__request_type__due_diligence_type__name']:
            count[status['corporate_request__request_type__due_diligence_type__name']] += 1
            if time[status['corporate_request__request_type__due_diligence_type__name']] is not None:

                time[status['corporate_request__request_type__due_diligence_type__name']] +=\
                    (status['corporate_request__completed_status__datetime'] - status['corporate_request__in_progress_status__datetime'])
            else:
                time[status['corporate_request__request_type__due_diligence_type__name']] =\
                    (status['corporate_request__completed_status__datetime'] - status['corporate_request__in_progress_status__datetime'])

        if status['request__request_type__due_diligence_type__name']:
            count[status['request__request_type__due_diligence_type__name']] += 1
            if time[status['request__request_type__due_diligence_type__name']] is not None:
                time[status['request__request_type__due_diligence_type__name']] +=\
                    (status['request__completed_status__datetime'] - status['request__in_progress_status__datetime'])
            else:
                time[status['request__request_type__due_diligence_type__name']] =\
                    (status['request__completed_status__datetime'] - status['request__in_progress_status__datetime'])




    human_resources = {"ddtype":"HR"}
    third_party = {"ddtype":"Third Party"}
    reg_comply = {"ddtype":"Full Scope"}
    bus_inv = {"ddtype":"Global"}



    if count['Pre-Employment'] > 0:
        raw_average = (time['Pre-Employment']/count['Pre-Employment'])
        human_resources['average'] = math.floor((raw_average.total_seconds()/3600) * 10 ** 2) / 10 ** 2
    else:
        human_resources['average'] = 0

    if count['Third Party'] > 0:
        raw_average = time['Third Party']/count['Third Party']
        third_party['average'] = math.floor((raw_average.total_seconds()/3600) * 10 ** 2) / 10 ** 2
    else:
        third_party['average'] = 0

    if count['Background Investigations'] > 0:
        raw_average = (time['Background Investigations']/count['Background Investigations'])
        reg_comply['average'] = math.floor((raw_average.total_seconds()/3600) * 10 ** 2) / 10 ** 2
    else:
        reg_comply['average'] = 0

    if count['Know Your Customer'] > 0:
        raw_average = (time['Know Your Customer']/count['Know Your Customer'])
        bus_inv['average'] = math.floor((raw_average.total_seconds()/3600) * 10 ** 2) / 10 ** 2
    else:
        bus_inv['average'] = 0

    average.append(human_resources)
    average.append(third_party)
    average.append(reg_comply)
    average.append(bus_inv)

    return JsonResponse(average, safe=False)


def celery_runner(request):

    zip_reports.delay()
    return redirect_to_dashboard(request.user)

@login_required
def migrate_attachments(request):
    if not(is_manager(request.user)):
        return redirect_to_dashboard(request.user)
    migrate_attachments = MigrateAttachments()
    migrate_attachments.start()
    return HttpResponseRedirect(reverse_lazy('manager_dashboard'))


@login_required
def survey_view(request):

    survey = settings.SURVEY_URL

    #Get current user
    user = request.user
    group = get_user_group(user)

    if is_company_supervisor_mixin_check(user):
        is_supervisor = True
    else:
        is_supervisor = False

    if is_company_employee(user):
        is_employee = True
    else:
        is_employee = False

    if group.name == COMPANY_EMPLOYEE_GROUP:
        return render(request, "core/survey.html", {
            'survey': survey,
            'is_supervisor': is_supervisor,
            'is_employee': is_employee
        })
    elif (group.name == SPOTLIT_MANAGER_GROUP):
        url = reverse_lazy('manager_dashboard')
        return redirect(url)
    elif (group.name == SPOTLIT_ANALYST_GROUP):
        url = reverse_lazy('analyst_dashboard')
        return redirect(url)
    elif (group.name == REVIEWER):
        url = reverse_lazy('reviewer_dashboard')
        return redirect(url)
    else:
        return redirect(reverse_lazy('login'))
