from __future__ import absolute_import

from celery import shared_task
from django.core.files import File
from .models import CorporateRequest, CustomRequest, RequestArchive, Request
from .models import Request as IndividualRequest
import StringIO
import zipfile
import datetime
import os
from .utils import generate_custom_pdf_file, generate_individual_pdf_file, generate_corporate_pdf_file
import urllib
from celery.utils.log import get_task_logger
import socket
from django.conf import settings
from .pdf_generator import join_pdf
from django.utils import timezone
archive_size = 100

@shared_task
def zip_corporate_requests(request_ids, created_by):
    opener = urllib.URLopener()
    requests = CorporateRequest.objects.filter(id__in=request_ids)
    failed_pdfs = []
    for request in requests:
        if not request.pdf_report:
            try:
                pdf = generate_corporate_pdf_file(request.report_url)
                if pdf:
                    request.pdf_report.save(request.report_url+".pdf", pdf)
            except:
                failed_pdfs.append(request.id)
    requests = CorporateRequest.objects.filter(id__in=request_ids).exclude(pdf_report=None)

    num_requests = len(requests)

    # Check if exactly divisible by archive_size
    if num_requests % archive_size == 0:
        # Int returns floor
        num_archives = int(num_requests/archive_size)
    else:
        num_archives = int(num_requests/archive_size)+1
    now = timezone.now()
    for i in range(num_archives):
        archive_piece = 'Part {} of {}'.format(i+1,num_archives)

        zipped_file = StringIO.StringIO()
        with zipfile.ZipFile(zipped_file, 'w') as zip:
            for request in requests[100*i:100+100*i]:
                # Added for windows local development
                if socket.gethostname() == 'CHI1004':
                    report_file_url = settings.MEDIA_ROOT+request.pdf_report.name
                    if request.attachment:
                        attachment_file_url = settings.MEDIA_ROOT+request.attachment.name
                else:
                    report_file_url = request.pdf_report.url
                    if request.attachment:
                        attachment_file_url = request.attachment.url
                pdf_list = []

                report_pdf_file = StringIO.StringIO(opener.open(report_file_url).read())
                pdf_list.append(report_pdf_file)

                if attachment_file_url:
                    try:
                        report_attachment_file = StringIO.StringIO(opener.open(attachment_file_url).read())
                        pdf_list.append(report_attachment_file)
                    except:
                        pass

                pdf_file = join_pdf(pdf_list)

                # zip.writestr(os.path.basename(report_file_url), pdf_file)
                zip.writestr(request.get_batch_pdf_name(), pdf_file)

        zipped_file.seek(0)
        archive = RequestArchive(company=created_by.company, created_by=created_by,
                                 datetime=now, archive_piece=archive_piece)
        date = timezone.localtime(archive.datetime).strftime("%Y-%m-%d_%H-%m-%S")
        archive.archive.save("corporate-{}-{}-{}-{}.zip".format(
                                created_by.company.name, 
                                created_by.user.username.split('@')[0],
                                date, 
                                archive_piece
                            ), File(zipped_file))
        archive.save()

    return failed_pdfs




@shared_task
def zip_individual_requests(request_ids, created_by):
    opener = urllib.URLopener()
    requests = Request.objects.filter(id__in=request_ids)
    failed_pdfs = []
    for request in requests:
        if not request.pdf_report:
            try:
                pdf = generate_individual_pdf_file(request.report_url)
                if pdf:
                    request.pdf_report.save(request.report_url+".pdf", pdf)
            except:
                failed_pdfs.append(request.id)

    # get fresh requests
    requests = Request.objects.filter(id__in=request_ids).exclude(pdf_report=None)
    num_requests = len(requests)

    # Check if exactly divisible by archive_size
    if num_requests % archive_size == 0:
        # Int returns floor
        num_archives = int(num_requests/archive_size)
    else:
        num_archives = int(num_requests/archive_size)+1
    now = timezone.now()
    for i in range(num_archives):
        archive_piece = 'Part {} of {}'.format(i+1,num_archives)

        # create a zipfile like object
        zipped_file =StringIO.StringIO()
        with zipfile.ZipFile(zipped_file, 'w') as zip:
            for request in requests[100*i:100+100*i]:
                # Added for windows local development
                if socket.gethostname() == 'CHI1004':
                    report_file_url = settings.MEDIA_ROOT+request.pdf_report.name
                    if request.attachment:
                        attachment_file_url = settings.MEDIA_ROOT+request.attachment.name
                else:
                    report_file_url = request.pdf_report.url
                    if request.attachment:
                        attachment_file_url = request.attachment.url
                pdf_list = []

                report_pdf_file = StringIO.StringIO(opener.open(report_file_url).read())
                pdf_list.append(report_pdf_file)

                if attachment_file_url:
                    try:
                        report_attachment_file = StringIO.StringIO(opener.open(attachment_file_url).read())
                        pdf_list.append(report_attachment_file)
                    except:
                        pass
                        
                pdf_file = join_pdf(pdf_list)

                # zip.writestr(os.path.basename(report_file_url), pdf_file)
                zip.writestr(request.get_batch_pdf_name(), pdf_file)

        zipped_file.seek(0)
        # save the zip file
        archive = RequestArchive(company=created_by.company, created_by=created_by,
                                 datetime=now, archive_piece=archive_piece)
        date = timezone.localtime(archive.datetime).strftime("%Y-%m-%d_%H-%m-%S")
        archive.archive.save("individual-{}-{}-{}-{}.zip".format(
                                created_by.company.name, 
                                created_by.user.username.split('@')[0],
                                date, 
                                archive_piece
                            ), File(zipped_file))
        archive.save()

    return failed_pdfs

@shared_task
def zip_custom_requests(request_ids, created_by):
    logger = get_task_logger(__name__)
    opener = urllib.URLopener()
    requests = CustomRequest.objects.filter(id__in=request_ids)
    failed_pdfs = []
    # first go through custom_requests, if the pdf is not already stored we will write it
    for ddrequest in requests:
        if not ddrequest.pdf_report:
            # on submit we create a pdf and save it
            try:
                pdf = generate_custom_pdf_file(ddrequest.report_url)
                if pdf:
                    ddrequest.pdf_report.save(ddrequest.report_url+".pdf", pdf)
            except:
                logger.info("failed creating request")

    # get the fresh requests exclude those without pdf reports.
    requests = CustomRequest.objects.filter(id__in=request_ids).exclude(pdf_report=None).order_by('id')

    num_requests = len(requests)

    # Check if exactly divisible by archive_size
    if num_requests % archive_size == 0:
        # Int returns floor
        num_archives = int(num_requests/archive_size)
    else:
        num_archives = int(num_requests/archive_size)+1
    now = timezone.now()
    for i in range(num_archives):
        archive_piece = 'Part {} of {}'.format(i+1,num_archives)

        # create a zip filelike object
        zipped_file = StringIO.StringIO()
        with zipfile.ZipFile(zipped_file, 'w') as zip:
            for ddrequest in requests[100*i:100+100*i]:
                # Added for windows local development
                if socket.gethostname() == 'CHI1004':
                    report_file_url = settings.MEDIA_ROOT+ddrequest.pdf_report.name
                    if ddrequest.attachment:
                        attachment_file_url = settings.MEDIA_ROOT+ddrequest.attachment.name
                else:
                    report_file_url = ddrequest.pdf_report.url
                    if ddrequest.attachment:
                        attachment_file_url = ddrequest.attachment.url
                pdf_list = []

                report_pdf_file = StringIO.StringIO(opener.open(report_file_url).read())
                pdf_list.append(report_pdf_file)

                if attachment_file_url:
                    try:
                        report_attachment_file = StringIO.StringIO(opener.open(attachment_file_url).read())
                        pdf_list.append(report_attachment_file)
                    except:
                        pass

                pdf_file = join_pdf(pdf_list)

                # zip.writestr(os.path.basename(report_file_url), pdf_file)
                zip.writestr(ddrequest.get_batch_pdf_name(), pdf_file)


        zipped_file.seek(0)
        # save the zip file
        archive = RequestArchive(company=created_by.company, created_by=created_by,
                                 datetime=now, archive_piece=archive_piece)
        date = timezone.localtime(archive.datetime).strftime("%Y-%m-%d_%H-%m-%S")
        archive.archive.save("custom-{}-{}-{}-{}.zip".format(
                                created_by.company.name, 
                                created_by.user.username.split('@')[0],
                                date, 
                                archive_piece
                            ), File(zipped_file))
        archive.save()
    
    return failed_pdfs

@shared_task
def hello(name1,name2):
    print 'Hello {} and {}!'.format(name1,name2)


from django.core.files.storage import default_storage


@shared_task
def delete_pdf_archive_report_objects():
    custom_requests = CustomRequest.objects.filter(pdf_report__isnull=False)
    for request in custom_requests:
        report = request.pdf_report
        if report:
            try:
                default_storage.delete(report.name)
            except:
                pass
        request.pdf_report.delete(save=True)

    requests = Request.objects.filter(pdf_report__isnull=False)
    for request in requests:
        report = request.pdf_report
        if report:
            try:
                default_storage.delete(report.name)
            except:
                pass
        request.pdf_report.delete(save=True)

    corporate_requests = CorporateRequest.objects.filter(pdf_report__isnull=False)
    for request in corporate_requests:
        report = request.pdf_report
        if report:
            try:
                default_storage.delete(report.name)
            except:
                pass
        request.pdf_report.delete(save=True)

@shared_task
def delete_pdf_archive_archive_objects():
    archives = RequestArchive.objects.all()
    for archive in archives:
        file = archive.archive
        if file:
            try:
                default_storage.delete(file.name)
            except:
                pass
        archive.archive.delete(save=True)
        archive.delete()
