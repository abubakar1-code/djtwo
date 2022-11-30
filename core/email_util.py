from __future__ import absolute_import
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template import loader
from email.MIMEImage import MIMEImage
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes

from .email_async import send_mail, send_mail_xls_attachment


from .models import Request, CorporateRequest, CustomRequest, Status
from .utils import get_user_group

import os

def send_activation_email(request, email, user):
    subject_template_name='Voyint User Activation'
    email_template_name='emails/activate_email.txt'
    use_https=True
    token_generator=default_token_generator
    from_email="Voyint Admin <info@voyint.com>"
    html_email_template_name='emails/activate_email.html'

    current_site = "portal.voyint.com"
    site_name = "core"
    domain = "portal.voyint.com"

    context = {
    'email': user.email,
    'domain': domain,
    'site_name': site_name,
    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
    'user': user,
    'token': token_generator.make_token(user),
    'protocol': 'https' if use_https else 'http',
    }

    send_mail(subject_template_name, email_template_name, from_email, user.email, fail_silently=False, html=html_email_template_name, context =context)

def send_verification_email(request, user):
    subject_template_name='Voyint User Activation'
    email_template_name='emails/account_verification.txt'
    use_https=True
    token_generator=default_token_generator
    from_email="Voyint Admin <info@voyint.com>"
    html_email_template_name='emails/account_verification.html'

    current_site = "portal.voyint.com"
    site_name = "core"
    domain = "portal.voyint.com"

    context = {
    'email': user.email,
    'domain': domain,
    'site_name': site_name,
    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
    'user': user,
    'token': token_generator.make_token(user),
    'protocol': 'https' if use_https else 'http',
    }

    send_mail(subject_template_name, email_template_name, from_email, user.email, fail_silently=False, html=html_email_template_name, context =context)


def send_status_change_email(request, user, status):
    status_for_user = Status.get_request_status_for_group(get_user_group(user), status)
    if hasattr(request,'last_name'):
        subject = "Status change on request " + str(request.last_name) + ", " + str(request.first_name)
    if hasattr(request,'name'):
        subject = "Status change on request, " + str(request.name)
    else:
        subject = "Status change on request, " + str(request.first_name)
    email_template_name='emails/status_change.txt'
    use_https=True
    from_email="Voyint Admin <info@voyint.com>"
    html_email_template_name='emails/status_change.html'

    current_site = "portal.voyint.com"
    site_name = "core"
    domain = "portal.voyint.com"

    context = {
    'email': user.email,
    'domain': domain,
    'site_name': site_name,
    'user': user,
    'protocol': 'https' if use_https else 'http',
    'status_id': status,
    'status': status_for_user,
    'request': request,
    }

    send_mail(subject, email_template_name, from_email, user.email, fail_silently=False, html=html_email_template_name, context =context)

def send_status_change_email_for_corporate(request, user, status):
    status_for_user = Status.get_request_status_for_group(get_user_group(user), status)
    subject = "Status change on request " + str(request.company_name)
    email_template_name='emails/status_change.txt'
    use_https=True
    from_email="Voyint Admin <info@voyint.com>"
    html_email_template_name='emails/status_change.html'

    current_site = "portal.voyint.com"
    site_name = "core"
    domain = "portal.voyint.com"

    context = {
    'email': user.email,
    'domain': domain,
    'site_name': site_name,
    'user': user,
    'protocol': 'https' if use_https else 'http',
    'status_id': status,
    'status': status_for_user,
    'request': request,
    }

    send_mail(subject, email_template_name, from_email, user.email, fail_silently=False, html=html_email_template_name, context =context)

def send_status_change_email_for_custom(request, user, status):
    status_for_user = Status.get_request_status_for_group(get_user_group(user), status)
    subject = "Status change on request " + str(request.name)
    email_template_name='emails/status_change.txt'
    use_https=True
    from_email="Voyint Admin <info@voyint.com>"
    html_email_template_name='emails/status_change.html'

    current_site = "portal.voyint.com"
    site_name = "core"
    domain = "portal.voyint.com"

    context = {
    'email': user.email,
    'domain': domain,
    'site_name': site_name,
    'user': user,
    'protocol': 'https' if use_https else 'http',
    'status_id': status,
    'status': status_for_user,
    'request': request,
    }

    send_mail(subject, email_template_name, from_email, user.email, fail_silently=False, html=html_email_template_name, context =context)

def send_received_email(request, user):
    subject = "Request received"
    email_template_name='emails/request_received.txt'
    use_https=True
    from_email="Voyint Admin <info@voyint.com>"
    html_email_template_name='emails/request_received.html'

    current_site = "portal.voyint.com"
    site_name = "core"
    domain = "portal.voyint.com"

    context = {
    'email': user.email,
    'domain': domain,
    'site_name': site_name,
    'user': user,
    'protocol': 'https' if use_https else 'http',
    'request': request,
    }

    send_mail(subject, email_template_name, from_email, user.email, fail_silently=False, html=html_email_template_name,
              context=context)


def send_created_by_change_email(request, user):
    if isinstance(request, Request):
        request_status = Status.EMPLOYEE_STATUS_CHOICES[request.get_request_status()]
    elif isinstance(request, CorporateRequest):
        request_status = Status.EMPLOYEE_STATUS_CHOICES[request.get_request_status()]
    else:
        request_status = Status.EMPLOYEE_STATUS_CHOICES[request.get_request_status()]

    subject = "Request has been reassigned"
    email_template_name = 'emails/request_reassigned.txt'
    use_https = True
    from_email = "Voyint Admin <info@voyint.com>"
    html_email_template_name = 'emails/request_reassigned.html'


    current_site = 'portal.voyint.com'
    site_name = "core"
    domain = "portal.voyint.com"

    context = {
        'email': user.email,
        'domain': domain,
        'site_name': site_name,
        'user': user,
        'protocol': 'https' if use_https else 'http',
        'request': request,
        'request_status': request_status
    }

    send_mail(subject, email_template_name, from_email, user.email, fail_silently=False, html=html_email_template_name,
              context=context)


def send_analyst_change_email(request, user):
    if isinstance(request, Request):
        request_status = Status.ANALYST_STATUS_CHOICES[request.get_request_status()]
    elif isinstance(request, CorporateRequest):
        request_status = Status.ANALYST_STATUS_CHOICES[request.get_request_status()]
    else:
        request_status = Status.ANALYST_STATUS_CHOICES[request.get_request_status()]

    subject = "Request has been reassigned"
    email_template_name = 'emails/request_reassigned.txt'
    use_https = True
    from_email = "Voyint Admin <info@voyint.com>"
    html_email_template_name = 'emails/request_reassigned.html'


    current_site = 'portal.voyint.com'
    site_name = "core"
    domain = "portal.voyint.com"

    context = {
        'email': user.email,
        'domain': domain,
        'site_name': site_name,
        'user': user,
        'protocol': 'https' if use_https else 'http',
        'request': request,
        'request_status': request_status
    }

    send_mail(subject, email_template_name, from_email, user.email, fail_silently=False, html=html_email_template_name,
              context=context)


def send_batch_file_success_email(user):
    subject = 'Batch File Upload'
    email_template_name = 'emails/batch_upload_success.txt'
    use_https = True
    from_email = 'Voyint Admin <info@voyint.com>'
    html_email_template_name = 'emails/batch_upload_success.html'

    current_site = 'portal.voyint.com'
    site_name = 'core'
    domain = 'portal.voyint.com'

    context = {
        'email': user.email,
        'domain': domain,
        'site_name': site_name,
        'user': user,
        'protocol': 'https' if use_https else 'http',
    }

    send_mail(subject, email_template_name, from_email, user.email, fail_silently=False, html=html_email_template_name,
              context=context)


def send_batch_file_failure_email(reason, user):
    subject = 'Batch File Upload'
    email_template_name = 'emails/batch_upload_failure.txt'
    use_https = True
    from_email = 'Voyint Admin <info@voyint.com>'
    html_email_template_name = 'emails/batch_upload_failure.html'

    current_site = 'portal.voyint.com'
    site_name = 'core'
    domain = 'portal.voyint.com'

    context = {
        'email': user.email,
        'domain': domain,
        'site_name': site_name,
        'user': user,
        'protocol': 'https' if use_https else 'http',
        'reason': reason
    }

    send_mail(subject, email_template_name, from_email, user.email, fail_silently=False, html=html_email_template_name,
              context=context)


def send_csv_email(csv_file, user):
    subject = 'Custom Request Status Report'
    email_template_name = 'emails/csv_report_success.txt'
    use_https = True
    from_email = 'Voyint Admin <info@voyint.com>'
    html_email_template_name = 'emails/csv_report_success.html'

    current_site = 'portal.voyint.com'
    site_name = 'core'
    domain = 'portal.voyint.com'
    context = {
        'email': user.email,
        'domain': domain,
        'site_name': site_name,
        'user': user,
        'protocol': 'https' if use_https else 'http',
    }
    send_mail(subject, email_template_name, from_email, user.email, fail_silently=False,
              html=html_email_template_name, context=context, attachment=csv_file)



def send_excel_email(xls_file, user):
    subject = 'Custom Request Status Report'
    email_template_name = 'emails/csv_report_success.txt'
    use_https = True
    from_email = 'Voyint Admin <info@voyint.com>'
    html_email_template_name = 'emails/csv_report_success.html'

    current_site = 'portal.voyint.com'
    site_name = 'core'
    domain = 'portal.voyint.com'
    context = {
        'email': user.email,
        'domain': domain,
        'site_name': site_name,
        'user': user,
        'protocol': 'https' if use_https else 'http',
    }
    send_mail_xls_attachment(subject, email_template_name, from_email, user.email, fail_silently=False,
              html=html_email_template_name, context=context, attachment=xls_file)

def send_new_customer_registration_email_to_admin(request, user):
    subject_template_name='Voyint New Customer Registration'
    email_template_name='emails/customer_registration_email_to_admin.txt'
    use_https=True
    from_email="Voyint Admin <info@voyint.com>"
    html_email_template_name='emails/customer_registration_email_to_admin.html'

    current_site = "portal.voyint.com"
    site_name = "core"
    domain = "portal.voyint.com"
    admin_email = "manager@voyint.com"
    context = {
    'email': user.email,
    'fullname':user.first_name+" "+user.last_name,
    'domain': domain,
    'site_name': site_name,
    'user': user,
    'protocol': 'https' if use_https else 'http',
    }

    send_mail(subject_template_name, email_template_name, from_email, admin_email, fail_silently=False, html=html_email_template_name, context =context)

def send_data_form_email(email,name,state, bcc):
    subject_template_name='Voyint Data Form'
    email_template_name='emails/data_form.txt'
    use_https=True
    from_email="Voyint Admin <info@voyint.com>"
    html_email_template_name='emails/data_form.html'

    current_site = "portal.voyint.com"
    site_name = "core"
    domain = "portal.voyint.com"
    context = {
    'email': email,
    'company_name':name,
    'domain': domain,
    'site_name': site_name,
    'protocol': 'https' if use_https else 'http',
    'state':state
    }

    send_mail(subject_template_name, email_template_name, from_email, email, fail_silently=False, html=html_email_template_name, context =context, attachment= None, bcc=bcc)
