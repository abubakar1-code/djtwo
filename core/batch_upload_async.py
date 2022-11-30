
import threading
import xlrd
import datetime
from .models import CompanyDueDiligenceTypeSelection, DynamicRequestForm, DynamicRequestFormFields, CustomRequest\
    , CustomRequestFields, Status

from .email_util import send_batch_file_failure_email, send_batch_file_success_email

import urllib
import os
import csv


class BatchUploadThread(threading.Thread):
    def __init__(self, newdoc, dynamic_request_pk, request_type_pk, company_employee, user):
        self.newdoc = newdoc
        self.dynamic_request_pk = dynamic_request_pk
        self.request_type_pk = request_type_pk
        self.company_employee = company_employee
        self.user = user
        threading.Thread.__init__(self)

    def run(self):
        # Get the Request Type
        request_type = CompanyDueDiligenceTypeSelection.objects.get(pk=self.request_type_pk)

        # get the file name URL
        file_name = self.newdoc.docfile.url

        # get the files extension
        file_extension = os.path.splitext(file_name)[1]

        # We need to use the URLopener for AWS
        opener = urllib.URLopener()
        myfile = opener.open(file_name).read()

        data = []
        keys = []
        count = 1

        # If the file is a CSV
        if file_extension == '.csv':
            # Read the CSV in as a list of dictionaries
            reader = csv.DictReader(myfile.decode('utf-8').splitlines(), delimiter=",")
            data = list(reader)

            # get a list of the keys which is the top row
            r = csv.reader(myfile.decode('utf-8').splitlines(), delimiter=",")
            keys = r.next()
            # remove any blank keys
            keys = filter(None, keys)
        else:
            #handle excel file
            xlbook = xlrd.open_workbook(file_contents=myfile)
            sheet = xlbook.sheet_by_index(0)
            keys = [sheet.cell(0, col_index).value for col_index in xrange(sheet.ncols)]
            for row_index in xrange(1, sheet.nrows):
                d = {}
                for col_index in xrange(sheet.ncols):
                    cell = sheet.cell(row_index, col_index)
                    cell_value = cell.value
                    # cell_type: 0 is blank, 1 is text, 2 is a number, 3 is a date
                    cell_type = sheet.cell_type(row_index, col_index)
                    # Cell is Text
                    if cell_type == 1:
                        d[keys[col_index]] = cell_value
                    # Cell is a Number
                    if cell_type == 2:
                        # check if its an int
                        if int(cell_value) == cell_value:
                            cell_value = int(cell_value)
                        d[keys[col_index]] = cell_value
                    # Cell is a Date
                    if cell_type == 3:
                        date_time = datetime.datetime(*xlrd.xldate_as_tuple(cell_value, xlbook.datemode)).date()
                        date_time = str(date_time)
                        date_time = datetime.datetime.strptime(date_time, '%Y-%m-%d').strftime('%m/%d/%y')
                        d[keys[col_index]] = str(date_time)
                data.append(d)
        # if we have data from the uploaded document
        if data:
            # try to find the dynamic form this data belongs to....
            try:
                dynamic_request_form = DynamicRequestForm.objects.get(pk=self.dynamic_request_pk)
            # if we can't find the form throw a huge fit..
            except DynamicRequestForm.DoesNotExist:
                send_batch_file_failure_email(
                    reason='We could not find the dynamic request form that this file belongs to'
                    , user=self.user)
                raise Exception('could not find dynamic request form in batch upload')
            # now we are going to try to find all of the fields that belong to this dynamic form
            try:
                dynamic_request_form_fields = DynamicRequestFormFields.objects.filter(
                    dynamic_request_form=self.dynamic_request_pk)
            # if there is a problem finding the fields throw an exception.
            except DynamicRequestFormFields.DoesNotExist:
                send_batch_file_failure_email(
                    reason='We could not find the dynamic request form fields for this request'
                    , user=self.user)
                raise Exception('could not find custom request form fields in batch upload')

            # Here we are getting a list of the form fields so we can check for missing columns
            dynamic_form_fields = [x.label for x in dynamic_request_form_fields]
            # Name is not technically a form field, but it is required.
            dynamic_form_fields.append('Name')

            # we get a list of form fields that don't match to any columns
            unmatched_form_fields = list(set(dynamic_form_fields) - set(keys))

            # and we get a list of columns that don't match to any fields
            unmatched_columns = list(set(keys) - set(dynamic_form_fields))

            # if we have unmatched columns, or unmatched fields.
            if len(unmatched_form_fields) > 0 or len(unmatched_columns) > 0:

                # stringify them so we can send an email to the user
                unmatched_form_fields_string = ', '.join(map(str, unmatched_form_fields))
                unmatched_columns_string = ', '.join(map(str, unmatched_columns))

                # Send batch file failure email.
                send_batch_file_failure_email(reason='Could Not Match Form Fields: ' +
                                                     unmatched_form_fields_string + '\n' +
                                                     'Could Not Match Column Headers: '+unmatched_columns_string,
                                              user=self.user)
                # Throw an exception
                raise Exception('could not match all fields in batch upload')
            # ok now for the fun stuff...
            for row in data:
                # Name is a required field so we must check for it.
                if not row.get('Name'):
                    send_batch_file_failure_email(reason='Could not find the column:"Name" (case sensitive) '
                                                  , user=self.user)
                    raise Exception('Name(case sensitive) is a required field')
                custom_request = CustomRequest(name=row.get('Name'),
                                               request_type=request_type,
                                               dynamic_request_form=dynamic_request_form,
                                               created_by=self.company_employee
                                               )
                try:
                    custom_request.clean()
                    custom_request.save()
                    # need to save twice because it's pk is part of display_id
                    custom_request.display_id = CustomRequest.generate_display_id(custom_request)
                    custom_request.save()
                except:
                    send_batch_file_failure_email(reason='Custom Request could not be saved '
                                                  , user=self.user)
                    raise Exception('Could not save custom request in batch upload')
                custom_request_status = Status.add_request_status(custom_request, Status.NEW_STATUS, '')
                for key, value in row.items():
                    found = False
                    for field in dynamic_request_form_fields:
                        if key == field.label:
                            found = True
                            custom_request_field = CustomRequestFields()
                            custom_request_field.custom_request = custom_request
                            custom_request_field.form_field = field
                            custom_request_field.value = value
                            try:
                                custom_request_field.save()
                            except:
                                send_batch_file_failure_email(reason='Could not save custom request field',
                                                              user=self.user)
                                raise Exception('could not save custom request field in batch upload')
                    if not found and key != 'Name' and key:
                        send_batch_file_failure_email(
                            reason='Could not map column "'+key+'" in your excel file to a form field', user=self.user)
                        # TODO: Probably may need to do this in some other situations as well....
                        custom_request.delete()
                        raise Exception('Could not map column "'+key+'" in your excel file to a form field')
            send_batch_file_success_email(self.user)
        else:
            # No Data!
            send_batch_file_failure_email(reason='No Data could be read from your file.', user=self.user)
