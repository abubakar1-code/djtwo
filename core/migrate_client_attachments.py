import threading
from .models import CustomRequest, CorporateRequest, Request, ClientAttachmentCustom, ClientAttachmentCorporate, \
    ClientAttachment


class MigrateAttachments(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        print'''
           %%% MIGRATING ATTACHMENTS %%%
        '''
        # custom first
        print 'CUSTOM START:'
        custom_requests = CustomRequest.objects.exclude(client_attachment__isnull=True).exclude(client_attachment__exact='')
        for request in custom_requests:
            if request.attachment:
                attachment = ClientAttachmentCustom(created_by=request.created_by,
                                                attachment=request.client_attachment, request=request)
                attachment.save()
                print ".",

        print 'CORPORATE START:'
        corporate_requests = CorporateRequest.objects.exclude(client_attachment__isnull=True).exclude(client_attachment__exact='')
        for request in corporate_requests:
            if request.attachment:
                attachment = ClientAttachmentCorporate(created_by=request.created_by, attachment=request.client_attachment,
                                                       request=request)
                attachment.save()
                print ".",

        print "INDIVIDUAL START:"
        ind_requests = Request.objects.exclude(client_attachment__isnull=True).exclude(client_attachment__exact='')
        for request in ind_requests:
            if request.attachment:
                attachment = ClientAttachment(created_by=request.created_by, attachment=request.client_attachment, request=request)
                attachment.save()
                print ".",
