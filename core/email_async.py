from django.core.mail import send_mail as core_send_mail
from django.core.mail import EmailMultiAlternatives
import threading
from django.conf import settings
from django.template import loader
from email.MIMEImage import MIMEImage

import os

class EmailThread(threading.Thread):
    def __init__(self, subject, body, from_email, recipient_list, fail_silently, html, context=None, attachment=None, bcc=None):
        self.subject = subject
        self.body = body
        self.recipient_list = recipient_list
        self.from_email = from_email
        self.fail_silently = fail_silently
        self.html = html
        self.attachment = attachment
        self.context = context
        self.bcc = bcc
        threading.Thread.__init__(self)

    def run(self):
        subject = ''.join(self.subject.splitlines())
        body = loader.render_to_string(self.body, self.context)
        msg = EmailMultiAlternatives(subject, body, self.from_email, [self.recipient_list], [self.bcc] if self.bcc else None)
        if self.html:
            html_email = loader.render_to_string(self.html, self.context)
            msg.attach_alternative(html_email, 'text/html')

            msg.mixed_subtype = 'related'
            logo = settings.COMPLY_EMAIL_LOGO_NAME
            # fp = open(os.path.join(os.path.join(settings.STATIC_ROOT), logo), 'rb')
            # msg_img = MIMEImage(fp.read())
            # fp.close()
            # msg_img.add_header('Content-ID', '<{}>'.format("logo"))
            # msg.attach(msg_img)

            if self.attachment is not None:
                msg.attach('custom_reports.csv', self.attachment.getvalue(), 'text/csv')
        msg.send(self.fail_silently)



def send_mail(subject, body, from_email, recipient_list, fail_silently=False, html=None, context = None, attachment=None, bcc = None, *args, **kwargs):
    EmailThread(subject, body, from_email, recipient_list, fail_silently, html, context, attachment, bcc).start()





class ExcelEmailThread(threading.Thread):
    def __init__(self, subject, body, from_email, recipient_list, fail_silently, html, context=None, attachment=None):
        self.subject = subject
        self.body = body
        self.recipient_list = recipient_list
        self.from_email = from_email
        self.fail_silently = fail_silently
        self.html = html
        self.attachment = attachment
        self.context = context
        threading.Thread.__init__(self)

    def run(self):
        subject = ''.join(self.subject.splitlines())
        body = loader.render_to_string(self.body, self.context)
        msg = EmailMultiAlternatives(subject, body, self.from_email, [self.recipient_list])
        if self.html:
            html_email = loader.render_to_string(self.html, self.context)
            msg.attach_alternative(html_email, 'text/html')

            msg.mixed_subtype = 'related'
            # logo = settings.COMPLY_EMAIL_LOGO_NAME
            # fp = open(os.path.join(os.path.join(settings.STATIC_ROOT), logo), 'rb')
            # msg_img = MIMEImage(fp.read())
            # fp.close()
            # msg_img.add_header('Content-ID', '<{}>'.format("logo"))
            # msg.attach(msg_img)

            if self.attachment is not None:
                msg.attach('custom_reports.xls', self.attachment.getvalue(), 'application/vnd.ms-excel')
        msg.send(self.fail_silently)


def send_mail_xls_attachment(subject, body, from_email, recipient_list, fail_silently=False, html=None, context = None, attachment=None, *args, **kwargs):
    ExcelEmailThread(subject, body, from_email, recipient_list, fail_silently, html, context, attachment).start()
