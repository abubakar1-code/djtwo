from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.conf import settings
from localflavor.us.models import USStateField
from django_countries.fields import CountryField
from django.template.defaultfilters import default, slugify
from django.core.exceptions import ValidationError
from django.utils import timezone
from encrypted_fields import EncryptedTextField
from itertools import chain
from os.path import splitext
import os.path
import StringIO, re, datetime
import pytz
from time import strftime
import xlrd


SPOTLIT_MANAGER_GROUP = "SpotLitManager"
SPOTLIT_ANALYST_GROUP = "SpotLitAnalyst"
REVIEWER = "Reviewer"
COMPANY_EMPLOYEE_GROUP = "CompanyEmployee"
REGISTERED_CUSTOMER_GROUP = "RegisteredCustomer"
UNVERIFIED_USER_GROUP = "UnverifiedUser"

PROJECT_PATH = os.path.abspath(os.path.dirname(__name__))


def request_content_file_name(instance, filename):
    return '/'.join(
        ['uploads', fix_company_name(instance.created_by.company.name), fix_file_name(filename)])

#def request_content_file_name(instance, filename):
#    return '/'.join(
#        ['uploads', fix_file_name(filename)])


def logo_file_name(instance, filename):
    return '/'.join(['logos', fix_company_name(instance.name), fix_file_name(filename)])


def report_logo_file_name(instance, filename):
    return '/'.join(['report_logos', fix_company_name(instance.name), fix_file_name(filename)])


def pdf_custom_report_file_name(request, filename):
    """
    :param request: A Custom Request
    :return: a string path to store report PDFs like /reports/company_name/display_id
    """
    return '/'.join(['reports', 'custom', fix_company_name(request.created_by.company.name), fix_file_name(filename)])


def pdf_corporate_report_file_name(request, filename):
    """
    :param request: A Corporate Request
    :return: a string path to store report PDFs like /reports/company_name/display_id
    """
    return '/'.join(['reports', 'custom', fix_company_name(request.created_by.company.name), fix_file_name(filename)])


def pdf_report_file_name(request, filename):
    """
    :param request: A Individual Request
    :return: a string path to store report PDFs like /reports/company_name/display_id
    """
    return '/'.join(['reports', 'custom', fix_company_name(request.created_by.company.name), fix_file_name(filename)])




def zip_archive_file_name(instance, filename):
    return '/'.join(['archives', fix_company_name(instance.created_by.company.name), fix_file_name(filename)])



def fix_company_name(company):
    company = slugify(company)
    return company


def fix_file_name(filename):
    name, extension = splitext(filename)
    new_file_name = slugify(name) + extension
    return new_file_name

class BaseRequestStatus(models.Model):
    NEW_STATUS = 1
    ASSIGNED_STATUS = 2
    IN_PROGRESS_STATUS = 3
    COMPLETED_STATUS = 4
    SUBMITTED_STATUS = 5
    REJECTED_STATUS = 6
    INCOMPLETE_STATUS = 7
    NEW_RETURNED_STATUS = 8
    DELETED_STATUS = 9
    REVIEW_STATUS = 0
    AWAITING_DATA_FORM_APPROVAL=10
    ARCHIVED_STATUS=11

    REQUEST_STATUS_CHOICES = (
        (REVIEW_STATUS, 'In Review'),
        (NEW_STATUS, 'New'),
        (ASSIGNED_STATUS, 'Assigned'),
        (IN_PROGRESS_STATUS, 'In Progress'),
        (COMPLETED_STATUS, 'Completed'),
        (SUBMITTED_STATUS, 'Submitted'),
        (REJECTED_STATUS, 'Rejected'),
        (INCOMPLETE_STATUS, 'Incomplete'),
        (NEW_RETURNED_STATUS, 'New Returned'),
        (DELETED_STATUS, 'Deleted'),
        (AWAITING_DATA_FORM_APPROVAL,"Data Form"),
        (ARCHIVED_STATUS, 'Archived')
    )

    SUPERVISOR_REQUEST_STATUS_CHOICES = (
        (IN_PROGRESS_STATUS, 'In Progress'),
        (SUBMITTED_STATUS, 'Completed'),
        (INCOMPLETE_STATUS, 'Incomplete'),
        (DELETED_STATUS, 'Deleted'),
        (ARCHIVED_STATUS, 'Archived')
    )

    MANAGER_STATUS_CHOICES = {
        NEW_STATUS: 'New',
        ASSIGNED_STATUS: 'Assigned',
        IN_PROGRESS_STATUS: 'In Progress',
        COMPLETED_STATUS: 'Completed',
        SUBMITTED_STATUS: 'Submitted',
        REJECTED_STATUS: 'Rejected',
        INCOMPLETE_STATUS: 'Incomplete',
        NEW_RETURNED_STATUS: 'New Returned',
        DELETED_STATUS: 'Deleted',
        REVIEW_STATUS: 'In Review',
        AWAITING_DATA_FORM_APPROVAL: 'Data Form',
        ARCHIVED_STATUS: 'Archived'
    }

    EMPLOYEE_STATUS_CHOICES = {
        NEW_STATUS: 'In Progress',
        ASSIGNED_STATUS: 'In Progress',
        IN_PROGRESS_STATUS: 'In Progress',
        COMPLETED_STATUS: 'In Progress',
        SUBMITTED_STATUS: 'Completed',
        REJECTED_STATUS: 'In Progress',
        INCOMPLETE_STATUS: 'Incomplete',
        NEW_RETURNED_STATUS: 'In Progress',
        DELETED_STATUS: 'Deleted',
        REVIEW_STATUS: 'In Progress',
        AWAITING_DATA_FORM_APPROVAL: 'Data Form',
        ARCHIVED_STATUS: 'Archived'
    }

    SUPERVISOR_STATUS_CHOICES = {
        NEW_STATUS: 'In Progress',
        ASSIGNED_STATUS: 'In Progress',
        IN_PROGRESS_STATUS: 'In Progress',
        COMPLETED_STATUS: 'In Progress',
        SUBMITTED_STATUS: 'Completed',
        REJECTED_STATUS: 'In Progress',
        INCOMPLETE_STATUS: 'Incomplete',
        NEW_RETURNED_STATUS: 'In Progress',
        DELETED_STATUS: 'Deleted',
        REVIEW_STATUS: 'In Progress',
        AWAITING_DATA_FORM_APPROVAL: 'Data Form',
        ARCHIVED_STATUS: 'Archived'
    }

    ANALYST_STATUS_CHOICES = {
        ASSIGNED_STATUS: 'New',
        IN_PROGRESS_STATUS: 'In Progress',
        COMPLETED_STATUS: 'Completed',
        SUBMITTED_STATUS: 'Submitted',
        REJECTED_STATUS: 'Rejected',
        INCOMPLETE_STATUS: 'Incomplete',
        NEW_RETURNED_STATUS: 'New Returned',
        DELETED_STATUS: 'Deleted',
        REVIEW_STATUS: 'In Review',
        AWAITING_DATA_FORM_APPROVAL: 'Data Form',
        ARCHIVED_STATUS: 'Archived'
    }

    REVIEWER_STATUS_CHOICES = {
        NEW_STATUS: 'New',
        ASSIGNED_STATUS: 'Assigned',
        IN_PROGRESS_STATUS: 'In Progress',
        COMPLETED_STATUS: 'Completed',
        SUBMITTED_STATUS: 'Submitted',
        REJECTED_STATUS: 'Rejected',
        INCOMPLETE_STATUS: 'Incomplete',
        NEW_RETURNED_STATUS: 'New Returned',
        DELETED_STATUS: 'Deleted',
        REVIEW_STATUS: 'In Review',
        AWAITING_DATA_FORM_APPROVAL: 'Data Form',
        ARCHIVED_STATUS: 'Archived'
    }

    status = models.IntegerField(choices=REQUEST_STATUS_CHOICES, default=NEW_STATUS)
    datetime = models.DateTimeField("Date", db_index=True)
    comments = models.TextField()

    class Meta:
        abstract = True
        ordering = ['-datetime']
        verbose_name_plural = 'Base Request Statuses'


class Status(BaseRequestStatus):
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    @classmethod
    def get_all_current_ids_queryset_for_company(self, company):
        ind_statuses = Status.objects.filter(request__created_by__company__name=company)\
            .order_by('request__id', '-datetime').distinct(
            'request__id').values_list('id', flat=True)

        corp_statuses = Status.objects.filter(corporate_request__created_by__company__name=company)\
            .order_by('corporate_request__id', '-datetime').distinct(
            'corporate_request__id').values_list('id', flat=True)

        cust_statuses = Status.objects.filter(custom_request__created_by__company__name=company)\
            .order_by('custom_request__id', '-datetime').distinct(
            'custom_request__id').values_list('id', flat=True)
        statuses = list(chain(ind_statuses, corp_statuses, cust_statuses))
        return statuses

    @classmethod
    def get_all_request_by_statuses_for_company(self, status, company):
        statuses = []
        ids = list(Status.get_all_current_ids_queryset_for_company(company))
        try:
            all_statuses = Status.objects.filter(id__in=ids)
            if all_statuses:
                statuses = all_statuses.filter(status__in=status)
        except Status.DoesNotExist:
            statuses = []
        return statuses

    @classmethod
    def get_all_current_ids_queryset_for_user(self, current_user):

        request_ids = Status.objects.filter(
            request__created_by__user=current_user).order_by(
            'request__id', '-datetime').distinct('request__id').values_list('id', flat=True)

        custom_request_ids = Status.objects.filter(
            custom_request__created_by__user=current_user).order_by(
            'custom_request__id', '-datetime').distinct('custom_request__id').values_list('id', flat=True)

        corp_request_ids = Status.objects.filter(corporate_request__created_by__user=current_user).order_by(
            'corporate_request__id', '-datetime').distinct('corporate_request__id').values_list('id', flat=True)

        statuses = list(chain(request_ids, custom_request_ids, corp_request_ids))

        return statuses

    @classmethod
    def get_all_current_ids_queryset_for_reviewer(self, current_user):

        request_ids = Status.objects.filter(
            request__reviewer__user=current_user).order_by(
            'request__id', '-datetime').distinct('request__id').values_list('id', flat=True)

        custom_request_ids = Status.objects.filter(
            custom_request__reviewer__user=current_user).order_by(
            'custom_request__id', '-datetime').distinct('custom_request__id').values_list('id', flat=True)

        corp_request_ids = Status.objects.filter(
                corporate_request__reviewer__user=current_user).order_by(
            'corporate_request__id', '-datetime').distinct('corporate_request__id').values_list('id', flat=True)

        statuses = list(chain(request_ids, custom_request_ids, corp_request_ids))

        return statuses

    @classmethod
    def get_all_current_ids_queryset(self):
        ind_statuses = Status.objects.filter(
            corporate_request__id__isnull=True, custom_request__id__isnull=True).order_by(
            'request__id', '-datetime').distinct('request__id').values_list('id', flat=True)

        corp_statuses = Status.objects.filter(request__id__isnull=True, custom_request__id__isnull=True).order_by(
            'corporate_request__id', '-datetime').distinct('corporate_request__id').values_list('id', flat=True)

        cust_statuses = Status.objects.filter(request__id__isnull=True, corporate_request__id__isnull=True).order_by(
            'custom_request__id', '-datetime').distinct('custom_request__id').values_list('id', flat=True)

        statuses = list(chain(ind_statuses, corp_statuses, cust_statuses))

        return statuses

    @classmethod
    def get_request_status_for_group(self, group, status):
        return_status = ""
        if (group):
            if (group.name == SPOTLIT_MANAGER_GROUP and status in self.MANAGER_STATUS_CHOICES):
                return_status = self.MANAGER_STATUS_CHOICES[status]
            elif (group.name == SPOTLIT_ANALYST_GROUP and status in self.ANALYST_STATUS_CHOICES):
                return_status = self.ANALYST_STATUS_CHOICES[status]
            elif (group.name == COMPANY_EMPLOYEE_GROUP and status in self.EMPLOYEE_STATUS_CHOICES):
                return_status = self.EMPLOYEE_STATUS_CHOICES[status]
            elif(group.name == REVIEWER and status in self.REVIEWER_STATUS_CHOICES):
                return_status = self.REVIEWER_STATUS_CHOICES[status]
        return return_status

    @classmethod
    def get_all_requests_by_status(self, status):
        statuses = []
        ids = list(Status.get_all_current_ids_queryset())
        try:
            all_statuses = Status.objects.filter(id__in=ids)
            if all_statuses:
                statuses = all_statuses.filter(status=status)
        except Status.DoesNotExist:
            statuses = []
        return statuses

    @classmethod
    def get_num_completed_requests_x_days_for_manager(self, days):
        end_date = datetime.datetime.now()
        start_date = end_date - datetime.timedelta(days=days)
        ids = list(Status.get_all_current_ids_queryset())
        all_statuses = Status.objects.filter(id__in=ids)
        completed_in_x_days = all_statuses.filter(status=Status.COMPLETED_STATUS).filter(
            datetime__range=[start_date, end_date]).count()
        print "Start Date = ", start_date
        print "End Date = ", end_date
        return completed_in_x_days

    @classmethod
    def get_num_rejected_requests_x_days_for_manager(self, days):
        end_date = datetime.datetime.now()
        start_date = end_date - datetime.timedelta(days=days)
        ids = list(Status.get_all_current_ids_queryset())
        all_statuses = Status.objects.filter(id__in=ids)
        rejected_in_x_days = all_statuses.filter(status=Status.REJECTED_STATUS).filter(
            datetime__range=[start_date, end_date]).count()
        return rejected_in_x_days

    @classmethod
    def get_num_new_requests_x_days_for_manager(self, days):
        end_date = datetime.datetime.now()
        start_date = end_date - datetime.timedelta(days=days)
        ids = list(Status.get_all_current_ids_queryset())
        all_statuses = Status.objects.filter(id__in=ids)
        completed_in_x_days = all_statuses.filter(status=Status.NEW_STATUS).filter(
            datetime__range=[start_date, end_date]).count()
        return completed_in_x_days

    @classmethod
    def get_all_current_ids_queryset_for_analyst(self, current_user):
        ind_statuses = Status.objects.filter(
            request__assignment__user=current_user).order_by('request__id', '-datetime').distinct(
            'request__id').values_list('id', flat=True)

        cust_statuses = Status.objects.filter(
            custom_request__assignment__user=current_user).order_by('custom_request__id', '-datetime').distinct(
            'custom_request__id').values_list('id', flat=True)

        corp_statuses = Status.objects.filter(
            corporate_request__assignment__user=current_user).order_by('corporate_request__id', '-datetime').distinct(
            'corporate_request__id').values_list('id', flat=True)
        statuses = list(chain(ind_statuses, cust_statuses, corp_statuses))
        return statuses

    @classmethod
    def get_all_requests_by_statuses_for_analyst(self, statuses, current_user):
        return_statuses = []
        ids = list(Status.get_all_current_ids_queryset_for_analyst(current_user))
        try:
            all_statuses = Status.objects.filter(id__in=ids)
            if all_statuses:
                return_statuses = all_statuses.filter(status__in=statuses)
        except Status.DoesNotExist:
            statuses = []
        return return_statuses

    @classmethod
    def add_request_status(self, request, status, comments):
        request_status = None
        if request is not None and status is not None and status in dict(Status.REQUEST_STATUS_CHOICES):
            if comments is None:
                comments = ""
            request_status = Status(content_object=request, status=status, comments=comments,
                                           datetime=datetime.datetime.now())
            request_status.save()
        return request_status

    @classmethod
    def get_statuses_for_reviewer_by_status(self, statuses, user):
        ids = self.get_all_current_ids_queryset_for_reviewer(user)
        review_statuses = Status.objects.filter(id__in=ids, status__in=statuses)
        return review_statuses

    @classmethod
    def get_num_in_progess_statuses(self):
        ids = list(Status.get_all_current_ids_queryset())

        statuses = Status.objects.filter(id__in=ids, status__in=[Status.IN_PROGRESS_STATUS, Status.ASSIGNED_STATUS,
                                                         Status.NEW_RETURNED_STATUS, Status.REVIEW_STATUS])

        return statuses.count()

    def __unicode__(self):
        return "%s: %s %s %s %s" % (
            self.id, self.content_type, self.object_id, self.status, self.datetime)

    class Meta:
        verbose_name_plural = 'Statuses'
        db_table = "core_status"
        ordering = ['-datetime']

class BaseRequestDetailStatus(models.Model):
    INITIAL_DB_CHECK_IN_PROGRESS_STATUS=1
    REQUEST_FOR_VALIDATION_IN_PROGRESS_STATUS=2
    PENDING_COURT_RUNNER_STATUS=3
    PENDING_EMPLOYEE_VERIFICATION_STATUS=4
    PENDING_EDUCATION_VERIFICATION_STATUS=5
    FINAL_DB_CHECKS_AND_WRITE_UP_IN_PROGRESS_STATUS=6
    OTHER=7

    REQUEST_DETAIL_STATUS_CHOICES = (
        (INITIAL_DB_CHECK_IN_PROGRESS_STATUS,"Inital database checks in-progress"),
        (REQUEST_FOR_VALIDATION_IN_PROGRESS_STATUS,"Request for verification in-progress"),
        (PENDING_COURT_RUNNER_STATUS,"Pending Court Runner(s)"),
        (PENDING_EMPLOYEE_VERIFICATION_STATUS,"Pending Employment Verification(s)"),
        (PENDING_EDUCATION_VERIFICATION_STATUS,"Pending Education Verification(s)"),
        (FINAL_DB_CHECKS_AND_WRITE_UP_IN_PROGRESS_STATUS,"Final database checks and write-up in-progress"),
        (OTHER,"Other")
    )

    status = models.IntegerField(choices=REQUEST_DETAIL_STATUS_CHOICES, default=INITIAL_DB_CHECK_IN_PROGRESS_STATUS)
    datetime = models.DateTimeField("Date", db_index=True)
    reason=models.TextField(blank=True,null=True)

    def __unicode__(self):
        return "request: %s, status: %s, reason: %s" % (
            self.request, self.status,self.reason)

    class Meta:
        abstract = True
        ordering = ['-datetime']
        verbose_name_plural = 'Base Request Detail Statuses'

class RequestDetailStatus(BaseRequestDetailStatus):
    request=models.ForeignKey('Request')

    class Meta:
        verbose_name_plural = 'Request Detail Statuses'
        db_table = "core_requestdetailstatus"
        ordering = ['-datetime']

class CorporateRequestDetailStatus(BaseRequestDetailStatus):
    request=models.ForeignKey('CorporateRequest')

    class Meta:
        verbose_name_plural = 'Corporate Request Detail Statuses'
        db_table = "core_corporaterequestdetailstatus"
        ordering = ['-datetime']


class CustomRequestDetailStatus(BaseRequestDetailStatus):
    request=models.ForeignKey('CustomRequest')

    class Meta:
        verbose_name_plural = 'Custom Request Detail Statuses'
        db_table = "core_customrequestdetailstatus"
        ordering = ['-datetime']


class Reports(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False)
    created_by = models.ForeignKey("CompanyEmployee")
    data = models.TextField(blank=False)
    created_date = models.DateTimeField(editable=False)
    report_request_type = models.CharField(max_length=50, null=False, blank=False)
    report_template = models.CharField(max_length=100, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.id:
            self.created_date = datetime.datetime.now(pytz.timezone('US/Eastern'))

        return super(Reports, self).save(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'Reports'


class Request(models.Model):
    display_id = models.CharField(max_length=50, default="")
    first_name = models.CharField(max_length=50, db_index=True)
    middle_name = models.CharField(max_length=50, db_index=True, blank=True)
    last_name = models.CharField(max_length=50, db_index=True, blank=True)
    citizenship = CountryField('Citizenship', null=True, blank=True)
    ssn = EncryptedTextField(blank=True)
    birthdate = models.DateField("Birthdate", null=True, blank=True)
    phone_number = models.CharField(max_length=15, default="", blank=True)
    email = models.CharField("Email", default="", max_length=50, blank=True)
    assignment = models.ForeignKey("SpotLitStaff", default=None, null=True, blank=True)
    reviewer = models.ForeignKey("SpotLitStaff", default=None, null=True, blank=True, related_name='reviewer')
    request_type = models.ForeignKey("CompanyDueDiligenceTypeSelection")
    created_by = models.ForeignKey("CompanyEmployee")
    comments = models.TextField(blank=True)
    address = models.ForeignKey("Address", blank=True, default=None, null=True)
    client_attachment = models.FileField(max_length=200, upload_to=request_content_file_name, default=None, blank=True,
                                         null=True)
    attachment = models.FileField(max_length=200, upload_to=request_content_file_name, default=None, blank=True, null=True)
    executive_summary = models.TextField(default="", blank=True)
    annual_income_exceeds_75000 = models.BooleanField(default=False)
    pending = models.BooleanField(default=False)

    in_progress_status = models.ForeignKey("Status", default=None, blank=True, null=True, related_name='+')
    completed_status = models.ForeignKey("Status", default=None, blank=True, null=True, related_name='+')
    submitted_status = models.ForeignKey("Status", default=None, null=True, blank=True, related_name='+')
    statuses = GenericRelation(Status, related_query_name='request')
    pdf_report = models.FileField(upload_to=pdf_report_file_name, default=None, blank=True, null=True)

    analyst_notes = models.TextField(default="", blank=True)
    reassigned_analyst_notes = models.TextField(default="", blank=True,null=True)
    reassigned_reviewer_notes = models.TextField(default="", blank=True,null=True)
    state_of_employment = USStateField(default=None,null=True, blank=True)

    analyst_internal_doc = models.FileField(max_length=200, upload_to=request_content_file_name, default=None, blank=True,
                                         null=True)

    due_date = models.DateField(null=True, blank=True)


    def __unicode__(self):
        return '%s: %s, %s %s' % (self.id, self.last_name, self.first_name, self.request_type)

    def get_report_url(self):
        date = datetime.datetime.now().strftime("%Y-%m-%d")
        return "%s_%s_%s" % (slugify(self.created_by.company.name), date, self.display_id)

    report_url = property(get_report_url)

    def delete_unrelated_services_after_update(request):
        request_type = request.request_type
        service_selection_allowed = CompanyServiceSelection.objects.filter(dd_type=request_type)
        services_allowed = [service_selection.service for service_selection in service_selection_allowed]
        services_saved = RequestServiceStatus.objects.filter(request=request)

        for request_service_status in services_saved:
            if (request_service_status.service.service not in services_allowed):
                request_service_status.delete()

    def get_request_status(self):
        request_status = None
        status = None
        try:
            request_status = Status.objects.filter(request=self).order_by('-datetime').first()
        except Status.DoesNotExist:
            request_status = None
        if request_status:
            status = request_status.status
        return status

    def get_in_progress_request_status(self):
        request_status = None
        status = None
        try:
            request_status = \
                Status.objects.filter(request=self, status=Status.IN_PROGRESS_STATUS).order_by('id').first()
        except Status.DoesNotExist:
            request_status = None
        return request_status

    def get_complete_request_status(self):
        request_status = None
        status = None
        try:
            request_status = \
                Status.objects.filter(request=self, status=Status.COMPLETED_STATUS).order_by('id').last()
        except Status.DoesNotExist:
            request_status = None
        return request_status

    def get_batch_pdf_name(self):
        try:
            id = self.display_id
            first = self.first_name.upper()
            last = self.last_name.upper()
            return u'{} {}, {}.pdf'.format(id,last,first)
        except:
            return self.display_id + '.pdf'

    @classmethod
    def get_requests_for_analyst(self, current_user):
        requests = []
        analyst = None
        try:
            analyst = SpotLitStaff.objects.get(user=current_user)
        except SpotLitStaff.DoesNotExist:
            analyst = None
        if (analyst):
            assignments = Request.objects.filter(assignment=analyst)
            requests = [request for request in assignments]
        return requests

    @classmethod
    def generate_display_id(self, request):
        id_str = str(request.id)
        if (len(id_str) < 4):
            id_str = id_str.zfill(4)

        due_diligence_type = request.request_type.due_diligence_type.name
        if (due_diligence_type == "Pre-Employment"):
            id_str = "HR-" + id_str
        elif (due_diligence_type == "Third Party"):
            id_str = "TP-" + id_str
        elif (due_diligence_type == "Background Investigations"):
            id_str = "FSBI-" + id_str
        elif (due_diligence_type == "Know Your Customer"):
            id_str = "GI-" + id_str

        return id_str

    class Meta:
        verbose_name_plural = 'Requests'


class ClientAttachment(models.Model):
    created_by = models.ForeignKey("CompanyEmployee")
    attachment = models.FileField(upload_to=request_content_file_name)
    request = models.ForeignKey(Request, related_name='attachments')


class CorporateRequest(models.Model):
    request_type = models.ForeignKey("CompanyDueDiligenceTypeSelection")
    company_name = models.CharField(max_length=50, blank=False)
    duns = models.CharField(max_length=200, blank=True)
    registration = models.CharField(max_length=50, blank=True)
    website = models.URLField(blank=True)
    name_variant = models.CharField(max_length=50, blank=True)
    parent_company_name = models.CharField(max_length=50, blank=True)
    recipient = models.CharField(max_length=50, blank=True, default='')
    street = models.CharField(max_length=200, blank=True, null=True)
    dependent_locality = models.CharField(max_length=200, blank=True, null=True)
    locality = models.CharField(max_length=200, blank=True, null=True)
    postalcode = models.CharField(max_length=15, blank=True, null=True)
    country = CountryField(null=True, blank=True)
    display_id = models.CharField(max_length=50, default="")
    phone_number = models.CharField(max_length=15, default="", blank=True)
    email = models.CharField("Email", default="", max_length=50, blank=True)
    created_by = models.ForeignKey("CompanyEmployee")
    assignment = models.ForeignKey("SpotLitStaff", default=None, null=True, blank=True)
    reviewer = models.ForeignKey("SpotLitStaff", default=None, null=True, blank=True, related_name='corporate_reviewer')
    comments = models.TextField(blank=True)
    client_attachment = models.FileField(max_length=200, upload_to=request_content_file_name, default=None, blank=True,
                                         null=True)
    attachment = models.FileField(max_length=200, upload_to=request_content_file_name, default=None, blank=True,
                                  null=True)
    executive_summary = models.TextField(default="", blank=True)
    in_progress_status = models.ForeignKey("Status", default=None, blank=True, null=True, related_name='+')
    completed_status = models.ForeignKey("Status", default=None, blank=True, null=True, related_name='+')
    submitted_status = models.ForeignKey("Status", default=None, null=True, blank=True, related_name='+')
    statuses = GenericRelation(Status, related_query_name='corporate_request')
    pdf_report = models.FileField(upload_to=pdf_corporate_report_file_name, default=None, blank=True, null=True)

    analyst_notes = models.TextField(default="", blank=True)
    reassigned_analyst_notes = models.TextField(default="", blank=True,null=True)
    reassigned_reviewer_notes = models.TextField(default="", blank=True,null=True)

    analyst_internal_doc = models.FileField(max_length=200, upload_to=request_content_file_name, default=None, blank=True,
                                         null=True)

    due_date = models.DateField(null=True, blank=True)


    def __unicode__(self):
        return '%s: %s' % (self.id, self.company_name)

    def get_report_url(self):
        date = datetime.datetime.now().strftime("%Y-%m-%d")
        return "%s_%s_%s" % (slugify(self.company_name), date, self.display_id)

    report_url = property(get_report_url)

    def delete_unrelated_services_after_update(request):
        request_type = request.request_type
        service_selection_allowed = CompanyServiceSelection.objects.filter(dd_type=request_type)
        services_allowed = [service_selection.service for service_selection in service_selection_allowed]
        services_saved = CorporateRequestServiceStatus.objects.filter(request=request)

        for request_service_status in services_saved:
            if (request_service_status.service.service not in services_allowed):
                CompanyServiceSelection.get_service_selections_for_company.request_service_status.delete()

    def get_request_status(self):
        request_status = None
        status = None
        try:
            request_status = Status.objects.filter(corporate_request=self).order_by('-datetime').first()
        except Status.DoesNotExist:
            request_status = None
        if request_status:
            status = request_status.status
        return status

    def get_batch_pdf_name(self):
        try:
            id = self.display_id
            name = self.company_name.upper()
            return u'{} {}.pdf'.format(id,name)
        except:
            return self.display_id + '.pdf'

    @classmethod
    def get_requests_for_analyst(self, current_user):
        requests = []
        analyst = None
        try:
            analyst = SpotLitStaff.objects.get(user=current_user)
        except SpotLitStaff.DoesNotExist:
            analyst = None
        if (analyst):
            assignments = CorporateRequest.objects.filter(assignment=analyst)
            requests = [request for request in assignments]
        return requests

    @classmethod
    def generate_display_id(self, request):
        id_str = str(request.id)
        if (len(id_str) < 4):
            id_str = id_str.zfill(4)

        due_diligence_type = request.request_type.due_diligence_type.name
        if (due_diligence_type == "Pre-Employment"):
            id_str = "HR-" + id_str
        elif (due_diligence_type == "Third Party"):
            id_str = "TP-" + id_str
        elif (due_diligence_type == "Background Investigations"):
            id_str = "FSBI-" + id_str
        elif (due_diligence_type == "Know Your Customer"):
            id_str = "GI-" + id_str

        return id_str


    def get_in_progress_request_status(self):
        request_status = None
        status = None
        try:
            request_status = \
                Status.objects.filter(corporate_request=self, status=Status.IN_PROGRESS_STATUS).order_by('id').first()
        except Status.DoesNotExist:
            request_status = None
        return request_status

    def get_complete_request_status(self):
        request_status = None
        status = None
        try:
            request_status = \
                Status.objects.filter(corporate_request=self, status=Status.COMPLETED_STATUS).order_by('id').last()
        except Status.DoesNotExist:
            request_status = None
        return request_status


class ClientAttachmentCorporate(models.Model):
    created_by = models.ForeignKey("CompanyEmployee")
    attachment = models.FileField(upload_to=request_content_file_name)
    request = models.ForeignKey(CorporateRequest, related_name='attachments')


class BaseRequestServiceStatus(models.Model):
    service = models.ForeignKey('CompanyServiceSelection')
    results = models.BooleanField(blank=True)
    comments = models.TextField()
    datetime = models.DateField(blank=True)

    def __unicode__(self):
        return "request: %s, service: %s, results: %s, comments: %s" % (
            self.request, self.service, self.results, self.comments)


    class Meta:
        abstract = True



class RequestServiceStatus(BaseRequestServiceStatus):
    request = models.ForeignKey('Request')

    @classmethod
    def save_request_service_status(self, request, service, results, comments):
        results_boolean = results == 'True'
        try:
            request_service_status = RequestServiceStatus.objects.filter(request=request).filter(
                service=service).first()
            request_service_status.request = request
            request_service_status.service = service
            request_service_status.results = results_boolean
            request_service_status.comments = comments
            request_service_status.datetime = datetime.datetime.now()
        except Exception, e:
            request_service_status = RequestServiceStatus(request=request, service=service, results=results_boolean,
                                                          comments=comments, datetime=datetime.datetime.now())
        if request_service_status:
            request_service_status.save()
        return request_service_status

    class Meta:
        db_table = 'core_requestservicestatus'
        verbose_name_plural = 'Request Service Statuses'


class CorporateRequestServiceStatus(BaseRequestServiceStatus):
    request = models.ForeignKey('CorporateRequest')

    @classmethod
    def save_request_service_status(self, request, service, results, comments):
        results_boolean = results == 'True'
        try:
            request_service_status = CorporateRequestServiceStatus.objects.filter(request=request).filter(
                service=service).first()
            request_service_status.request = request
            request_service_status.service = service
            request_service_status.results = results_boolean
            request_service_status.comments = comments
            request_service_status.datetime = datetime.datetime.now()
        except Exception, e:
            request_service_status = CorporateRequestServiceStatus(request=request, service=service,
                                                                   results=results_boolean, comments=comments,
                                                                   datetime=datetime.datetime.now())
        if request_service_status:
            request_service_status.save()
        return request_service_status

    class Meta:
        db_table = 'core_corporaterequestservicestatus'
        verbose_name_plural = 'Corporate Request Service Statuses'


class CustomRequestServiceStatus(BaseRequestServiceStatus):
    request = models.ForeignKey('CustomRequest')

    @classmethod
    def save_request_service_status(self, request, service, results, comments):
        results_boolean = results == 'True'
        try:
            request_service_status = CustomRequestServiceStatus.objects.filter(request=request).filter(
                service=service).first()
            request_service_status.request = request
            request_service_status.service = service
            request_service_status.results = results_boolean
            request_service_status.comments = comments
            request_service_status.datetime = datetime.datetime.now()
        except Exception, e:
            request_service_status = CustomRequestServiceStatus(request=request, service=service,
                                                                   results=results_boolean, comments=comments,
                                                                   datetime=datetime.datetime.now())
        if request_service_status:
            request_service_status.save()
            print CustomRequestServiceStatus.objects.get(id=request_service_status.id)
        return request_service_status

    class Meta:
        db_table = 'core_customrequestservicestatus'
        verbose_name_plural = 'Custom Request Service Statuses'


class Company(models.Model):
    name = models.CharField(max_length=50, db_index=True)
    address = models.ForeignKey('Address', blank=True, default=None, null=True)
    phone_number = models.CharField(max_length=15, blank=True, default=None, null=True)
    tax_id = models.CharField(max_length=50, blank=True, default=None, null=True)
    logo = models.ImageField(upload_to=logo_file_name, default=None, blank=True, null=True)
    report_logo = models.ImageField(upload_to=report_logo_file_name, default=None, blank=True, null=True)
    individual_template = models.CharField(max_length=500, null=True, blank=True, default=None)
    corporate_template = models.CharField(max_length=500, null=True, blank=True, default=None)
    is_corporate = models.BooleanField(default=False)
    is_individual = models.BooleanField(default=True)
    is_custom = models.BooleanField(default=False)
    company_logo_active = models.BooleanField(default=False)
    report_logo_active = models.BooleanField(default=False)
    batch_upload_active = models.BooleanField(default=False)
    restrict_attachments = models.BooleanField(default=False)
    terms_agreed = models.BooleanField(default=True)

    def __unicode__(self):
        return "%s" % self.name

    class Meta:
        verbose_name_plural = 'Companies'


class CompanyEmployee(models.Model):
    user = models.OneToOneField(User)
    phone_number = models.CharField(max_length=15, blank=True)
    company = models.ForeignKey('Company')
    position = models.CharField(max_length=50, blank=True)
    is_activated = models.BooleanField(default=False)
    supervisor = models.BooleanField(default=False)

    def __unicode__(self):
        return "%s: %s, %s" % (self.company.name, self.user.last_name, self.user.first_name)

    @classmethod
    def get_company_employee(self, current_user):
        employee = CompanyEmployee.objects.filter(user=current_user).first()
        return employee

    @classmethod
    def get_company_employees(self, company):
        company_employees = CompanyEmployee.objects.filter(company__name=company)
        return company_employees


class SpotLitStaff(models.Model):
    user = models.OneToOneField(User)
    phone_number = models.CharField(max_length=15)
    is_activated = models.BooleanField(default=False)

    def __unicode__(self):
        return "%s, %s" % (self.user.last_name, self.user.first_name)

    def is_analyst(self):
        user_groups = self.user.groups.all()
        analyst_group = filter(lambda group: group.name == SPOTLIT_ANALYST_GROUP, user_groups)
        if (analyst_group):
            return True
        else:
            return False

    def is_manager(self):
        user_groups = self.user.groups.all()
        manager_group = filter(lambda group: group.name == SPOTLIT_MANAGER_GROUP, user_groups)
        if (manager_group):
            return True
        else:
            return False

    def is_reviewer(self):
        user_groups = self.user.groups.all()
        reviewer_group = filter(lambda group: group.name == REVIEWER, user_groups)
        if (reviewer_group):
            return True
        else:
            return False

    @classmethod
    def get_analysts(self,sorted=False):
        analyst_users = User.objects.filter(groups__name=SPOTLIT_ANALYST_GROUP)
        if sorted:
            analysts = SpotLitStaff.objects.filter(user__in=analyst_users).order_by("user__last_name")
        else:
            analysts = SpotLitStaff.objects.filter(user__in=analyst_users)
        return analysts

    @classmethod
    def get_reviewers(self,sorted=False):
        reviewer_users = User.objects.filter(groups__name=REVIEWER)
        if sorted:
            reviewers = SpotLitStaff.objects.filter(user__in=reviewer_users).order_by("user__last_name")
        else:
            reviewers = SpotLitStaff.objects.filter(user__in=reviewer_users)
        return reviewers

    class Meta:
        verbose_name_plural = 'Spotlit Staff'

class DueDiligenceType(models.Model):
    name = models.CharField(max_length=90, db_index=True)

    def natural_key(self):
        return (self.id, self.name)

    def __unicode__(self):
        return "%s" % (self.name)

    class Meta:
        verbose_name_plural = 'Due Diligence Types'

class Service(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField()
    no_info_description = models.TextField(null=True, blank=True)
    display_order = models.IntegerField()

    def __unicode__(self):
        return "%s" % (self.name)


class DueDiligenceTypeServices(models.Model):
    due_diligence_type = models.ForeignKey("DueDiligenceType")
    service = models.ForeignKey("Service")

    def __unicode__(self):
        return "%s %s" % (self.due_diligence_type.name, self.service.name)

    @classmethod
    def get_all_services_for_type(self, type_name):
        service_selections = DueDiligenceTypeServices.objects.filter(due_diligence_type__name=type_name).order_by(
            'service__display_order')
        services = [selection.service for selection in service_selections]
        return services

    class Meta:
        verbose_name_plural = 'Due Diligence Type Services'


class CompanyDueDiligenceTypeSelection(models.Model):
    BASIC_LEVEL = 1
    ENHANCED_LEVEL = 2
    COMPREHENSIVE_LEVEL = 3

    TYPE_LEVEL_CHOICES = (
        (BASIC_LEVEL, 'Essential'),
        (ENHANCED_LEVEL, 'Enhanced'),
        (COMPREHENSIVE_LEVEL, 'Extensive'),
    )

    is_public = models.BooleanField(default=False)
    company = models.ForeignKey('Company',null=True,blank=True,default=None)
    due_diligence_type = models.ForeignKey("DueDiligenceType")
    name = models.CharField(max_length=90)
    comments = models.TextField()
    level = models.IntegerField(choices=TYPE_LEVEL_CHOICES, default=BASIC_LEVEL)
    price = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=True)
    invoice_instructions = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def natural_key(self):
        return (self.id, self.name, self.due_diligence_type.name, self.level)


    def __unicode__(self):
        if self.name:
            return "%s - %s - %s" % (self.due_diligence_type.name, self.get_level_display(), self.name)
        return "%s - %s" % (self.due_diligence_type, self.get_level_display())

    def save(self,*args,**kwargs):
        if self.is_public is True and self.company is not None:
            raise ValidationError('Public Packages cannot have Company field assigned')
        if self.is_public is False and self.company is None:
            raise ValidationError('Company field is required in Private Packages')
        return super(CompanyDueDiligenceTypeSelection, self).save(*args, **kwargs)

    @classmethod
    def get_due_diligence_types_for_current_user(self, current_user):
        types_to_return = []
        employee = CompanyEmployee.get_company_employee(current_user)
        if employee is not None:
            company = employee.company
            types_to_return = CompanyDueDiligenceTypeSelection.objects.filter(company=company, is_active=True)
        return types_to_return

    @classmethod
    def get_public_packages(self):
        return CompanyDueDiligenceTypeSelection.objects.filter(is_public=True)

    @classmethod
    def get_enabled_public_packages(self,company):
        company_disabled_public_packages_ids = list(map(lambda x:x.package.id,CompanyDisabledPackage.objects.filter(company=company)))
        public_packages = CompanyDueDiligenceTypeSelection.objects.filter(is_public=True).exclude(pk__in=company_disabled_public_packages_ids)
        return public_packages

    class Meta:
        verbose_name_plural = 'Company Due Diligencte Type Selections'

class CompanyServiceSelection(models.Model):
    dd_type = models.ForeignKey('CompanyDueDiligenceTypeSelection')
    service = models.ForeignKey("Service")

    def __unicode__(self):
        return "%s %s %s %s" % (
            self.dd_type.name, self.dd_type.company.name if self.dd_type.company is not None else "(Public)", self.dd_type.due_diligence_type.name, self.service.name)


    @classmethod
    def get_service_selections_for_request(self, request_object):
        company = request_object.created_by.company
        request_type = request_object.request_type
        dd_type_selection = CompanyDueDiligenceTypeSelection.objects.get(pk=request_type.pk)
        service_selections = CompanyServiceSelection.objects.filter(dd_type=dd_type_selection).order_by(
            'service__display_order')
        return service_selections

    @classmethod
    def get_service_selections_for_company(self, company):
        dd_type_selections = CompanyDueDiligenceTypeSelection.objects.filter(company=company)
        service_selections = CompanyServiceSelection.objects.filter(dd_type__in=dd_type_selections)
        return service_selections

    @classmethod
    def get_service_selections_for_public_packages(self):
        dd_type_selections = CompanyDueDiligenceTypeSelection.objects.filter(is_public=True)
        service_selections = CompanyServiceSelection.objects.filter(dd_type__in=dd_type_selections)
        return service_selections

    class Meta:
        verbose_name_plural = 'Company Service Selections'

class CompanyDisabledPackage(models.Model):
    company = models.ForeignKey("Company")
    package = models.ForeignKey("CompanyDueDiligenceTypeSelection")

    def __unicode__(self):
        return "%s %s" % (self.company.name, self.package.name)

    class Meta:
        verbose_name_plural = 'Company Disabled Public Packages'

class Address(models.Model):
    street = models.CharField(max_length=50)
    street2 = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    state = USStateField()
    zipcode = models.CharField(max_length=10)

    def __unicode__(self):
        return "%s\n%s\n%s, %s %s" % (self.street, self.street2,
                                      self.city, self.state, self.zipcode)

    def get_short_street(self):
        street = self.street
        if (len(street) > 30):
            street = street[0:29]
        return street

    short_street = property(get_short_street)

    def get_short_street2(self):
        street2 = self.street2
        if (len(street2) > 30):
            street2 = street2[0:29]
        return street2

    short_street2 = property(get_short_street2)

    class Meta:
        verbose_name_plural = 'Adresses'

# -- Dynamic Form Models --
class RequestFormFieldTypes(models.Model):
    TEXT = 'Text'
    LIST = 'List'
    TEXTAREA = 'Text Area'
    EMAIL = 'Email'

    type = models.CharField(max_length=50, unique=True)

    def __unicode__(self):
        return "%s" % self.type

    class Meta:
        verbose_name = "Request Form Field Type"
        verbose_name_plural = "Request Form Field Types"


class LayoutGroupSections(models.Model):
    REQUEST_INFO = 'Request Information'
    CONTACT_INFO = 'Contact Information'

    group_name = models.CharField(max_length=75, unique=True)

    def __unicode__(self):
        return "%s" % self.group_name

    class Meta:
        verbose_name = "Layout Group Section"
        verbose_name_plural = "Layout Group Sections"


class DynamicRequestForm(models.Model):
    company = models.ForeignKey(Company)

    name = models.CharField(max_length=100)
    render_form = models.BooleanField(default=True)

    def __unicode__(self):
        return "%s" % self.name


class DynamicRequestFormFields(models.Model):
    dynamic_request_form = models.ForeignKey(DynamicRequestForm)
    type = models.ForeignKey(RequestFormFieldTypes)
    group = models.ForeignKey(LayoutGroupSections)

    label = models.CharField(max_length=50)
    sort_order = models.IntegerField(default=0)
    help_text = models.CharField(blank=True, max_length=150)
    field_format = models.TextField(blank=True)
    required = models.BooleanField(default=False)
    archive = models.BooleanField(default=False)

    def __unicode__(self):
        return "%s" % (self.label)

    class Meta:
        verbose_name_plural = 'Dynamic Request Form Fields'

# content_type_id = 30
class CustomRequest(models.Model):
    dynamic_request_form = models.ForeignKey(DynamicRequestForm)

    display_id = models.CharField(max_length=50, default="")
    name = models.CharField(max_length=50, db_index=True)
    assignment = models.ForeignKey("SpotLitStaff", default=None, null=True, blank=True)
    reviewer = models.ForeignKey("SpotLitStaff", default=None, null=True, blank=True, related_name="custom_reviewer")
    request_type = models.ForeignKey("CompanyDueDiligenceTypeSelection")
    created_by = models.ForeignKey("CompanyEmployee")
    comments = models.TextField(blank=True)
    client_attachment = models.FileField(max_length=200, upload_to=request_content_file_name, default=None, blank=True,
                                         null=True)
    attachment = models.FileField(max_length=200, upload_to=request_content_file_name, default=None, blank=True,
                                  null=True)
    executive_summary = models.TextField(default="", blank=True)
    statuses = GenericRelation(Status, related_query_name='custom_request')

    in_progress_status = models.ForeignKey("Status", default=None, null=True, blank=True, related_name='+')
    completed_status = models.ForeignKey("Status", default=None, null=True, blank=True, related_name='+')
    submitted_status = models.ForeignKey("Status", default=None, null=True, blank=True, related_name='+')
    pdf_report = models.FileField(upload_to=pdf_custom_report_file_name, default=None, blank=True, null=True)

    analyst_notes = models.TextField(default="", blank=True)
    reassigned_analyst_notes = models.TextField(default="", blank=True,null=True)
    reassigned_reviewer_notes = models.TextField(default="", blank=True,null=True)

    analyst_internal_doc = models.FileField(max_length=200, upload_to=request_content_file_name, default=None, blank=True,
                                         null=True)

    due_date = models.DateField(null=True, blank=True)

    email = models.CharField("Email", default="", max_length=50, blank=True, null=True)


    def __unicode__(self):
        return '%s: %s, %s' % (self.id, self.name, self.request_type)

    def get_report_url(self):
        date = datetime.datetime.now().strftime("%Y-%m-%d")
        return "%s_%s_%s" % (slugify(self.created_by.company.name), date, self.display_id)

    report_url = property(get_report_url)

    def get_in_progress_request_status(self):
        custom_request_status = None
        status = None
        try:
            custom_request_status = \
                Status.objects.filter(custom_request=self, status=Status.IN_PROGRESS_STATUS).order_by('id').first()
        except Status.DoesNotExist:
            custom_request_status = None
        return custom_request_status

    def get_complete_request_status(self):
        custom_request_status = None
        status = None
        try:
            custom_request_status = \
                Status.objects.filter(custom_request=self, status=Status.COMPLETED_STATUS).order_by('id').last()
        except Status.DoesNotExist:
            custom_request_status = None
        return custom_request_status

    def delete_unrelated_services_after_update(request):
        request_type = request.request_type
        service_selection_allowed = CompanyServiceSelection.objects.filter(dd_type=request_type)
        services_allowed = [service_selection.service for service_selection in service_selection_allowed]
        services_saved = CustomRequestServiceStatus.objects.filter(request=request)

        for request_service_status in services_saved:
            if (request_service_status.service.service not in services_allowed):
                request_service_status.delete()

    def get_request_status(self):
        request_status = None
        status = None
        try:
            request_status = Status.objects.filter(custom_request=self).order_by('-datetime').first()
        except Status.DoesNotExist:
            request_status = None
        if request_status:
            status = request_status.status
        return status

    def get_batch_pdf_name(self):
        try:
            id = self.display_id
            name = self.name.upper()
            # names = self.name.split(u' ')
            # if len(names) > 1:
            #     name = u'{}, {}'.format(names[1].upper(),names[0].upper())
            # else:
            #     name = names[0]
            return u'{} {}.pdf'.format(id,name)
        except:
            return self.display_id + '.pdf'

    @classmethod
    def get_requests_for_analyst(self, current_user):
        requests = []
        analyst = None
        try:
            analyst = SpotLitStaff.objects.get(user=current_user)
        except SpotLitStaff.DoesNotExist:
            analyst = None
        if (analyst):
            assignments = CustomRequest.objects.filter(assignment=analyst)
            requests = [request for request in assignments]
        return requests

    @classmethod
    def generate_display_id(self, request):
        id_str = str(request.id)
        if (len(id_str) < 4):
            id_str = id_str.zfill(4)

        # due_diligence_type = request.request_type.due_diligence_type.name
        # if (due_diligence_type == "Pre-Employment"):
        #     id_str = "HR-" + id_str
        # elif (due_diligence_type == "Third Party"):
        #     id_str = "TP-" + id_str
        # elif (due_diligence_type == "Background Investigations"):
        #     id_str = "FSBI-" + id_str
        # elif (due_diligence_type == "Know Your Customer"):
        #     id_str = "GI-" + id_str
        id_str = "CR-" + id_str
        return id_str

    def save(self, *args, **kwargs):
         return super(CustomRequest, self).save(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'Custom Requests'


class ClientAttachmentCustom(models.Model):
    created_by = models.ForeignKey(CompanyEmployee)
    attachment = models.FileField(upload_to=request_content_file_name)
    request = models.ForeignKey(CustomRequest, related_name='attachments')


class CustomRequestFields(models.Model):
    custom_request = models.ForeignKey(CustomRequest)
    form_field = models.ForeignKey(DynamicRequestFormFields)
    value = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = 'Custom Request Fields'


class BatchFile(models.Model):
    # docfile = models.FileField(upload_to='documents/%Y/%m/%d')
    created_by = models.ForeignKey("CompanyEmployee")
    docfile = models.FileField(upload_to=request_content_file_name)


class RequestArchive(models.Model):
    company = models.ForeignKey("Company")
    datetime = models.DateTimeField("Date")
    created_by = models.ForeignKey("CompanyEmployee")
    archive = models.FileField(upload_to=zip_archive_file_name)
    archive_piece = models.CharField(max_length=100, null=False, blank=False, default='Part 1 of 1')
    @classmethod
    def get_company_archives(self, company):
        return RequestArchive.objects.filter(company=company)

    def get_name(self):
        return os.path.basename(self.archive.url)

    def as_json(self):
        return dict(
            company=self.company.name,
            datetime=strftime("%b %d %Y %H:%M:%S", timezone.localtime(self.datetime).timetuple()),
            created_by=self.created_by.user.username,
            archive_url=self.archive.url,
            archive_name=self.get_name(),
            archive_piece=self.archive_piece
        )


class ChargeType(models.Model):
    name = models.CharField(max_length=50, null=False, blank=False)
    description = models.CharField(max_length=250, null=True, blank=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Charge Types'

class Surcharge(models.Model):
    charge_type = models.ForeignKey("ChargeType")
    ref_number = models.CharField(max_length=100, null=True, blank=True)
    request_id = models.CharField(max_length=25, null=False, blank=False)
    request_type = models.CharField(max_length=25, null=False, blank=False)
    estimated_cost = models.DecimalField(decimal_places=2, max_digits=20, null=False, blank=False)
    notes = models.CharField(max_length=250, null=True, blank=True)
    source = models.CharField(max_length=100,null=True,blank=True,default=None)
    order_number = models.CharField(max_length=100,null=True,blank=True,default=None)
    processing_fee = models.CharField(max_length=100,null=True,blank=True,default=None)


    def __unicode__(self):
        return '{} - {}'.format(self.request_id, self.charge_type.name)

    class Meta:
        verbose_name_plural = 'Surcharges'


class RequestSelectedSupervisor(models.Model):
    supervisor = models.ForeignKey("CompanyEmployee")
    request = models.ForeignKey('Request')

class CorporateRequestSelectedSupervisor(models.Model):
    supervisor = models.ForeignKey("CompanyEmployee")
    corporate_request = models.ForeignKey('CorporateRequest')

class CustomRequestSelectedSupervisor(models.Model):
    supervisor = models.ForeignKey("CompanyEmployee")
    custom_request = models.ForeignKey('CustomRequest')