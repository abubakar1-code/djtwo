import xlwt
import threading
import StringIO
from django.utils.dateformat import DateFormat
from pytz import timezone

from .email_util import send_excel_email
from .models import CustomRequest, Status, CompanyEmployee, CustomRequestFields



class ExcelReportGenerator(threading.Thread):

    def __init__(self, request):
        self.request = request
        threading.Thread.__init__(self)

    def run(self):
        current_user = self.request.user
        supervisor = CompanyEmployee.get_company_employee(current_user)
        company = supervisor.company
        ids = list(Status.get_all_current_ids_queryset_for_company(company))

        fieldnames = [
            'custom_request__id', 'custom_request__display_id', 'status', 'custom_request__request_type__name']

        statuses = Status.objects.filter(id__in=ids, custom_request__created_by__company=company).order_by(
            'request__id').values(*fieldnames)

        del fieldnames[0]

        field_labels = ['Salesforce Case', 'Party Key', "Assigned Specialist's Email", 'Group', 'Reporting Period']

        for label in field_labels:
            fieldnames.append(label)

        fieldnames.append('Start Date')
        fieldnames.append('Completed Date')


        headers = ['Display ID', 'Status','Request Type', 'Salesforce Case', 'Party Key','Assigned Specialist\'s Email',
                   'Group', 'Reporting Period', 'Start Date', 'Completed Date']
        workbook = xlwt.Workbook(encoding = 'ascii')
        worksheet = workbook.add_sheet('My Worksheet')
        row_index = 0
        col_index = 0
        for header in headers:
            worksheet.write(row_index, col_index, header)
            col_index += 1
        row_index = 1
        col_index = 0
        for row in statuses:
            request_id = row['custom_request__id']
            request = CustomRequest.objects.get(pk=request_id)
            request_fields = CustomRequestFields.objects.filter(custom_request=request_id, form_field__label__in=field_labels).values('value', 'form_field__label')
            row['Start Date'] = ''
            row['Completed Date'] = ''
            row['Salesforce Case'] = ''
            row['Party Key'] = ''
            row["Assigned Specialist's Email"] = ''
            row['Group'] = ''
            row['Reporting Period'] = ''
            del row['custom_request__id']
            if row['status'] == 1 or row['status'] == 2:
                row['status'] = 'New'
            elif row['status'] == 5:
                row['status'] = 'Submitted'
                start_est_datetime = request.in_progress_status.datetime.astimezone(timezone('US/Eastern'))
                df = DateFormat(start_est_datetime)
                formatted_start_date = df.format('n/d/Y H:i')
                row['Start Date'] = formatted_start_date
                end_est_datetime = request.completed_status.datetime.astimezone(timezone('US/Eastern'))
                df = DateFormat(end_est_datetime)
                formatted_end_date = df.format('n/d/Y H:i')
                row['Completed Date'] = formatted_end_date
            elif row['status'] == 7:
                row['status'] = 'Incomplete'
            else:
                row['status'] = 'In Progress'

            for field in request_fields:
                label = field['form_field__label']
                value = field['value']
                row[label] = value
            for col in row:
                worksheet.write(row_index, col_index, row[fieldnames[col_index]])
                col_index += 1
            col_index = 0
            row_index += 1

        excel_file = StringIO.StringIO()
        workbook.save(excel_file)
        send_excel_email(excel_file, current_user)






