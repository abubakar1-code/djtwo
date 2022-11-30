import threading

from .models import CompanyEmployee, Status, CustomRequest, DynamicRequestFormFields, CustomRequestFields

from django.utils import formats
from django.utils.dateformat import DateFormat

import csv

from pytz import timezone

from .email_util import send_csv_email

import StringIO

class CsvReportGenerator(threading.Thread):
    def __init__(self, request):
        self.request = request
        threading.Thread.__init__(self)

    def run(self):
        print "$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$"
        print 'CSV REPORT THREAD START'
        print "$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$"
        current_user = self.request.user
        supervisor = CompanyEmployee.get_company_employee(current_user)
        company = supervisor.company
        ids = list(Status.get_all_current_ids_queryset())
        statuses = Status.objects.filter(id__in=ids, request__created_by__company=company).order_by('request__id').values(
            'request__id', 'request__display_id', 'request__request_type__name', 'status')
        fieldnames = [
            'request__display_id', 'status',
            'Start Date', 'Completed Date', 'request__request_type__name']
        
        field_labels = ['Salesforce Case', 'Party Key', "Assigned Specialist's Email", 'Group']


        for label in field_labels:
            fieldnames.append(label)

        for status in statuses:
            id = status['request__id']
            request = CustomRequest.objects.get(pk=id)

            if status['status'] == 1 or status['status'] == 2:
                status['status'] = 'New'
            elif status['status'] == 5:
                status['status'] = 'Submitted'
                start_est_datetime = request.get_in_progress_request_status().datetime.astimezone(timezone('US/Eastern'))
                df = DateFormat(start_est_datetime)
                formatted_start_date = df.format('n/d/Y H:i')
                status['Start Date'] = formatted_start_date
                end_est_datetime = request.get_complete_request_status().datetime.astimezone(timezone('US/Eastern'))
                df = DateFormat(end_est_datetime)
                formatted_end_date = df.format('n/d/Y H:i')
                status['Completed Date'] = formatted_end_date
            elif status['status'] == 7:
                status['status'] = 'Incomplete'
            else:
                status['status'] = 'In Progress'

            request_fields = CustomRequestFields.objects.filter(custom_request=id, form_field__label__in=field_labels).values('value', 'form_field__label')
            for field in request_fields:
                label = field['form_field__label']
                value = field['value']
                status[label] = value
            del status['request__id']

        csvfile = StringIO.StringIO()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(statuses)
        print "$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$"
        print "CSV GENERATOR END"
        print "$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$"
        send_csv_email(csvfile, current_user)
