
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, ButtonHolder, Submit, Field, HTML, Div
from crispy_forms.bootstrap import FormActions, PrependedText

from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, SetPasswordForm
from django.template.defaultfilters import default

from localflavor.us.forms import USSocialSecurityNumberField, USPhoneNumberField, USZipCodeField, USStateSelect, \
    USStateField
from django_countries import countries
from django_countries.fields import CountryField
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from multiupload.fields import MultiFileField

from .models import BaseRequestDetailStatus, Request, CorporateRequest, SpotLitStaff, DueDiligenceType, Company, CompanyEmployee,\
    CompanyDueDiligenceTypeSelection, Service, DueDiligenceTypeServices, CompanyServiceSelection, Address, \
    DynamicRequestFormFields, RequestFormFieldTypes, LayoutGroupSections, \
    CustomRequest, CustomRequestFields, ClientAttachmentCustom, ClientAttachmentCorporate, ClientAttachment, \
    Surcharge, ChargeType
from .field_choices import *

from .utils import get_company_employee, check_for_contact_form_fields
from os.path import split
import collections, re, magic, datetime
from .validators import *


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)

        self.fields['username'].required = True
        self.fields['password'].required = True

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                HTML("""
                <label class="control-label visible-ie8 visible-ie9 requiredField">Email</label>
                <i class="fa fa-envelope"></i>"""),
                Field('username', css_class="placeholder-no-fix", type="text", autocomplete="off", placeholder="Email"),
                css_class="input-icon"
            ),
            Div(
                HTML("""
                <label class="control-label visible-ie8 visible-ie9 requiredField">Password</label>
                <i class="fa fa-lock"></i>"""),
                Field('password', css_class="placeholder-no-fix", type="text", autocomplete="off",
                      placeholder="Password"),
                css_class="input-icon"
            ),
            HTML("""

            <button id="login" type="submit" class="btn btn-secondary pull-right">
            Login <i class="m-icon-swapright m-icon-white"></i>
            </button>""")
        )

        self.helper.form_show_labels = False

    def clean_username(self):
        return self.cleaned_data['username'].lower()


class ChangePasswordForm(SetPasswordForm):
    MIN_LENGTH = 8

    def __init__(self, *args, **kwargs):
        super(ChangePasswordForm, self).__init__(*args, **kwargs)
        self.fields['new_password1'].validators.append(validate_password_strength)

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div('new_password1', 'new_password2'
                ),
            HTML("""
            <button type="submit" class="btn green pull-right">
            Submit <i class="m-icon-swapright m-icon-white"></i>
            </button>""")
        )

    def clean_new_password1(self):
        password1 = self.cleaned_data.get('new_password1')
        # At least MIN_LENGTH long
        if len(password1) < self.MIN_LENGTH:
            raise forms.ValidationError("The new password must be at least %d characters long." % self.MIN_LENGTH)

        lower = False
        upper = False
        number = False
        symbol = False

        for c in password1:
            if c.isdigit():
                number = True
            if c.isupper():
                upper = True
            if c.islower():
                lower = True
            if not c.isalpha() and not c.isdigit():
                symbol = True

        if not lower or not upper or not number or not symbol:
            raise forms.ValidationError("The new password must contain at least one uppercase letter,"
                                        " one lowercase letter, one digit, and and one special character")
        return password1


class ForgotPasswordForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super(PasswordResetForm, self).__init__(*args, **kwargs)

        self.fields['email'].required = True

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                HTML("""
                <label class="control-label visible-ie8 visible-ie9 requiredField">Email</label>
                <i class="fa fa-envelope"></i>"""),
                Field('email', css_class="placeholder-no-fix", type="text", autocomplete="off", placeholder="Email"),
                css_class="input-icon"
            ),
            HTML("""
            <button type="button" id="back-btn" class="btn" onclick="window.location='{% url 'login' %}'">
            <i class="m-icon-swapleft"></i> Back </button>
            <button type="submit" class="btn green pull-right">
            Submit <i class="m-icon-swapright m-icon-white"></i>
            </button>""")
        )

        self.helper.form_show_labels = False

    def save(self, domain_override='portal.voyint.com',
             subject_template_name='emails/reset_subject.txt',
             email_template_name='emails/reset_email.html',
             use_https=False, token_generator=default_token_generator,
             from_email='info@voyint.com', request=None):
        super(ForgotPasswordForm, self).save(domain_override='portal.voyint.com',
                                             subject_template_name=subject_template_name,
                                             email_template_name=email_template_name, use_https=use_https,
                                             token_generator=token_generator, from_email='info@voyint.com',
                                             request=None)


class IndividualRequestForm(forms.ModelForm):
    request_type = forms.ModelChoiceField(queryset=[])

    # non-required fields
    phone_number = USPhoneNumberField(required=False, label="Phone Number (XXX-XXX-XXXX)")
    ssn = USSocialSecurityNumberField(label='SSN (XXX-XX-XXXX)', required=False)
    birthdate = forms.DateField(widget=forms.widgets.DateInput(format="%m/%d/%Y"), label="Birthdate (mm/dd/yyyy)",
                                required=False)

    # address fields
    street = forms.CharField(label="Street Address", required=False, max_length=50)
    street2 = forms.CharField(label="Street Address 2", required=False, max_length=50)
    city = forms.CharField(label="City", required=False, max_length=50)
    state = USStateField(required=False, widget=USStateSelect())
    zipcode = USZipCodeField(required=False, max_length=10)
    annual_income_exceeds_75000 = forms.BooleanField(required=False,label='The subject\'s salary will exceed $75,000 (for Pre-Employment requests only) <span style="font-size:20px" data-toggle="tooltip" title="The FCRA sets some time limits on what can be reported (eg. Bankruptcies, liens, civil suits, etc.). These restrictions do not apply to applicants with a salary of $75,000 or more per year."><span class="glyphicon glyphicon-info-sign text-primary"></span></span>')
    state_of_employment = USStateField(required=False, widget=USStateSelect(),label='State of Employment (for Pre-Employment requests only) <span style="font-size:20px" data-toggle="tooltip " title="Certain states have specific pre-employment reporting requirements that we must adhere to if the candidate will work in that state"><span class="glyphicon glyphicon-info-sign text-primary"></span></span>')

    client_attachment = MultiFileField(min_num=0,
                                       max_num=10,
                                       max_file_size=1024*1024*25,
                                       label='Select a file to add as an attachment',
                                       required=False)


    def __init__(self, request, *args, **kwargs):
        self.request = request
        instance = None
        client_attachment = None
        if ('instance' in kwargs):
            instance = kwargs['instance']
        super(IndividualRequestForm, self).__init__(*args, **kwargs)

        types = CompanyDueDiligenceTypeSelection.get_due_diligence_types_for_current_user(self.request.user)
        company = CompanyEmployee.get_company_employee(self.request.user).company
        public_types = CompanyDueDiligenceTypeSelection.get_enabled_public_packages(company)
        self.fields['request_type'].queryset = types | public_types

        # middle name and email not required
        self.fields["middle_name"].required = False
        self.fields["email"].required = False

        # citizenship required
        self.fields["citizenship"].required = False

        #add United States to the top of the citizenship list
        us = dict(countries)['US']
        us_choice = ('US', us)
        current_choices = self.fields['citizenship'].choices
        all_choices = [us_choice] + current_choices
        self.fields['citizenship'].choices = all_choices

        #add 'Select a state' to the State choice list and make initial
        current_states = self.fields['state'].widget.choices
        current_states = [('Select', 'Select a state'), ] + current_states
        self.fields['state'].widget.choices = current_states

        current_states_of_employment = self.fields['state_of_employment'].widget.choices
        current_states_of_employment = [('Select', 'Select a state'), ] + current_states_of_employment
        self.fields['state_of_employment'].widget.choices = current_states_of_employment

        if (instance is not None and instance.address is not None):
            if (instance.address.street is not None and len(instance.address.street) > 0):
                self.fields['street'].initial = instance.address.street
            if (instance.address.street2 is not None and len(instance.address.street2) > 0):
                self.fields['street2'].initial = instance.address.street2
            if (instance.address.city is not None and len(instance.address.city) > 0):
                self.fields['city'].initial = instance.address.city
            if (instance.address.state is not None and len(instance.address.state) > 0):
                self.fields['state'].initial = instance.address.state
            if (instance.address.zipcode is not None and len(instance.address.zipcode) > 0):
                self.fields['zipcode'].initial = instance.address.zipcode

        self.helper = FormHelper()
        self.helper.layout = Layout(Div(
            Div(
                Div(HTML("""Due Diligence Request Type"""), css_class="panel-title"), css_class="panel-heading"),
            Div(
                Div(Div('request_type', css_class="col-md-12"), css_class="row")
                , css_class="panel-body")
            , css_class="panel panel-info"
        )
        )
        self.helper.layout.append(
            Div(
                Div(
                    Div(HTML("""Request Information"""), css_class="panel-title"), css_class="panel-heading"),
                Div(
                    Div(Div('first_name', css_class="col-md-12"), css_class="row"),
                    Div(Div('middle_name', css_class="col-md-12"), css_class="row"),
                    Div(Div('last_name', css_class="col-md-12"), css_class="row"),
                    Div(Div('citizenship', css_class="col-md-7"), Div('ssn', css_class="col-md-5"), css_class="row"),
                    Div(Div('birthdate', css_class="col-md-5"), css_class="row"),
                    Div(Div('annual_income_exceeds_75000', css_class="col-md-10"), css_class="row"),
                    Div(Div('state_of_employment', css_class="col-md-10"), css_class="row")
                    , css_class="panel-body")
                , css_class="panel panel-info"
            ))
        self.helper.layout.append(
            Div(
                Div(
                    Div(HTML("""Contact Information"""), css_class="panel-title"), css_class="panel-heading"),
                Div(
                    Div(Div('street', css_class="col-md-12"), css_class="row"),
                    Div(Div('street2', css_class="col-md-12"), css_class="row"),
                    Div(Div('city', css_class="col-md-5"), Div('state', css_class="col-md-4"),
                        Div('zipcode', css_class="col-md-3"), css_class="row"),
                    Div(Div('phone_number', css_class="col-md-8"), css_class="row"),
                    Div(Div('email', css_class="col-md-12"), css_class="row")
                    , css_class="panel-body")
                , css_class="panel panel-info"
            ))



        self.helper.layout.append(Div(HTML("""<hr><h4 class="block">Attachment:</h4>""")))
        self.helper.layout.append('client_attachment')
        self.helper.layout.append('comments')
        self.helper.layout.append(FormActions(
            Submit('create_request', 'Submit', css_class='btn-primary pull-right'),
        )
        )


    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if (len(first_name) > 50):
            self._errors['first_name'] = ['First name too long.']

        return first_name

    def clean_middle_name(self):
        middle_name = self.cleaned_data.get('middle_name')
        if (len(middle_name) > 50):
            self._errors['middle_name'] = ['Middle name too long.']

        return middle_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if (len(last_name) > 50):
            self._errors['lst_name'] = ['Last name too long.']

        return last_name

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if (len(phone_number) > 15):
            self._errors['phone_number'] = ['Invalid Phone Number']

        return phone_number

    def clean_client_attachment(self):
        attachments = self.cleaned_data.get('client_attachment')
        for attachment in self.cleaned_data['client_attachment']:
            if attachment:
                if not correct_file_type(attachment):
                    self._errors['client_attachment'] = ['File must be PDF, Zip, Microsoft Word File,'
                                                             ' Microsoft Excel File or JPEG.']
        return attachments

    def clean(self):
        cleaned_data = super(IndividualRequestForm, self).clean()

        street = ""
        street2 = ""
        city = ""
        state = ""
        zipcode = ""

        if ('street' in cleaned_data):
            street = cleaned_data['street']

        if ('street2' in cleaned_data):
            street2 = cleaned_data['street2']

        if ('city' in cleaned_data):
            city = cleaned_data['city']

        if ('state' in self.cleaned_data):
            state = cleaned_data['state']

        if ('zipcode' in cleaned_data):
            zipcode = cleaned_data['zipcode']

        # clean up state errors before custom validation
        if 'state' in self._errors:
            del self._errors['state']
        if 'state_of_employment' in self._errors:
            del self._errors['state_of_employment']

        # if they start inputting data about the address, make sure they have a complete address
        if ((street is not None and len(street) > 0) or (street2 is not None and len(street2) > 0)
            or (city is not None and len(city) > 0) or (zipcode is not None and len(zipcode) > 0)
            or (state and not 'Select' in state)):
        #     if street is None or len(street) == 0:
        #         self._errors['street'] = ['Street address required']
        #     if city is None or len(city) == 0:
        #         self._errors['city'] = ['City required']
            if not state or 'Select' in state:
                self._errors['state'] = ['State required']
            # if zipcode is None or len(zipcode) == 0:
            #     self._errors['zipcode'] = ['Zipcode required']


        return cleaned_data

    def save(self, *args, **kwargs):
        user = self.request.user
        request = super(IndividualRequestForm, self).save(commit=False)
        request.annual_income_exceeds_75000 = self.cleaned_data['annual_income_exceeds_75000']
        if "state_of_employment" in self.cleaned_data:
            request.state_of_employment = self.cleaned_data['state_of_employment']
        else:
            request.state_of_employment= None
        request.created_by = get_company_employee(user)

        if ("state" in self.cleaned_data and 'Select' not in self.cleaned_data['state']):
            street = self.cleaned_data['street']
            street2 = self.cleaned_data['street2']
            city = self.cleaned_data['city']
            state = self.cleaned_data['state']
            zipcode = self.cleaned_data['zipcode']
            address = Address(street=street, street2=street2, city=city, state=state, zipcode=zipcode)
            address.save()
            request.address = address

        request.save()

        display_id = Request.generate_display_id(request)
        request.display_id = display_id
        request.save()

        if "client_attachment" in self.cleaned_data:
            ClientAttachment.objects.filter(request=request).delete()

        for attachment in self.cleaned_data['client_attachment']:
            ind_attachment = ClientAttachment(created_by=request.created_by, request=request,
                                                       attachment=attachment).save()

            if not request.client_attachment:
                company_name = request.created_by.company.name.lower()
                attachment_url = "uploads/{}/{}".format(company_name, attachment.name)
                request.client_attachment = attachment_url
                request.save()

        return request


    class Meta:
        model = Request
        fields = ['request_type', 'first_name', 'middle_name', 'last_name', 'ssn', 'birthdate', 'phone_number', 'email',
                  'citizenship', 'comments']


def correct_file_type(attachment):
    is_good_type = False
    file_type = magic.from_buffer(attachment.read(1024))
    match = r'PDF document|Microsoft Office Document|Zip archive data|JPEG image data|Microsoft Excel 2007+'
    good_type = re.search(match, file_type)
    if good_type is not None:
        is_good_type = True
    return is_good_type


class CorporateRequestForm(forms.ModelForm):
    request_type = forms.ModelChoiceField(queryset=[], label="Request Type")
    company_name = forms.CharField(required=True, max_length=50, label="Company Name")

    # request info
    duns = forms.CharField(required=False, label="DUNS Number")
    registration = forms.CharField(required=False, label="Company Registration Number")
    website = forms.URLField(label="Website URL", required=False)
    name_variant = forms.CharField(max_length=50, required=False, label='Company Name Variant')
    parent_company_name = forms.CharField(max_length=50, required=False, label='Parent Company Name')
    comments = forms.CharField(widget=forms.Textarea, label="Comments", required=False)

    # contact info
    recipient = forms.CharField(required=False, max_length=50, label="Recipient")
    street = forms.CharField(required=False, max_length=200, label="Street Address")
    dependent_locality = forms.CharField(required=False, max_length=200, label="Dependent Locality")
    locality = forms.CharField(required=False, max_length=200, label="Locality")
    postalcode = forms.CharField(required=False, max_length=15)
    country = CountryField()
    email = forms.EmailField(label="Email", required=False)
    phone_number = forms.CharField(required=False, label="Phone Number")
    client_attachment = MultiFileField(min_num=0,
                                       max_num=10,
                                       max_file_size=1024*1024*25,
                                       label='Select a file to add as an attachment',
                                       required=False)

    def __init__(self, request, *args, **kwargs):
        self.request = request
        instance = None
        if ('instance' in kwargs):
            instance = kwargs['instance']
        super(CorporateRequestForm, self).__init__(*args, **kwargs)

        types = CompanyDueDiligenceTypeSelection.get_due_diligence_types_for_current_user(self.request.user)
        company = CompanyEmployee.get_company_employee(self.request.user).company
        public_types = CompanyDueDiligenceTypeSelection.get_enabled_public_packages(company)
        self.fields['request_type'].queryset = types | public_types


        self.helper = FormHelper()
        self.helper.layout = Layout(Div(
            Div(
                Div(HTML("""Due Diligence Request Type"""), css_class="panel-title"), css_class="panel-heading"),
            Div(
                Div(Div('request_type', css_class="col-md-12"), css_class="row")
                , css_class="panel-body")
            , css_class="panel panel-info"
        )
        )
        self.helper.layout.append(
            Div(
                Div(
                    Div(HTML("""Request Information"""), css_class="panel-title"), css_class="panel-heading"),
                Div(
                    Div(Div('company_name', css_class="col-md-12"), css_class="row"),
                    Div(Div('duns', css_class="col-md-12"), css_class="row"),
                    Div(Div('registration', css_class="col-md-12"), css_class="row"),
                    Div(Div('website', css_class="col-md-12"), css_class="row"),
                    Div(Div('name_variant', css_class="col-md-12"), css_class="row"),
                    Div(Div('parent_company_name', css_class="col-md-12"), css_class="row"),
                    css_class="panel-body"),
                css_class="panel panel-info"
            ))
        self.helper.layout.append(
            Div(
                Div(
                    Div(HTML("""Contact Information"""), css_class="panel-title"), css_class="panel-heading"),
                Div(
                    Div(Div('recipient', css_class="col-md-12"), css_class="row"),
                    Div(Div('street', css_class="col-md-12"), css_class="row"),
                    Div(Div('dependent_locality', css_class="col-md-12"), css_class="row"),
                    Div(Div('locality', css_class="col-md-12"), css_class="row"),
                    Div(Div('postalcode', css_class="col-md-12"), css_class="row"),
                    Div(Div('country', css_class="col-md-12"), css_class="row"),
                    Div(Div('email', css_class="col-md-12"), css_class="row"),
                    Div(Div('phone_number', css_class="col-md-12"), css_class="row"),
                    css_class="panel-body"),
                css_class="panel panel-info"
            ))


        self.helper.layout.append(Div(HTML("""<hr><h4 class="block">Attachment:</h4>""")))
        self.helper.layout.append('client_attachment')
        self.helper.layout.append(HTML("""<hr>"""))

        self.helper.layout.append('comments')
        self.helper.layout.append(FormActions(
            Submit('create_corporate_request', 'Submit', css_class='btn-primary pull-right'),
        )
        )

    def clean(self):
        cleaned_data = super(CorporateRequestForm, self).clean()

        if 'client_attachment' in cleaned_data:
            for attachment in self.cleaned_data['client_attachment']:
                if attachment:
                    if not correct_file_type(attachment):
                        self._errors['client_attachment'] = ['File must be PDF, Zip, Microsoft Word File,'
                                                             ' Microsoft Excel File or JPEG.']
        return cleaned_data

    def save(self, *args, **kwargs):
        user = self.request.user
        request = super(CorporateRequestForm, self).save(commit=False)



        request = CorporateRequest(request_type=self.cleaned_data['request_type'],
                                   company_name=self.cleaned_data['company_name'],
                                   duns=self.cleaned_data['duns'],
                                   registration=self.cleaned_data['registration'],
                                   website=self.cleaned_data['website'],
                                   name_variant=self.cleaned_data['name_variant'],
                                   parent_company_name=self.cleaned_data['parent_company_name'],
                                   comments=self.cleaned_data['comments'],
                                   recipient=self.cleaned_data['recipient'],
                                   street=self.cleaned_data['street'],
                                   dependent_locality=self.cleaned_data['dependent_locality'],
                                   locality=self.cleaned_data['locality'],
                                   postalcode=self.cleaned_data['postalcode'],
                                   country=self.cleaned_data['country'],
                                   email=self.cleaned_data['email'],
                                   phone_number=self.cleaned_data['phone_number'],
                                   created_by=get_company_employee(user)
                                   )
        request.save()

        display_id = CorporateRequest.generate_display_id(request)
        request.display_id = display_id
        request.save()

        if "client_attachment" in self.cleaned_data:
            ClientAttachmentCorporate.objects.filter(request=request).delete()

        for attachment in self.cleaned_data['client_attachment']:
            corporate_attachment = ClientAttachmentCorporate(created_by=request.created_by, request=request,
                                                       attachment=attachment).save()

            if not request.client_attachment:
                company_name = request.created_by.company.name.lower()
                attachment_url = "uploads/{}/{}".format(company_name, attachment.name)
                request.client_attachment = attachment_url
                request.save()

        return request

    class Meta:
        model = CorporateRequest
        fields = ['request_type', 'company_name', 'duns', 'registration', 'website', 'name_variant',
                  'parent_company_name', 'comments',
                  'recipient', 'street', 'dependent_locality', 'locality', 'postalcode', 'country', 'email',
                  'phone_number', 'client_attachment']



class IndividualRequestFormManager(forms.ModelForm):
    client_attachment = MultiFileField(min_num=0,
                                       max_num=10,
                                       max_file_size=1024*1024*25,
                                       label='Select a file to add as an attachment',
                                       required=True)

    def __init__(self, request, *args, **kwargs):
        self.request = request
        instance = None
        if ('instance' in kwargs):
            instance = kwargs['instance']
        super(IndividualRequestFormManager, self).__init__(*args, **kwargs)

        self.helper = FormHelper()

        self.helper.layout = Layout(Div(HTML("""<hr><h4 class="block">Attachment:</h4>""")))
        self.helper.layout.append('client_attachment')
        self.helper.layout.append(HTML("""<hr>"""))

        self.helper.layout.append(FormActions(
            Submit('create_corporate_request', 'Submit', css_class='btn-primary pull-right'),
        )
        )

    def clean(self):
        cleaned_data = super(IndividualRequestFormManager, self).clean()

        if 'client_attachment' in cleaned_data:
            for attachment in self.cleaned_data['client_attachment']:
                if attachment:
                    if not correct_file_type(attachment):
                        self._errors['client_attachment'] = ['File must be PDF, Zip, Microsoft Word File,'
                                                             ' Microsoft Excel File or JPEG.']
        return cleaned_data

    def save(self, *args, **kwargs):
        user = self.request.user
        request = super(IndividualRequestFormManager, self).save(commit=False)

        if "client_attachment" in self.cleaned_data:
            ClientAttachment.objects.filter(request=request).delete()

        for attachment in self.cleaned_data['client_attachment']:
            ind_attachment = ClientAttachment(created_by=request.created_by, request=request,
                                                       attachment=attachment).save()

            if not request.client_attachment:
                company_name = request.created_by.company.name.lower()
                attachment_url = "uploads/{}/{}".format(company_name, attachment.name)
                request.client_attachment = attachment_url
                request.save()

        return request

    class Meta:
        model = Request
        fields = ['client_attachment']

class CorporateRequestFormManager(IndividualRequestFormManager):
    def save(self, *args, **kwargs):
        user = self.request.user
        request = super(IndividualRequestFormManager, self).save(commit=False)

        if "client_attachment" in self.cleaned_data:
            ClientAttachmentCorporate.objects.filter(request=request).delete()

        for attachment in self.cleaned_data['client_attachment']:
            corporate_attachment = ClientAttachmentCorporate(created_by=request.created_by, request=request,
                                                       attachment=attachment).save()

            if not request.client_attachment:
                company_name = request.created_by.company.name.lower()
                attachment_url = "uploads/{}/{}".format(company_name, attachment.name)
                request.client_attachment = attachment_url
                request.save()

        return request
    class Meta:
        model = CorporateRequest
        fields = ['client_attachment']


class CustomRequestFormManager(IndividualRequestFormManager):
    def save(self, *args, **kwargs):
        user = self.request.user
        request = super(IndividualRequestFormManager, self).save(commit=False)

        if "client_attachment" in self.cleaned_data:
            ClientAttachmentCustom.objects.filter(request=request).delete()

        for attachment in self.cleaned_data['client_attachment']:
            custom_attachment = ClientAttachmentCustom(created_by=request.created_by, request=request,
                                                       attachment=attachment).save()

            if not request.client_attachment:
                company_name = request.created_by.company.name.lower()
                attachment_url = "uploads/{}/{}".format(company_name, attachment.name)
                request.client_attachment = attachment_url
                request.save()

        return request
    class Meta:
        model = CustomRequest
        fields = ['client_attachment']

class CompanyForm(forms.ModelForm):
    # address fields
    street = forms.CharField(label="Street Address", required=False, max_length=50)
    street2 = forms.CharField(label="Street Address 2", required=False, max_length=50)
    city = forms.CharField(label="City", required=False, max_length=50)
    state = USStateField(required=False, widget=USStateSelect())
    zipcode = USZipCodeField(required=False, max_length=10)
    terms_agreed = forms.BooleanField(required=True,label="I have reviewed the <a href='https://www.voyint.com/proposal'> Voyint Services Proposal</a>. I understand that standard background check packages (Tier I-III) will be immediately available to my portal account. Additional Services or updated packages can be added by our team at any time.")

    def __init__(self, *args, **kwargs):
        instance = None
        if ('instance' in kwargs):
            instance = kwargs['instance']

        super(CompanyForm, self).__init__(*args, **kwargs)

        if (instance is not None and instance.address is not None):
            if (instance.address.street is not None and len(instance.address.street) > 0):
                self.fields['street'].initial = instance.address.street
            if (instance.address.street2 is not None and len(instance.address.street2) > 0):
                self.fields['street2'].initial = instance.address.street2
            if (instance.address.city is not None and len(instance.address.city) > 0):
                self.fields['city'].initial = instance.address.city
            if (instance.address.state is not None and len(instance.address.state) > 0):
                self.fields['state'].initial = instance.address.state
            if (instance.address.zipcode is not None and len(instance.address.zipcode) > 0):
                self.fields['zipcode'].initial = instance.address.zipcode

        self.helper = FormHelper()
        self.helper.layout = Layout(
            'name',
            'phone_number',
            'tax_id',
            Div(HTML("""<h3 class="form-section">Address</h3>"""),
                Div(Div('street', css_class="col-md-12"), css_class="row"),
                Div(Div('street2', css_class="col-md-12"), css_class="row"),
                Div(Div('city', css_class="col-md-5"), Div('state', css_class="col-md-3"),
                    Div('zipcode', css_class="col-md-4"), css_class="row")),
                Div(Div('terms_agreed', css_class="col-md-12"), css_class="row"),
            FormActions(
                Submit('create_company', 'Submit', css_class='btn-primary'),
            )
        )

    class Meta:
        model = Company
        fields = ['name', 'phone_number', 'tax_id', ]

    def save(self, *args, **kwargs):
        company = super(CompanyForm, self).save(commit=True)

        if (self.cleaned_data['street'] is not None and len(self.cleaned_data['street']) > 0):
            street = self.cleaned_data['street']
            street2 = self.cleaned_data['street2']
            city = self.cleaned_data['city']
            state = self.cleaned_data['state']
            zipcode = self.cleaned_data['zipcode']
            address = Address(street=street, street2=street2, city=city, state=state, zipcode=zipcode)
            address.save()
            company.address = address
        company.save()
        return company

    def clean(self):
        cleaned_data = super(CompanyForm, self).clean()

        street = ""
        street2 = ""
        city = ""
        state = ""
        zipcode = ""

        if ('street' in cleaned_data):
            street = cleaned_data['street']

        if ('street2' in cleaned_data):
            street2 = cleaned_data['street2']

        if ('city' in cleaned_data):
            city = cleaned_data['city']

        if ('state' in cleaned_data):
            state = cleaned_data['state']

        if ('zipcode' in cleaned_data):
            zipcode = cleaned_data['zipcode']

        if ('terms_agreed' in cleaned_data):
            if cleaned_data["terms_agreed"] == False:
                self._errors["terms_agreed"] = ["Field Required"]

        # if they start inputting data about the address, make sure they have a complete address
        if ((street is not None and len(street) > 0) or (street2 is not None and len(street2) > 0)
            or (city is not None and len(city) > 0) or (zipcode is not None and len(zipcode) > 0)):
            if street is None or len(street) == 0:
                self._errors['street'] = ['Street address required']
            if city is None or len(city) == 0:
                self._errors['city'] = ['City required']
            if state is None or len(state) == 0:
                self._errors['state'] = ['State required']
            if zipcode is None or len(zipcode) == 0:
                self._errors['zipcode'] = ['Zipcode required']

        return cleaned_data


class SetCompanyCorporateForm(forms.Form):
    is_corporate = forms.BooleanField(required=False, label="")

    def __init__(self, *args, **kwargs):
        if 'is_corp' in kwargs:
            is_corp = kwargs.pop('is_corp')
        super(SetCompanyCorporateForm, self).__init__(*args, **kwargs)

        if is_corp:
            self.fields['is_corporate'].initial = is_corp

        self.helper = FormHelper()
        self.helper.layout = Layout('is_corporate')


class SetCompanyIndividualForm(forms.Form):
    is_individual = forms.BooleanField(required=False, label="")

    def __init__(self, *args, **kwargs):
        if 'is_individual' in kwargs:
            is_individual = kwargs.pop('is_individual')
        super(SetCompanyIndividualForm, self).__init__(*args, **kwargs)

        if is_individual:
            self.fields['is_individual'].initial = is_individual

        self.helper = FormHelper()
        self.helper.layout = Layout('is_individual')

class AnalystNotesForm(forms.Form):
    def __init__(self, *args, **kwargs):
        analyst_notes = ""
        if ('analyst_notes' in kwargs):
            analyst_notes = kwargs.pop('analyst_notes')
        super(AnalystNotesForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout()
        self.helper.form_tag = False

        self.fields['analyst_notes'] = forms.CharField(label="Notes",
                                                           widget=forms.Textarea,
                                                           required=True)

        if len(analyst_notes) > 0:
            self.fields['analyst_notes'].initial = analyst_notes
        self.helper.layout.append('analyst_notes')

class AnalystInternalDocForm(forms.Form):
    def __init__(self, *args, **kwargs):
        analyst_internal_doc = None
        if ('analyst_internal_doc' in kwargs):
            analyst_internal_doc = kwargs.pop('analyst_internal_doc')
        super(AnalystInternalDocForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout()
        self.helper.form_tag = False

        self.fields['analyst_internal_doc'] = forms.FileField(label='Select a file to add as an internal document', required=False)                                                        

        if analyst_internal_doc is not None:
            self.fields['analyst_internal_doc'].initial = analyst_internal_doc
        self.helper.layout.append('analyst_internal_doc')


class AnalystRequestDetailStatusForm(forms.Form):
    def __init__(self, *args, **kwargs):
        REQUEST_ANALYST_CHOICES=(
            (BaseRequestDetailStatus.INITIAL_DB_CHECK_IN_PROGRESS_STATUS,"Inital database checks in-progress"),
            (BaseRequestDetailStatus.REQUEST_FOR_VALIDATION_IN_PROGRESS_STATUS,"Request for validation in-progress"),
            (BaseRequestDetailStatus.PENDING_COURT_RUNNER_STATUS,"Pending Court Runner(s)"),
            (BaseRequestDetailStatus.PENDING_EMPLOYEE_VERIFICATION_STATUS,"Pending Employment Verification(s)"),
            (BaseRequestDetailStatus.PENDING_EDUCATION_VERIFICATION_STATUS,"Pending Education Verification(s)"),
            (BaseRequestDetailStatus.FINAL_DB_CHECKS_AND_WRITE_UP_IN_PROGRESS_STATUS,"Final database checks and write-up in-progress"),
            (BaseRequestDetailStatus.OTHER,"Other")
        )
        request_analyst_status= None
        request_analyst_status_other_text= ""

        if ('request_detail_statuses' in kwargs):
            request_detail_statuses = kwargs.pop('request_detail_statuses')

        if ('request_detail_other_text' in kwargs):
            request_detail_other_text = kwargs.pop('request_detail_other_text')

        super(AnalystRequestDetailStatusForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout()
        self.helper.form_tag = False

        self.fields["request_analyst_status"]= forms.MultipleChoiceField(label="Select the Request Status:", choices=REQUEST_ANALYST_CHOICES,
                                         widget=forms.CheckboxSelectMultiple,required=False)
        self.fields["request_analyst_status"].initial=request_detail_statuses

        self.helper.layout.append('request_analyst_status')

        self.fields["request_analyst_status_other_text"] = forms.CharField(label="If Other, please mention:",max_length=100,required=False)
        self.fields["request_analyst_status_other_text"].initial = request_detail_other_text
        self.helper.layout.append('request_analyst_status_other_text')


class ServicesForm(forms.Form):
    def __init__(self, *args, **kwargs):
        CHOICES = ((True, 'Found Information to Report',), (False, 'No Information to Report',))
        initial = []
        service_statuses = []
        general_comments = ""
        should_have_submit_buttons = False
        attachment = None
        client_attachment = None
        executive_summary = ""
        render_rich_text = None
        if ('initial' in kwargs):
            initial = kwargs.pop('initial')

        if ('analyst_buttons' in kwargs):
            analyst_buttons = kwargs.pop('analyst_buttons')

        if ('reviewer_buttons' in kwargs):
            reviewer_buttons = kwargs.pop('reviewer_buttons')

        if ('service_statuses' in kwargs):
            service_statuses = kwargs.pop('service_statuses')

        if ('executive_summary' in kwargs):
            executive_summary = kwargs.pop('executive_summary')

        if ('render_rich_text' in kwargs):
            render_rich_text = kwargs.pop('render_rich_text')

        if ('pending' in kwargs):
            pending = kwargs.pop('pending')

        service_status_dict = {}
        if service_statuses:
            for service_status in service_statuses:
                service_status_dict[service_status.service.service.id] = service_status

        if ('file' in kwargs):
            attachment = kwargs.pop('file')
        if ('client_file' in kwargs):
            attachment = kwargs.pop('client_file')
        super(ServicesForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.layout = Layout()
        self.helper.form_tag = False

        # exec summary
        self.fields['executive_summary'] = forms.CharField(label="Executive Summary",
                                                           widget=forms.Textarea,
                                                           required=True)

        if render_rich_text:
            if len(executive_summary) > 0:
                self.fields['executive_summary'].initial = executive_summary
            self.helper.layout.append('executive_summary')
        else:
            self.helper.layout.append(HTML("<label class=\"control-label requiredField\" for=\"id_executive_summary\">Executive Summary<span class=\"asteriskField\">*</span></label>"))
            self.helper.layout.append(HTML("<div style=\"background:#D8D8D8\">" + executive_summary + "</div>"))

        self.helper.layout.append(HTML("""<hr>"""))

        for selection in initial:
            selection_initial = None
            comment_initial = None
            if (selection.service.id in service_status_dict.keys()):
                service_status = service_status_dict[selection.service.id]
                selection_initial = service_status.results
                comment_initial = service_status.comments

            selection_id = 'selection_%s' % selection.id
            comment_id = 'comment_%s' % selection.id
            self.fields[selection_id] = forms.ChoiceField(label=selection.service.name, widget=forms.RadioSelect,
                                                          choices=CHOICES)
            if (selection_initial is not None):
                self.fields[selection_id].initial = selection_initial
            else:
                if (selection_id in self.data):
                    selection_initial = self.data[selection_id]
            self.helper.layout.append(Field(selection_id, css_class='selection'))

            if render_rich_text:
                self.fields[comment_id] = forms.CharField(label="Results", widget=forms.Textarea, required=False)

                if (comment_initial):
                    self.fields[comment_id].initial = comment_initial

                if (selection_initial == True or selection_initial == 'True'):
                    self.helper.layout.append(
                        Div(Field(comment_id), ccc_class="comment-div show-div", name="div_" + comment_id))
                else:
                    self.helper.layout.append(
                        Div(Field(comment_id), css_class='comment-div hide-div', name="div_" + comment_id))
                    # TODO: and here


            elif (selection_initial == True or selection_initial == 'True'):
                self.helper.layout.append(
                        Div(Field(comment_id), ccc_class="comment-div show-div", name="div_" + comment_id))

                self.helper.layout.append(HTML("<label class=\"control-label requiredField\" for=\"" +comment_id+"\">Results</label>"))
                self.helper.layout.append(Div(HTML("<div id=\""+ comment_id +"\" style=\"background:#D8D8D8\">" + comment_initial + "</div>"), ccc_class="comment-div show-div", name="div_" + comment_id))
            else:
                self.helper.layout.append(Div(Field(comment_id), css_class='comment-div hide-div', name="div_" + comment_id))
                # TODO: HERE


        if analyst_buttons:
            self.fields['attachment'] = forms.FileField(label='Select a file to add as an attachment', required=False)
            if attachment:
                self.fields['attachment'].initial = attachment

            self.helper.layout.append(Div(HTML("""<hr><h4 class="block">Attachment:</h4>""")))
            self.helper.layout.append('attachment')
            self.helper.layout.append(HTML("""<hr>"""))

            self.helper.layout.append(FormActions(
                Submit('save_services', 'Save for Later', css_class='btn-primary'),
                Submit('submit_as_pending', 'Submit as Pending', css_class='btn-primary') if pending is True else None,
                Submit('submit_request_for_review', 'Submit For Review', css_class='btn-danger pull-right')))

        elif reviewer_buttons:
            self.fields['attachment'] = forms.FileField(label='Select a file to add as an attachment', required=False)
            if attachment:
                self.fields['attachment'].initial = attachment

            self.helper.layout.append(Div(HTML("""<hr><h4 class="block">Attachment:</h4>""")))
            self.helper.layout.append('attachment')
            self.helper.layout.append(HTML("""<hr>"""))

            self.helper.layout.append(FormActions(
                Submit('save_services_reviewer', 'Save for Later', css_class='btn-primary'),
                Submit('submit_request', 'Submit To Manager', css_class='btn-danger pull-right')))

        elif attachment is not None:
            path, name = split(attachment.url)
            self.helper.layout.append(Div(HTML("""<hr><j4 class="block">Attachment:</h4>""")))
            self.helper.layout.append(Div(HTML("""
                <a target="_blank" href=\"""" + attachment.url + """\">""" + name + """</a>""")))


class CompanyEmployeeRegistrationForm(forms.Form):
    username = forms.CharField()
    first_name = forms.CharField()
    last_name = forms.CharField()
    position = forms.CharField(required=False)
    phone_number = forms.CharField(required=False)
    supervisor = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        if 'instance' in kwargs:
            kwargs.pop('instance')
        employee = None
        if 'initial' in kwargs:
            initial = kwargs['initial']
            if 'employee' in initial:
                employee = initial.pop('employee')
        super(CompanyEmployeeRegistrationForm, self).__init__(*args, **kwargs)

        # username and email will be the same
        self.fields['username'].label = "Email Address:"
        self.fields['username'].help_text = "Enter unique email address"

        if employee:
            self.fields['username'].initial = employee.user.username
            self.fields['first_name'].initial = employee.user.first_name
            self.fields['last_name'].initial = employee.user.last_name
            self.fields['position'].initial = employee.position
            self.fields['phone_number'].initial = employee.phone_number
            self.fields['supervisor'].initial = employee.supervisor

        self.helper = FormHelper()
        self.helper.layout = Layout(
            'username',
            'first_name',
            'last_name',
            'position',
            'phone_number',
            'supervisor',
            ButtonHolder(
                Submit('register', 'Submit', css_class='btn-primary')
            )
        )

        # class Meta:
        # model= User
        # fields = ("username","first_name", "last_name", "position", "phone_number")

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if (len(phone_number) > 15):
            self._errors['phone_number'] = ['Invalid Phone Number']

        return phone_number

    def clean_position(self):
        position = self.cleaned_data.get('position')
        if (len(position) > 50):
            self._errors['position'] = ['Position too long.']

        return position


class CustomerRegistrationForm(forms.Form):
    username = forms.CharField()
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput())
    first_name = forms.CharField()
    last_name = forms.CharField()
    phone_number = forms.CharField(required=False)

    def __init__(self,*args,**kwargs):
        super(CustomerRegistrationForm, self).__init__(*args, **kwargs)
        self.fields['password'].validators.append(validate_password_strength)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'username',
            'email',
            'password',
            'first_name',
            'last_name',
            'phone_number',
            ButtonHolder(
                Submit('register', 'Submit', css_class='btn-primary')
            )
        )

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if (len(phone_number) > 15):
            self._errors['phone_number'] = ['Invalid Phone Number']

        return phone_number


class CompanyDueDiligenceSelectionForm(forms.Form):
    name = forms.CharField(label="Choose a due diligence type name:", required=False)
    levels = forms.ChoiceField(label="Select a billing level:",
                               choices=CompanyDueDiligenceTypeSelection.TYPE_LEVEL_CHOICES)
    services = forms.MultipleChoiceField(label="Select the services to be performed:", choices=[],
                                         widget=forms.CheckboxSelectMultiple)
    # comments = forms.CharField(widget=forms.Textarea)
    price = forms.FloatField()
    invoice_instructions = forms.CharField(widget=forms.Textarea, required=False)
    is_active = forms.BooleanField(required=False, label="Activated?")

    def __init__(self, *args, **kwargs):
        instance = kwargs.pop('instance', None)
        super(CompanyDueDiligenceSelectionForm, self).__init__(*args, **kwargs)

        if instance:
            self.fields['name'].initial = instance.name
            self.fields['levels'].initial = instance.level
            # self.fields['comments'].initial = instance.comments
            self.fields['price'].initial = instance.price
            self.fields['invoice_instructions'].initial = instance.invoice_instructions
            self.fields['is_active'].initial = instance.is_active

            services_to_select = []
            service_selections = CompanyServiceSelection.objects.filter(dd_type=instance)
            for service_selection in service_selections:
                services_to_select.append(service_selection.service.name)
            self.fields['services'].initial = services_to_select

        self.helper = FormHelper()
        self.helper.layout = Layout(
            'levels',
            'name',
            PrependedText('price', '$'),
            'invoice_instructions',
            PrependedText('is_active', ''),
            'services'
        )


class HumanResourcesTypeSelectionForm(CompanyDueDiligenceSelectionForm):
    def __init__(self, *args, **kwargs):
        super(HumanResourcesTypeSelectionForm, self).__init__(*args, **kwargs)

        services = DueDiligenceTypeServices.get_all_services_for_type("Pre-Employment")
        self.fields['services'].choices = zip(services, services)

        self.helper.layout.append(
            ButtonHolder(
                Submit('human_resources', 'Submit', css_class='btn-primary')
            )
        )


class InvestigativeTypeSelectionForm(CompanyDueDiligenceSelectionForm):
    def __init__(self, *args, **kwargs):
        super(InvestigativeTypeSelectionForm, self).__init__(*args, **kwargs)

        services = DueDiligenceTypeServices.get_all_services_for_type("Third Party")
        self.fields['services'].choices = zip(services, services)

        self.helper.layout.append(
            ButtonHolder(
                Submit('investigative', 'Submit', css_class='btn-primary')
            )
        )


class RegulatoryTypeSelectionForm(CompanyDueDiligenceSelectionForm):
    def __init__(self, *args, **kwargs):
        super(RegulatoryTypeSelectionForm, self).__init__(*args, **kwargs)

        services = DueDiligenceTypeServices.get_all_services_for_type("Background Investigations")
        self.fields['services'].choices = zip(services, services)

        self.helper.layout.append(
            ButtonHolder(
                Submit('regulatory', 'Submit', css_class='btn-primary')
            )
        )


class BusinessInvestmentTypeSelectionForm(CompanyDueDiligenceSelectionForm):
    def __init__(self, *args, **kwargs):
        super(BusinessInvestmentTypeSelectionForm, self).__init__(*args, **kwargs)

        services = DueDiligenceTypeServices.get_all_services_for_type("Know Your Customer")
        self.fields['services'].choices = zip(services, services)
        self.helper.layout.append(
            ButtonHolder(
                Submit('business_investment', 'Submit', css_class='btn-primary')
            )
        )


class CompanyAdminForm(forms.ModelForm):
    individual_template = forms.FilePathField(path="%s/templates/reports" % settings.SITE_ROOT, required=None)
    corporate_template = forms.FilePathField(path="%s/templates/reports" % settings.SITE_ROOT, required=None)

    class Meta:
        model = Company
        fields = ['name', 'address', 'phone_number', 'tax_id', 'logo', 'report_logo', 'individual_template',
              'corporate_template', 'is_corporate', 'is_individual', 'is_custom', 'company_logo_active',
              'report_logo_active', 'batch_upload_active', 'restrict_attachments','terms_agreed']


class DynamicRequestFormForm(forms.Form):
    name = forms.CharField()
    render_form = forms.BooleanField(label="Display Custom Request", required=False)

    def __init__(self, *args, **kwargs):
        drf = None
        if 'initial' in kwargs:
            initial = kwargs['initial']
            if 'dynamic_request_form' in initial:
                drf = initial.pop('dynamic_request_form')
        super(DynamicRequestFormForm, self).__init__(*args, **kwargs)

        if drf:
            self.fields['name'].initial = drf.name
            self.fields['render_form'].initial = drf.render_form

        self.fields['name'].label = "Name:"
        self.fields['name'].help_text = "Enter unique name"

        self.helper = FormHelper()
        self.helper.layout = Layout(
            'name',
            'render_form',
            ButtonHolder(
                Submit('create_custom_request', 'Submit', css_class='btn-primary')
            )
        )


class DynamicRequestFormFieldsForm(forms.Form):
    label = forms.CharField()
    help_text = forms.CharField(label="Help Text", required=False)
    group = forms.ModelChoiceField(queryset=[], label="Layout Group Section")
    type = forms.ModelChoiceField(queryset=[])
    sort_order = forms.IntegerField(label="Sort Order", initial=0)
    field_format = forms.CharField(widget=forms.Textarea, required=False)
    required = forms.BooleanField(required=False)
    archive = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        field = None
        if 'initial' in kwargs:
            initial = kwargs['initial']
            if 'field' in initial:
                field = initial.pop('field')

        super(DynamicRequestFormFieldsForm, self).__init__(*args, **kwargs)

        if field:
            self.fields['label'].initial = field.label
            self.fields['help_text'].initial = field.help_text
            self.fields['group'].initial = field.group
            self.fields['type'].initial = field.type
            self.fields['sort_order'].initial = field.sort_order
            self.fields['field_format'].initial = field.field_format
            self.fields['required'].initial = field.required
            self.fields['archive'].initial = field.archive

        self.fields['label'].label = "Field Label:"
        self.fields['archive'].label = "Archived"

        groups = LayoutGroupSections.objects.all()
        self.fields['group'].queryset = groups
        self.fields['group'].help_text = "Section of the Form the field renders."

        types = RequestFormFieldTypes.objects.all()
        self.fields['type'].queryset = types

        self.fields['field_format'].help_text = "If type 'LIST', use semicolon-delimited values"

        self.helper = FormHelper()
        self.helper.layout = Layout(
            'required',
            'archive',
            'label',
            'help_text',
            'type',
            'group',
            'sort_order',
            'field_format',
            ButtonHolder(
                Submit('dynamic_request_form_configure', 'Submit', css_class='btn-primary'),
                HTML("""<a class="btn btn-info" href="{% url 'company' dynamic_request_form.company.id %}">Back to Company Profile</a>""")
            ),
        )


class CustomRequestForm(forms.Form):
    name = forms.CharField(label='Name:')
    request_type = forms.ModelChoiceField(queryset=[], required=False)
    comments = forms.CharField(widget=forms.Textarea, required=False, label='Comments:')

    def __init__(self, request, *args, **kwargs):
        self.request = request
        update = None
        instance = None
        client_attachment = None
        fields = None
        if ('instance' in kwargs):
            instance = kwargs.pop('instance')
        if ('fields' in kwargs):
            fields = kwargs.pop('fields')
        if ('update' in kwargs):
            update = kwargs.pop('update')


        super(CustomRequestForm, self).__init__(*args, **kwargs)

        types = CompanyDueDiligenceTypeSelection.get_due_diligence_types_for_current_user(self.request.user)
        company = CompanyEmployee.get_company_employee(self.request.user).company
        public_types = CompanyDueDiligenceTypeSelection.get_enabled_public_packages(company)
        self.fields['request_type'].queryset = types | public_types

        if update:
            self.fields['request_type'].initial = instance.request_type
            self.fields['name'].initial = instance.name
            self.fields['comments'].initial = instance.comments

        for field in fields:
            choices = collections.OrderedDict()
            if update:
                if str(field.form_field.type) == 'List':
                    selection = field.form_field.field_format.split(';')
                    selection.sort()
                    choices[''] = '-----------'
                    for item in selection:
                        choices[item] = item

                    self.fields['custom_%s' % field.form_field.id] = forms.ChoiceField(choices=[(choice, choice) for choice in choices],
                                                                                 label=field.form_field.label,
                                                                                 required=field.form_field.required)

                elif str(field.form_field.type) == 'Text Area':
                    self.fields['custom_%s' % field.form_field.id] = forms.CharField(widget=forms.Textarea, required=field.form_field.required,
                                                                          label=field.form_field.label)

                elif str(field.form_field.type) == 'State':
                    self.fields['custom_%s' % field.form_field.id] = USStateField(required=False, widget=USStateSelect(),label=field.form_field.label)
                
                else:
                    self.fields['custom_%s' % field.form_field.id] = forms.CharField(label=field.form_field.label, required=field.form_field.required)

                self.fields['custom_%s' % field.form_field.id].initial = field.value
                self.fields['custom_%s' % field.form_field.id].help_text = field.form_field.help_text
            else:
                if str(field.type) == 'List':
                    selection = field.field_format.split(';')
                    selection.sort()
                    choices[''] = '-----------'
                    for item in selection:
                        choices[item] = item

                    self.fields['custom_%s' % field.id] = forms.ChoiceField(choices=[(choice, choice) for choice in choices],
                                                                                 label=field.label,
                                                                                 required=field.required)
                elif str(field.type) == 'Text Area':
                    self.fields['custom_%s' % field.id] = forms.CharField(widget=forms.Textarea, required=field.required,
                                                                          label=field.label)

                elif str(field.type) == 'State':
                    self.fields['custom_%s' % field.id] = USStateField(required=False, widget=USStateSelect(),label=field.label)
                
                else:
                    self.fields['custom_%s' % field.id] = forms.CharField(label=field.label, required=field.required)

                self.fields['custom_%s' % field.id].help_text = field.help_text

        self.helper = FormHelper()

        self.helper.layout = Layout(Div(
            Div(
                Div(HTML("""Due Diligence Request Type"""), css_class="panel-title"), css_class="panel-heading"),
            Div(
                Div(Div('request_type', css_class="col-md-12"), css_class="row")
                , css_class="panel-body")
            , css_class="panel panel-info"
        ))

        panel = Div(css_class="panel panel-info")
        panel.append(Div(Div(HTML("""Request Information"""), css_class="panel-title"), css_class="panel-heading"))
        panel.append(Div(Div(Div('name', css_class="col-md-12"), css_class="row"), css_class="panel-body"))
        for field in fields:
            if update:
                if field.form_field.group.group_name == LayoutGroupSections.REQUEST_INFO:
                    panel.append(
                        Div(Div(Div('custom_%s' % field.form_field.id, css_class="col-md-12"), css_class="row"),
                            css_class="panel-body"))
            else:
                if field.group.group_name == LayoutGroupSections.REQUEST_INFO:
                    panel.append(Div(Div(Div('custom_%s' % field.id, css_class="col-md-12"), css_class="row"),
                                     css_class="panel-body"))
        self.helper.layout.append(panel)

        if check_for_contact_form_fields(fields, update):
            panel = Div(css_class="panel panel-info")
            panel.append(Div(Div(HTML("""Contact Information"""), css_class="panel-title"), css_class="panel-heading"))
            for field in fields:
                if update:
                    if field.form_field.group.group_name == LayoutGroupSections.CONTACT_INFO:
                        panel.append(
                            Div(Div(Div('custom_%s' % field.form_field.id, css_class="col-md-12"), css_class="row"),
                                css_class="panel-body"))
                else:
                    if field.group.group_name == LayoutGroupSections.CONTACT_INFO:
                        panel.append(Div(Div(Div('custom_%s' % field.id, css_class="col-md-12"), css_class="row"),
                                        css_class="panel-body"))
            self.helper.layout.append(panel)

        self.fields['client_attachment'] = MultiFileField(min_num=0, max_num=10,
                                                          label='Select a file to add as an attachment', required=False,
                                                          max_file_size=1024*1024*25)

        if update:
            self.fields['client_attachment'].initial = MultiFileField(min_num=0, max_num=10, max_file_size=1024*1024*5)

        self.helper.layout.append(Div(HTML("""<hr><h4 class="block">Attachment:</h4>""")))
        self.helper.layout.append('client_attachment')
        self.helper.layout.append('comments')

        self.helper.layout.append(FormActions(
            Submit('create_request', 'Submit', css_class='btn-primary pull-right'),
        ))


    def clean_name(self):
        name = self.cleaned_data.get('name')
        if (len(name) > 50):
            self._errors['name'] = ['Name too long.']

        return name

    def clean_request_type(self):
        request_type = self.cleaned_data.get('request_type')
        if not request_type:
            self._errors['request_type'] = ['Due Diligence Request type is required.']

        return request_type

    def clean(self):
        cleaned_data = super(CustomRequestForm, self).clean()

        if 'client_attachment' in cleaned_data:
            for attachment in self.cleaned_data['client_attachment']:
                if attachment:
                    if not correct_file_type(attachment):
                        self._errors['client_attachment'] = ['File must be PDF, Zip, Microsoft Word File,'
                                                             ' Microsoft Excel File or JPEG.']
        return cleaned_data


    def save(self, *args, **kwargs):
        user = self.request.user
        if len(args) == 0:
            return

        # Checks for extra arguement related to updating Custom Requests
        if len(args) < 3:
            dynamic_request_form = args[0]

            request = CustomRequest(name=self.cleaned_data['name'],
                                    request_type=self.cleaned_data['request_type'],
                                    dynamic_request_form=dynamic_request_form,
                                    created_by=get_company_employee(user),
                                    comments=self.cleaned_data['comments']
                                    )

            request.save()
            request.display_id = CustomRequest.generate_display_id(request)
            request.save()

            fields = args[1]
            for field in fields:
                value = self.cleaned_data['custom_%s' % field.id]
                CustomRequestFields(custom_request=request, form_field=field, value=value).save()
                if str(field.type) == "Email":
                    request.email = value
            request.save()

            if "client_attachment" in self.cleaned_data:
                ClientAttachmentCustom.objects.filter(request=request).delete()


            for attachment in self.cleaned_data['client_attachment']:
                custom_attachment = ClientAttachmentCustom(created_by=request.created_by, request=request,
                                                           attachment=attachment).save()

                if not request.client_attachment:
                    company_name = request.created_by.company.name.lower()
                    attachment_url = "uploads/{}/{}".format(company_name, attachment.name)
                    request.client_attachment = attachment_url
                    request.save()

            return request
        else:
            custom_request = args[0]
            custom_request.name = self.cleaned_data['name']
            custom_request.request_type = self.cleaned_data['request_type']
            custom_request.comments=self.cleaned_data['comments']
            if len(self.cleaned_data['client_attachment']) > 0:
                ClientAttachmentCustom.objects.filter(request=custom_request).delete()
            for attachment in self.cleaned_data['client_attachment']:
                custom_attachment = ClientAttachmentCustom(created_by=custom_request.created_by, request=custom_request,
                                                           attachment=attachment).save()

                if not custom_request.client_attachment:
                    company_name = custom_request.created_by.company.name.lower()
                    attachment_url = "uploads/{}/{}".format(company_name, attachment.name)
                    custom_request.client_attachment = attachment_url
            custom_request.display_id = CustomRequest.generate_display_id(custom_request)

            fields = args[1]
            for field in fields:
                value = self.cleaned_data['custom_%s' % field.form_field.id]
                field.value = value
                field.save()
                if str(field.form_field.type) == "Email":
                    custom_request.email = value
            custom_request.save()

            return custom_request


class DocumentForm(forms.Form):
    docfile = forms.FileField()
    batch_custom_form_type = forms.CharField()


class EtradeReportingPeriodForm(forms.Form):
    reporting_period = forms.ChoiceField(choices=etrade_reporting_period, required=True)


class SurchargeForm(forms.ModelForm):
    charge_type = forms.ModelChoiceField(required=False, queryset=ChargeType.objects.all(), label="Charge Type")
    ref_number = forms.CharField(required=False, label="Ref Number")
    request_id = forms.CharField(required=False)
    request_type = forms.CharField(required=False)
    estimated_cost = forms.FloatField(required=False)
    notes = forms.CharField(required=False, label="Notes")
    source = forms.CharField(required=False,label="Source")
    order_number = forms.CharField(required=False,label="Order Number")
    processing_fee = forms.CharField(required=False,label="Processing Fee")

    def __init__(self, *args, **kwargs):
        instance = kwargs.pop('instance', None)
        super(SurchargeForm, self).__init__(*args, **kwargs)
        if instance:
            self.fields['charge_type'].initial = instance.charge_type
            self.fields['ref_number'].initial = instance.ref_number
            self.fields['request_id'].initial = instance.request_id
            self.fields['request_type'].initial = instance.request_type
            self.fields['estimated_cost'].initial = instance.estimated_cost
            self.fields['notes'].initial = instance.notes
            self.fields['source'].initial = instance.source
            self.fields['order_number'].initial = instance.order_number
            self.fields['processing_fee'].initial = instance.processing_fee

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Field('ref_number'),
            Field('charge_type'),
            Field('source'),
            Field('order_number'),
            Field(PrependedText('processing_fee', '$')),
            Field(PrependedText('estimated_cost', '$'))
        )

    def clean(self):
        cleaned_data = super(SurchargeForm, self).clean()
        charge_type = cleaned_data.get("charge_type")
        ref_number = cleaned_data.get("ref_number")
        estimated_cost = cleaned_data.get("estimated_cost")
        source = cleaned_data.get('source')
        order_number = cleaned_data.get('order_number')
        processing_fee = cleaned_data.get('processing_fee')


        if not charge_type or not ref_number or not source or not order_number or not processing_fee or not estimated_cost:
            raise forms.ValidationError('All Fields Required')

        return cleaned_data

    class Meta:
        model = Surcharge
        widgets = {'request_id': forms.HiddenInput(),'request_type': forms.HiddenInput()}
        fields = ['ref_number', 'charge_type', 'estimated_cost', 'request_id', 'request_type','source','order_number','processing_fee']
