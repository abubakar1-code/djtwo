from itertools import chain

from django.core.urlresolvers import reverse
from django.db.models import Count
from django.utils import formats
from django.core.serializers.json import DjangoJSONEncoder

from views import ManagerOnlyMixin, ManagerSupervisorOnlyMixin, SupervisorOnlyMixin

from eztables.views import DatatablesView

from django.http import HttpResponse


from pytz import timezone

from .models import Request, CorporateRequest, CustomRequest, CompanyDueDiligenceTypeSelection, Reports, Status, Surcharge

import datetime

from .utils import *
import json


####################################
#
# ARCHIVED REPORTS
#
####################################


class ArchivedReportsDatatablesView(ManagerOnlyMixin, DatatablesView):
    model = Reports
    fields = (
        'id',
        'name',
        'created_by__user',
        'created_by__company',
        'report_request_type',
        'report_template',
        'created_date',
    )

    def get_row(self, row):
        report_id = row.pop('id')
        report_name = row.pop('name')
        request_url = reverse('archived_report', kwargs={"archived_report_id": report_id,
                                                         "report_name": report_name})

        display = "<a target=\"_blank\" href=\"" + request_url + "\" class=\"btn btn-xs grey btn-editable\"><i class=\"fa fa-search\"></i> View</a>"
        row['id'] = display

        report = Reports.objects.get(pk=report_id)

        row['name'] = report.name
        row['created_by__user'] = report.created_by.user.get_full_name()
        row['created_by__company'] = report.created_by.company.name
        row['report_request_type'] = report.report_request_type
        if report.report_template is None:
            row['report_template'] = ''
        else:
            row['report_template'] = report.report_template

        DATE_FORMAT = "%Y-%m-%d %X"
        datetime = row.pop('created_date')
        cst_datetime = datetime.astimezone(timezone('US/Central'))
        formatted_date = formats.date_format(cst_datetime, "SHORT_DATETIME_FORMAT")
        row['created_date'] = formatted_date

        return super(ArchivedReportsDatatablesView, self).get_row(row)

    def get_queryset(self):
        #not retaining order_by from sub query so must do two queries. not ideal and not great for performance.
        #will have to be updated
        reports = Reports.objects.all()

        name_search = str(self.request.GET['sSearch_0'])
        if len(name_search) > 0 and name_search != 'undefined':
            reports = reports.filter(name__icontains=name_search)

        created_by_search = str(self.request.GET['sSearch_1'])
        if len(created_by_search) > 0 and created_by_search != 'undefined':
            reports = reports.filter(created_by__user__last_name__icontains=created_by_search)

        company_search = self.request.GET['sSearch_2']
        if (len(company_search) > 0):
            reports = reports.filter(created_by__company__id=int(company_search))

        request_type = self.request.GET['sSearch_3']
        if len(request_type) > 0 and request_type != 'undefined':
            reports = reports.filter(report_request_type__icontains=request_type)

        start_end_date = str(self.request.GET['sSearch_4'])
        if len(start_end_date) > 3:
            array = start_end_date.split('+')
            start = fix_created_time(array[0])
            end = fix_end(array[1])
            reports = reports.filter(created_date__range=[start, end])

        reports = sort_reports(self.request, reports)

        return reports

    def json_response(self, data):
        return HttpResponse(
            json.dumps(data, cls=DjangoJSONEncoder),
            content_type='application/json'
        )

###
# SUPERVISOR
###

class NewAllRequestsDatatablesView(DatatablesView):
    model = Status
    fields = (
        'object_id',
        'custom_request__name',
        'status',
        'datetime',
        'content_type__model',
        'request__first_name',
        'request__last_name',
        'corporate_request__company_name',
    )

    def get_row(self, row):
        # Setting the links to display the details for each row.
        if row['content_type__model'] == 'request':
            # grabbing id, and changing it do display_id
            request_id = row.pop('object_id')
            request = Request.objects.get(pk=request_id)

            # creating link
            request_url = reverse('request_supervisor', kwargs={"pk": request_id})
            display = "<a href=\"" + request_url + "\" class=\"btn btn-xs grey btn-editable\">  "+request.display_id+"</a>"
            row['object_id'] = display
            row['content_type__model'] = 'Individual'

            # Setting Name
            first_name = request.first_name
            last_name = request.last_name
            combo_name = first_name+" "+last_name
            row['custom_request__name'] = combo_name
            row['request__first_name'] = ''
            row['request__last_name'] = ''
            # if row['status'] == Status.SUBMITTED_STATUS:
            #     row['datetime'] = row['request__completed_status__datetime']

        elif row['content_type__model'] == 'customrequest':
            request_id = row.pop('object_id')
            request_url = reverse('request_supervisor_for_custom', kwargs={"pk": int(request_id)})
            display = "<a href=\"" + request_url + "\" class=\"btn btn-xs grey btn-editable\">"+CustomRequest.objects.get(pk=request_id).display_id+"</a>"
            row['object_id'] = display
            row['content_type__model'] = 'Custom'
            # if row['status'] == Status.SUBMITTED_STATUS:
            #     row['datetime'] =row['custom_request__completed_status__datetime']

        elif row['content_type__model'] == 'corporaterequest':
            request_id = row.pop('object_id')
            request_url = reverse('request_supervisor_for_corporate', kwargs={"pk": int(request_id)})
            display = "<a href=\"" + request_url + "\" class=\"btn btn-xs grey btn-editable\">"+CorporateRequest.objects.get(pk=request_id).display_id+"</a>"
            row['object_id'] = display
            row['content_type__model'] = 'Corporate'
            row['custom_request__name'] = row['corporate_request__company_name']
            row['corporate_request__company_name'] = ''
            # if row['status'] == Status.SUBMITTED_STATUS:
            #     row['datetime'] = row['corporate_request__completed_status__datetime']

        status = row.pop('status')
        display_status = Status.SUPERVISOR_STATUS_CHOICES[status]
        row['status'] = display_status

        datetime = row.pop('datetime')
        cst_datetime = datetime.astimezone(timezone('US/Central'))
        formatted_date = formats.date_format(cst_datetime, "SHORT_DATETIME_FORMAT")
        row['datetime'] = formatted_date


        return super(NewAllRequestsDatatablesView, self).get_row(row)

    def get_queryset(self):
        current_user = self.request.user
        search = self.request.GET['sSearch']
        try:
            sort = self.request.GET['iSortCol_0']
        except Exception, e:
            sort = None

        supervisor = get_company_employee(current_user)
        company = supervisor.company.name
        ids = list(Status.get_all_current_ids_queryset_for_company(company))
        statuses = Status.objects.filter(id__in=ids)

        length = len(statuses)

        if length == 0:
            return Status.objects.none()

        if sort and length > 0:
            statuses = self.sort_supervisor_datatable(statuses)

        if (len(search) > 0):
            statuses = self.search_col_name(search, statuses) | self.search_col_id(search, statuses)

        # ID
        id_search = ifCustomReturnVal(self.request.GET['sSearch_0'])
        if (len(id_search) > 0):
            cust_id_filt = statuses.filter(custom_request__display_id__icontains=id_search)
            corp_id_filt = statuses.filter(corporate_request__display_id__icontains=id_search)
            ind_id_filt = statuses.filter(request__display_id__icontains=id_search)
            statuses = cust_id_filt | corp_id_filt | ind_id_filt

        # NAME
        name_search = ifCustomReturnVal(self.request.GET['sSearch_1'])
        if (len(name_search) > 0):
            cust_name = statuses.filter(custom_request__name__icontains=name_search)
            corp_name = statuses.filter(corporate_request__company_name__icontains=name_search)
            ind_first_name = statuses.filter(request__first_name__icontains=name_search)
            ind_last_name = statuses.filter(request__last_name__icontains=name_search)
            statuses = cust_name | corp_name | ind_first_name | ind_last_name


        # Created By
        created_by_id = ifCustomReturnVal(self.request.GET['sSearch_2'])
        if (len(created_by_id) > 0):
            cust_ids = statuses.filter(custom_request__created_by__user__id=created_by_id).values_list('id', flat=True)
            corp_ids = statuses.filter(corporate_request__created_by__user__id=created_by_id).values_list('id', flat=True)
            ind_ids = statuses.filter(request__created_by__user__id=created_by_id).values_list('id', flat=True)
            comb_ids = list(chain(cust_ids, corp_ids, ind_ids))
            statuses = statuses.filter(id__in=comb_ids)


        # STATUS
        status_search = ifCustomReturnVal(self.request.GET['sSearch_3'])
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
            elif int(status_search) == Status.ARCHIVED_STATUS:
                supervisor_search_statuses = [Status.ARCHIVED_STATUS]

            statuses = statuses.filter(status__in=supervisor_search_statuses)


        # TYPE
        type_search = ifCustomReturnVal(self.request.GET['sSearch_4'])
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
        start_end_date = self.request.GET['sSearch_5']
        if (len(start_end_date) > 3):
            array = start_end_date.split('+')
            start = fix_start(array[0])
            end = fix_end(array[1])
            statuses = statuses.filter(id__in=ids).filter(datetime__range=[start, end])


        # CUSTOM FIELD
        custom_field = ifCustomReturnVal(self.request.GET['sSearch_7'])
        if (len(custom_field) > 0):
            field_ids = list(
                CustomRequestFields.objects.filter(custom_request__dynamic_request_form__render_form=True,
                                                   form_field__id=custom_field).exclude(
                    value__isnull=True).exclude(value__exact='').values_list('custom_request__id', flat=True))

            statuses = statuses.filter(custom_request__id__in=field_ids)


        # CUSTOM FIELD VALUE
        custom_field_value = ifCustomReturnVal(self.request.GET['sSearch_8'])
        if (len(custom_field_value) > 0):
            field_ids = list(
                CustomRequestFields.objects.filter(custom_request__dynamic_request_form__render_form=True,
                                                   value__icontains=custom_field_value).values_list(
                                                    'custom_request__id', flat=True))
            statuses = statuses.filter(custom_request__id__in=field_ids)

        # FORM NAME
        dynamic_request_form_id = ifCustomReturnVal(self.request.GET['sSearch_9'])
        if (len(dynamic_request_form_id) > 0):
            statuses = statuses.filter(custom_request__dynamic_request_form__id=dynamic_request_form_id)


        # REQUEST TYPE
        request_type = ifCustomReturnVal(self.request.GET['sSearch_10'])
        if len(request_type) > 0:
            statuses = statuses.filter(content_type__model=request_type)


        return statuses

    def search_col_id(self, search, queryset):
        corp_set = queryset
        corp_set = corp_set.filter(corporate_request__display_id__icontains=search)

        ind_set = queryset
        ind_set = ind_set.filter(request__display_id__icontains=search)

        cust_set = queryset
        cust_set = cust_set.filter(custom_request__display_id__icontains=search)

        searched_set = cust_set | ind_set | corp_set
        return searched_set

    def search_col_name(self, search, queryset):
        corp_set = queryset
        corp_set = corp_set.filter(corporate_request__company_name__icontains=search)

        ind_set_first_name = queryset
        ind_set_last_name = queryset
        ind_set_first_name = ind_set_first_name.filter(request__first_name__icontains=search)
        ind_set_last_name = ind_set_last_name.filter(request__last_name__icontains=search)

        cust_set = queryset
        cust_set = cust_set.filter(custom_request__name__icontains=search)

        searched_set = corp_set | ind_set_first_name | ind_set_last_name | cust_set
        return searched_set

    def sort_supervisor_datatable(self, statuses):
        sort_column = self.request.GET['iSortCol_0']
        sort_direction = self.request.GET['sSortDir_0']
        order_by = ''
        if (sort_column == '0'):
            order_by = 'object_id'
        elif (sort_column == '1'):
            corp_name = 'corporate_request__company_name'
            cust_name = 'custom_request__name'
            ind_name = 'request__first_name'
            if (sort_direction == 'desc'):
                corp_name = '-' + corp_name
                cust_name = '-' + cust_name
                ind_name = '-' + ind_name
            statuses = statuses.order_by(corp_name, cust_name, ind_name)


        elif (sort_column == '2'):
            statuses = sort_statuses(statuses,sort_direction)
        elif (sort_column == '3'):
            date = 'datetime'
            # Below is code to change  this to sort on completed dates and all other dates
            # cust_comp_date = 'custom_request__completed_status__datetime'
            # corp_comp_date = 'corporate_request__completed_status__datetime'
            # ind_comp_date = 'request__completed_status__datetime'
            # if (sort_direction == 'desc'):
            #     date = '-' + date
            #     cust_comp_date = '-' + cust_comp_date
            #     corp_comp_date = '-' + corp_comp_date
            #     ind_comp_date = '-' + ind_comp_date
            # statuses = statuses.order_by(date, cust_comp_date, corp_comp_date, ind_comp_date)
        elif (sort_column == '4'):
            order_by = 'content_type__model'
        if (sort_direction == 'desc'):
            order_by = '-' + order_by
        if len(order_by) > 2:
            statuses = statuses.order_by(order_by)
        return statuses

    def json_response(self, data):
        return HttpResponse(
            json.dumps(data, cls=DjangoJSONEncoder),
            content_type='application/json'
        )


class SupervisorCompletedRequestsDatatable(DatatablesView):
    model = Status
    fields = (
        'object_id',
        'custom_request__name',
        'custom_request__completed_status__datetime',
        'content_type__model',
        'content_type__id',
        'request__first_name',
        'request__last_name',
        'corporate_request__company_name',
        'request__completed_status__datetime',
        'corporate_request__completed_status__datetime'
    )
    def get_row(self, row):
        # Setting the links to display the details for each row.
        if row['content_type__model'] == 'request':
            # grabbing id, and changing it do display_id
            request_id = row.pop('object_id')
            request = Request.objects.get(pk=request_id)

            # creating link
            request_url = reverse('request_supervisor', kwargs={"pk": request_id})
            display = "<a href=\"" + request_url + "\" class=\"btn btn-xs grey btn-editable\">  "+request.display_id+"</a>"
            row['object_id'] = display
            row['content_type__model'] = 'Individual'

            # Setting Name
            first_name = request.first_name
            last_name = request.last_name
            combo_name = first_name+" "+last_name
            row['custom_request__name'] = combo_name
            row['request__first_name'] = ''
            row['request__last_name'] = ''

            # Setting completed Date
            request_completed_status__datetime = row['request__completed_status__datetime']
            row['custom_request__completed_status__datetime'] = request_completed_status__datetime

            # setting report link
            report_url = reverse('report', kwargs={'company_date_id': request.report_url})
            row['content_type__model'] = "<a target=\"_blank\" download="+request.report_url+" href="+report_url+">"+request.report_url+"</a>"


        elif row['content_type__model'] == 'customrequest':
            request_id = row.pop('object_id')
            request = CustomRequest.objects.get(pk=request_id)
            request_url = reverse('request_supervisor_for_custom', kwargs={"pk": int(request_id)})
            display = "<a href=\"" + request_url + "\" class=\"btn btn-xs grey btn-editable\">"+request.display_id+"</a>"
            row['object_id'] = display

            #Setting report link
            report_url = reverse('custom_report', kwargs={'company_date_id': request.report_url})
            row['content_type__model'] = "<a target=\"_blank\" download="+request.report_url+" href="+report_url+">"+request.report_url+"</a>"



        elif row['content_type__model'] == 'corporaterequest':
            # Creating Link
            request_id = row.pop('object_id')
            request = CorporateRequest.objects.get(pk=request_id)
            request_url = reverse('request_supervisor_for_corporate', kwargs={"pk": int(request_id)})
            display = "<a href=\"" + request_url + "\" class=\"btn btn-xs grey btn-editable\">"+request.display_id+"</a>"
            row['object_id'] = display

            # setting request type
            row['content_type__model'] = 'Corporate'

            # Setting name
            row['custom_request__name'] = row['corporate_request__company_name']
            row['corporate_request__company_name'] = ''

            # Setting End Date
            corporate_request__completed_status__datetime = row['corporate_request__completed_status__datetime']
            row['custom_request__completed_status__datetime'] = corporate_request__completed_status__datetime

            # setting report link
            report_url = reverse('corporate_report', kwargs={'company_date_id': request.report_url})
            row['content_type__model'] = "<a target=\"_blank\" download="+request.report_url+" href="+report_url+">"+request.report_url+"</a>"

        # Setting supporting docs link
        try:
            row['content_type__id'] = "<a target='_blank' download="+request.display_id+"_supporting_doc"+" href="+request.attachment.url+">"+request.display_id+"_supporting_doc"+"</a>"
        except:
            row['content_type__id'] = ''

        datetime = row.pop('custom_request__completed_status__datetime')
        if datetime:
            cst_datetime = datetime.astimezone(timezone('US/Central'))
            formatted_date = formats.date_format(cst_datetime, "SHORT_DATETIME_FORMAT")
            row['custom_request__completed_status__datetime'] = formatted_date
        else:
            row['custom_request__completed_status__datetime'] = ""

        row['request__completed_status__datetime'] = ''
        row['corporate_request__completed_status__datetime'] = ''



        return super(SupervisorCompletedRequestsDatatable, self).get_row(row)

    def get_queryset(self):
        current_user = self.request.user
        search = self.request.GET['sSearch']
        try:
            sort = self.request.GET['iSortCol_0']
        except Exception, e:
            sort = None

        supervisor = get_company_employee(current_user)
        company = supervisor.company.name
        ids = list(Status.get_all_current_ids_queryset_for_company(company))


        '''
         Below is code to find submitted requests with there last completed date
        '''
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


        length = len(statuses)

        if length == 0:
            return Status.objects.none()

        if sort and length > 0:
            statuses = self.sort_supervisor_datatable(statuses)

        if (len(search) > 0):
            statuses = self.search_col_name(search, statuses) | self.search_col_id(search, statuses)

        return statuses

    def search_col_id(self, search, queryset):
        corp_set = queryset
        corp_set = corp_set.filter(corporate_request__display_id__icontains=search)

        ind_set = queryset
        ind_set = ind_set.filter(request__display_id__icontains=search)

        cust_set = queryset
        cust_set = cust_set.filter(custom_request__display_id__icontains=search)

        searched_set = cust_set | ind_set | corp_set
        return searched_set

    def search_col_name(self, search, queryset):
        corp_set = queryset
        corp_set = corp_set.filter(corporate_request__company_name__icontains=search)

        ind_set_first_name = queryset
        ind_set_last_name = queryset
        ind_set_first_name = ind_set_first_name.filter(request__first_name__icontains=search)
        ind_set_last_name = ind_set_last_name.filter(request__last_name__icontains=search)

        cust_set = queryset
        cust_set = cust_set.filter(custom_request__name__icontains=search)

        searched_set = corp_set | ind_set_first_name | ind_set_last_name | cust_set
        return searched_set

    def sort_supervisor_datatable(self, statuses):
        sort_column = self.request.GET['iSortCol_0']
        sort_direction = self.request.GET['sSortDir_0']
        order_by = ''
        if (sort_column == '0'):
            order_by = 'object_id'
        elif (sort_column == '1'):
            corp_name = 'corporate_request__company_name'
            cust_name = 'custom_request__name'
            ind_name = 'request__first_name'
            if (sort_direction == 'desc'):
                corp_name = '-' + corp_name
                cust_name = '-' + cust_name
                ind_name = '-' + ind_name
            statuses = statuses.order_by(corp_name, cust_name, ind_name)
        elif (sort_column == '2'):
            order_by = 'datetime'
        elif (sort_column == '3'):
            order_by = 'content_type'
        elif (sort_column == '4'):
            order_by = 'object_id'
        if (sort_direction == 'desc'):
            order_by = '-' + order_by
        if len(order_by) > 2:
            statuses = statuses.order_by(order_by)
        return statuses

    def json_response(self, data):
        return HttpResponse(
            json.dumps(data, cls=DjangoJSONEncoder),
            content_type='application/json'
        )


class SupervisorInProgressRequestsDatatable(DatatablesView):
    model = Status
    fields = (
        'object_id',
        'custom_request__name',
        'status',
        'datetime',
        'request__first_name',
        'request__last_name',
        'corporate_request__company_name',
        'content_type__model',
    )
    def get_row(self, row):
        # Setting the links to display the details for each row.
        if row['content_type__model'] == 'request':
            # grabbing id, and changing it do display_id
            request_id = row.pop('object_id')
            request = Request.objects.get(pk=request_id)

            # creating link
            request_url = reverse('request_supervisor', kwargs={"pk": request_id})
            display = "<a href=\"" + request_url + "\" class=\"btn btn-xs grey btn-editable\">  "+request.display_id+"</a>"
            row['object_id'] = display
            row['content_type__model'] = 'Individual'

            # Setting Name
            first_name = request.first_name
            last_name = request.last_name
            combo_name = first_name+" "+last_name
            row['custom_request__name'] = combo_name
            row['request__first_name'] = ''
            row['request__last_name'] = ''


        elif row['content_type__model'] == 'customrequest':
            request_id = row.pop('object_id')
            request_url = reverse('request_supervisor_for_custom', kwargs={"pk": int(request_id)})
            display = "<a href=\"" + request_url + "\" class=\"btn btn-xs grey btn-editable\">"+CustomRequest.objects.get(pk=request_id).display_id+"</a>"
            row['object_id'] = display
            row['content_type__model'] = 'Custom'

        elif row['content_type__model'] == 'corporaterequest':
            # Creating Link
            request_id = row.pop('object_id')
            request_url = reverse('request_supervisor_for_corporate', kwargs={"pk": int(request_id)})
            display = "<a href=\"" + request_url + "\" class=\"btn btn-xs grey btn-editable\">"+CorporateRequest.objects.get(pk=request_id).display_id+"</a>"
            row['object_id'] = display

            # setting request type
            row['content_type__model'] = 'Corporate'

            # Setting name
            row['custom_request__name'] = row['corporate_request__company_name']
            row['corporate_request__company_name'] = ''

        status = row.pop('status')
        print "status: ",status
        if status == 0 or status == 4:
            display_status = "Quality Check"
        else:
            display_status = Status.SUPERVISOR_STATUS_CHOICES[status]
        row['status'] = display_status


        datetime = row.pop('datetime')
        cst_datetime = datetime.astimezone(timezone('US/Central'))
        formatted_date = formats.date_format(cst_datetime, "SHORT_DATETIME_FORMAT")
        row['datetime'] = formatted_date

        row['content_type__model'] = ''

        return super(SupervisorInProgressRequestsDatatable, self).get_row(row)

    def get_queryset(self):
        current_user = self.request.user
        search = self.request.GET['sSearch']
        try:
            sort = self.request.GET['iSortCol_0']
        except Exception, e:
            sort = None

        supervisor = get_company_employee(current_user)
        company = supervisor.company.name
        ids = list(Status.get_all_current_ids_queryset_for_company(company))

        in_prog_statuses = [Status.NEW_STATUS, Status.ASSIGNED_STATUS, Status.IN_PROGRESS_STATUS,
                            Status.COMPLETED_STATUS, Status.REJECTED_STATUS, Status.REJECTED_STATUS,
                            Status.INCOMPLETE_STATUS, Status.NEW_RETURNED_STATUS, Status.REVIEW_STATUS,Status.AWAITING_DATA_FORM_APPROVAL]

        statuses = Status.objects.filter(id__in=ids, status__in=in_prog_statuses)

        length = len(statuses)

        if length == 0:
            return Status.objects.none()

        if sort and length > 0:
            statuses = self.sort_supervisor_datatable(statuses)

        if (len(search) > 0):
            statuses = self.search_col_name(search, statuses) | self.search_col_id(search, statuses)

        return statuses

    def search_col_id(self, search, queryset):
        corp_set = queryset
        corp_set = corp_set.filter(corporate_request__display_id__icontains=search)

        ind_set = queryset
        ind_set = ind_set.filter(request__display_id__icontains=search)

        cust_set = queryset
        cust_set = cust_set.filter(custom_request__display_id__icontains=search)

        searched_set = cust_set | ind_set | corp_set
        return searched_set

    def search_col_name(self, search, queryset):
        corp_set = queryset
        corp_set = corp_set.filter(corporate_request__company_name__icontains=search)

        ind_set_first_name = queryset
        ind_set_last_name = queryset
        ind_set_first_name = ind_set_first_name.filter(request__first_name__icontains=search)
        ind_set_last_name = ind_set_last_name.filter(request__last_name__icontains=search)

        cust_set = queryset
        cust_set = cust_set.filter(custom_request__name__icontains=search)

        searched_set = corp_set | ind_set_first_name | ind_set_last_name | cust_set
        return searched_set

    def sort_supervisor_datatable(self, statuses):
        sort_column = self.request.GET['iSortCol_0']
        sort_direction = self.request.GET['sSortDir_0']
        order_by = ''
        if (sort_column == '0'):
            order_by = 'object_id'
        elif (sort_column == '1'):
            corp_name = 'corporate_request__company_name'
            cust_name = 'custom_request__name'
            ind_name = 'request__first_name'
            if (sort_direction == 'desc'):
                corp_name = '-' + corp_name
                cust_name = '-' + cust_name
                ind_name = '-' + ind_name
            statuses = statuses.order_by(corp_name, cust_name, ind_name)
        elif (sort_column == '2'):
            statuses = sort_statuses(statuses,sort_direction)
        elif (sort_column == '3'):
            order_by = 'datetime'
        if (sort_direction == 'desc'):
            order_by = '-' + order_by
        if len(order_by) > 2:
            statuses = statuses.order_by(order_by)

        return statuses

    def json_response(self, data):
        return HttpResponse(
            json.dumps(data, cls=DjangoJSONEncoder),
            content_type='application/json'
        )


class SupervisorReportsDatatablesView(DatatablesView):
    model = Status
    fields = (
        'id',
        'object_id',
        'custom_request__name',
        'datetime',
        'request__first_name',
        'request__last_name',
        'corporate_request__company_name',
        'content_type__model',

    )

    def get_row(self, row):
        # Setting the links to display the details for each row.
        if row['content_type__model'] == 'request':
            # grabbing id, and changing it do display_id
            request_id = row.pop('object_id')
            request = Request.objects.get(pk=request_id)

            # creating link
            row['id'] = "<input id=\""+"check-"+str(request_id)+"\" style=\"width: 20px; height: 20px;\" type=\"checkbox\" name=\"requests\" value=\""+str(request_id)+"\">"+"</input>"
            display = request.display_id
            row['object_id'] = display
            row['content_type__model'] = 'Individual'

            # Setting Name
            first_name = request.first_name
            last_name = request.last_name
            combo_name = first_name+" "+last_name
            row['custom_request__name'] = combo_name
            row['request__first_name'] = ''
            row['request__last_name'] = ''

        elif row['content_type__model'] == 'customrequest':
            request_id = row.pop('object_id')
            row['id'] = "<input id=\""+"check-"+str(request_id)+"\" style=\"width: 20px; height: 20px;\" type=\"checkbox\" name=\"requests\" value=\""+str(request_id)+"\">"+"</input>"
            display = CustomRequest.objects.get(pk=request_id).display_id
            row['object_id'] = display
            row['content_type__model'] = 'Custom'

        elif row['content_type__model'] == 'corporaterequest':
            request_id = row.pop('object_id')
            row['id'] = "<input id=\""+"check-"+str(request_id)+"\" style=\"width: 20px; height: 20px;\" type=\"checkbox\" name=\"requests\" value=\""+str(request_id)+"\">"+"</input>"
            display = CorporateRequest.objects.get(pk=request_id).display_id
            row['object_id'] = display
            row['content_type__model'] = 'Corporate'
            row['custom_request__name'] = row['corporate_request__company_name']
            row['corporate_request__company_name'] = ''
        row['content_type__model'] = ''
        datetime = row.pop('datetime')
        cst_datetime = datetime.astimezone(timezone('US/Central'))
        formatted_date = formats.date_format(cst_datetime, "SHORT_DATETIME_FORMAT")
        row['datetime'] = formatted_date




        return super(SupervisorReportsDatatablesView, self).get_row(row)

    def get_queryset(self):
        current_user = self.request.user
        try:
            sort = self.request.GET['iSortCol_0']
        except Exception, e:
            sort = None

        supervisor = get_company_employee(current_user)
        company = supervisor.company.name
        ids = list(Status.get_all_current_ids_queryset_for_company(company))
        statuses = Status.objects.filter(id__in=ids, status=Status.SUBMITTED_STATUS)

        length = len(statuses)

        if length == 0:
            return Status.objects.none()

        if sort and length > 0:
            statuses = self.sort_supervisor_datatable(statuses)



        # ID
        id_search = ifCustomReturnVal(self.request.GET['sSearch_0'])
        if (len(id_search) > 0):
            cust_id_filt = statuses.filter(custom_request__display_id__icontains=id_search)
            corp_id_filt = statuses.filter(corporate_request__display_id__icontains=id_search)
            ind_id_filt = statuses.filter(request__display_id__icontains=id_search)
            statuses = cust_id_filt | corp_id_filt | ind_id_filt

        # NAME
        name_search = ifCustomReturnVal(self.request.GET['sSearch_1'])
        if (len(name_search) > 0):
            cust_name = statuses.filter(custom_request__name__icontains=name_search)
            corp_name = statuses.filter(corporate_request__company_name__icontains=name_search)
            ind_first_name = statuses.filter(request__first_name__icontains=name_search)
            ind_last_name = statuses.filter(request__last_name__icontains=name_search)
            statuses = cust_name | corp_name | ind_first_name | ind_last_name


        # Created By
        created_by_id = ifCustomReturnVal(self.request.GET['sSearch_2'])
        if (len(created_by_id) > 0):
            cust_ids = statuses.filter(custom_request__created_by__user__id=created_by_id).values_list('id', flat=True)
            corp_ids = statuses.filter(corporate_request__created_by__user__id=created_by_id).values_list('id', flat=True)
            ind_ids = statuses.filter(request__created_by__user__id=created_by_id).values_list('id', flat=True)
            comb_ids = list(chain(cust_ids, corp_ids, ind_ids))
            statuses = statuses.filter(id__in=comb_ids)


        # STATUS
        status_search = ifCustomReturnVal(self.request.GET['sSearch_3'])
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
        type_search = ifCustomReturnVal(self.request.GET['sSearch_4'])
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
        start_end_date = self.request.GET['sSearch_5']
        if (len(start_end_date) > 3):
            array = start_end_date.split('+')
            start = fix_start(array[0])
            end = fix_end(array[1])
            statuses = statuses.filter(id__in=ids).filter(datetime__range=[start, end])


        # CUSTOM FIELD
        custom_field = ifCustomReturnVal(self.request.GET['sSearch_7'])
        if (len(custom_field) > 0):
            field_ids = list(
                CustomRequestFields.objects.filter(custom_request__dynamic_request_form__render_form=True,
                                                   form_field__id=custom_field).exclude(
                    value__isnull=True).exclude(value__exact='').values_list('custom_request__id', flat=True))

            statuses = statuses.filter(custom_request__id__in=field_ids)


        # CUSTOM FIELD VALUE
        custom_field_value = ifCustomReturnVal(self.request.GET['sSearch_8'])
        if (len(custom_field_value) > 0):
            field_ids = list(
                CustomRequestFields.objects.filter(custom_request__dynamic_request_form__render_form=True,
                                                   value__icontains=custom_field_value).values_list(
                                                    'custom_request__id', flat=True))
            statuses = statuses.filter(custom_request__id__in=field_ids)

        # FORM NAME
        dynamic_request_form_id = ifCustomReturnVal(self.request.GET['sSearch_9'])
        if (len(dynamic_request_form_id) > 0):
            statuses = statuses.filter(custom_request__dynamic_request_form__id=dynamic_request_form_id)


        # REQUEST TYPE
        request_type = ifCustomReturnVal(self.request.GET['sSearch_10'])
        if len(request_type) > 0:
            statuses = statuses.filter(content_type__model=request_type)

        return statuses


    def sort_supervisor_datatable(self, statuses):
        sort_column = self.request.GET['iSortCol_0']
        sort_direction = self.request.GET['sSortDir_0']
        order_by = ''
        if (sort_column == '0'):
            order_by = 'object_id'
        elif (sort_column == '1'):
            order_by = 'object_id'
        elif (sort_column == '2'):
            corp_name = 'corporate_request__company_name'
            cust_name = 'custom_request__name'
            ind_name = 'request__first_name'
            if (sort_direction == 'desc'):
                corp_name = '-' + corp_name
                cust_name = '-' + cust_name
                ind_name = '-' + ind_name
            statuses = statuses.order_by(corp_name, cust_name, ind_name)


        # elif (sort_column == '3'):
        #     order_by = 'status'
        elif (sort_column == '3'):
            order_by = 'datetime'
            # date = 'datetime'

            # Below is code to change  this to sort on completed dates and all other dates
            # cust_comp_date = 'custom_request__completed_status__datetime'
            # corp_comp_date = 'corporate_request__completed_status__datetime'
            # ind_comp_date = 'request__completed_status__datetime'
            # if (sort_direction == 'desc'):
            #     date = '-' + date
            #     cust_comp_date = '-' + cust_comp_date
            #     corp_comp_date = '-' + corp_comp_date
            #     ind_comp_date = '-' + ind_comp_date
            # statuses = statuses.order_by(date, cust_comp_date, corp_comp_date, ind_comp_date)
        # elif (sort_column == '5'):
        #     order_by = 'content_type__model'
        if (sort_direction == 'desc'):
            order_by = '-' + order_by
        if len(order_by) > 2:
            statuses = statuses.order_by(order_by)
        return statuses

    def json_response(self, data):
        return HttpResponse(
            json.dumps(data, cls=DjangoJSONEncoder),
            content_type='application/json'
        )


###
# EMPLOYEE
###
class EmployeeCompletedRequestsDatatable(DatatablesView):
    model = Status
    fields = (
        'object_id',
        'custom_request__name',
        'custom_request__completed_status__datetime',
        'content_type__model',
        'content_type__id',
        'request__first_name',
        'request__last_name',
        'corporate_request__company_name',
        'request__completed_status__datetime',
        'corporate_request__completed_status__datetime'
    )
    def get_row(self, row):
        # Setting the links to display the details for each row.
        if row['content_type__model'] == 'request':
            # grabbing id, and changing it do display_id
            request_id = row.pop('object_id')
            request = Request.objects.get(pk=request_id)

            # creating link
            request_url = reverse('request_employee', kwargs={"pk": request_id})
            display = "<a href=\"" + request_url + "\" class=\"btn btn-xs grey btn-editable\">  "+request.display_id+"</a>"
            row['object_id'] = display
            row['content_type__model'] = 'Individual'

            # Setting Name
            first_name = request.first_name
            last_name = request.last_name
            combo_name = first_name+" "+last_name
            row['custom_request__name'] = combo_name
            row['request__first_name'] = ''
            row['request__last_name'] = ''

            # Setting completed Date
            request_completed_status__datetime = row['request__completed_status__datetime']
            row['custom_request__completed_status__datetime'] = request_completed_status__datetime

            # setting report link
            report_url = reverse('report', kwargs={'company_date_id': request.report_url})
            row['content_type__model'] = "<a target=\"_blank\" download="+request.report_url+" href="+report_url+">"+request.report_url+"</a>"


        elif row['content_type__model'] == 'customrequest':
            request_id = row.pop('object_id')
            request = CustomRequest.objects.get(pk=request_id)
            request_url = reverse('request_employee_for_custom', kwargs={"pk": int(request_id)})
            display = "<a href=\"" + request_url + "\" class=\"btn btn-xs grey btn-editable\">"+request.display_id+"</a>"
            row['object_id'] = display

            #Setting report link
            report_url = reverse('custom_report', kwargs={'company_date_id': request.report_url})
            row['content_type__model'] = "<a target=\"_blank\" download="+request.report_url+" href="+report_url+">"+request.report_url+"</a>"



        elif row['content_type__model'] == 'corporaterequest':
            # Creating Link
            request_id = row.pop('object_id')
            request = CorporateRequest.objects.get(pk=request_id)
            request_url = reverse('request_employee_for_corporate', kwargs={"pk": int(request_id)})
            display = "<a href=\"" + request_url + "\" class=\"btn btn-xs grey btn-editable\">"+request.display_id+"</a>"
            row['object_id'] = display

            # setting request type
            row['content_type__model'] = 'Corporate'

            # Setting name
            row['custom_request__name'] = row['corporate_request__company_name']
            row['corporate_request__company_name'] = ''

            # Setting End Date
            corporate_request__completed_status__datetime = row['corporate_request__completed_status__datetime']
            row['custom_request__completed_status__datetime'] = corporate_request__completed_status__datetime

            # setting report link
            report_url = reverse('corporate_report', kwargs={'company_date_id': request.report_url})
            row['content_type__model'] = "<a target=\"_blank\" download="+request.report_url+" href="+report_url+">"+request.report_url+"</a>"

        # Setting supporting docs link
        try:
            row['content_type__id'] = "<a target='_blank' download="+request.display_id+"_supporting_doc"+" href="+request.attachment.url+">"+request.display_id+"_supporting_doc"+"</a>"
        except:
            row['content_type__id'] = ''

        datetime = row.pop('custom_request__completed_status__datetime')
        cst_datetime = datetime.astimezone(timezone('US/Central'))
        formatted_date = formats.date_format(cst_datetime, "SHORT_DATETIME_FORMAT")
        row['custom_request__completed_status__datetime'] = formatted_date

        row['request__completed_status__datetime'] = ''
        row['corporate_request__completed_status__datetime'] = ''



        return super(EmployeeCompletedRequestsDatatable, self).get_row(row)

    def get_queryset(self):
        current_user = self.request.user
        search = self.request.GET['sSearch']
        try:
            sort = self.request.GET['iSortCol_0']
        except Exception, e:
            sort = None

        ids = list(Status.get_all_current_ids_queryset_for_user(current_user))


        '''
         Below is code to find submitted requests with there last completed date
        '''
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


        length = len(statuses)

        if length == 0:
            return Status.objects.none()

        if sort and length > 0:
            statuses = self.sort_employee_datatable(statuses)

        if (len(search) > 0):
            statuses = self.search_col_name(search, statuses) | self.search_col_id(search, statuses)

        return statuses

    def search_col_id(self, search, queryset):
        corp_set = queryset
        corp_set = corp_set.filter(corporate_request__display_id__icontains=search)

        ind_set = queryset
        ind_set = ind_set.filter(request__display_id__icontains=search)

        cust_set = queryset
        cust_set = cust_set.filter(custom_request__display_id__icontains=search)

        searched_set = cust_set | ind_set | corp_set
        return searched_set

    def search_col_name(self, search, queryset):
        corp_set = queryset
        corp_set = corp_set.filter(corporate_request__company_name__icontains=search)

        ind_set_first_name = queryset
        ind_set_last_name = queryset
        ind_set_first_name = ind_set_first_name.filter(request__first_name__icontains=search)
        ind_set_last_name = ind_set_last_name.filter(request__last_name__icontains=search)

        cust_set = queryset
        cust_set = cust_set.filter(custom_request__name__icontains=search)

        searched_set = corp_set | ind_set_first_name | ind_set_last_name | cust_set
        return searched_set

    def sort_employee_datatable(self, statuses):
        sort_column = self.request.GET['iSortCol_0']
        sort_direction = self.request.GET['sSortDir_0']
        order_by = ''
        if (sort_column == '0'):
            order_by = 'object_id'
        elif (sort_column == '1'):
            corp_name = 'corporate_request__company_name'
            cust_name = 'custom_request__name'
            ind_name = 'request__first_name'
            if (sort_direction == 'desc'):
                corp_name = '-' + corp_name
                cust_name = '-' + cust_name
                ind_name = '-' + ind_name
            statuses = statuses.order_by(corp_name, cust_name, ind_name)
        elif (sort_column == '2'):
            order_by = 'datetime'
        elif (sort_column == '3'):
            order_by = 'content_type'
        elif (sort_column == '4'):
            order_by = 'object_id'
        if (sort_direction == 'desc'):
            order_by = '-' + order_by
        if len(order_by) > 2:
            statuses = statuses.order_by(order_by)
        return statuses

    def json_response(self, data):
        return HttpResponse(
            json.dumps(data, cls=DjangoJSONEncoder),
            content_type='application/json'
        )


class RestrictedAttachments(DatatablesView):
    model = Status
    fields = (
        'object_id',
        'custom_request__name',
        'custom_request__completed_status__datetime',
        'content_type__model',
        'request__first_name',
        'request__last_name',
        'corporate_request__company_name',
        'request__completed_status__datetime',
        'corporate_request__completed_status__datetime'
    )

    def get_row(self, row):
        # Setting the links to display the details for each row.
        if row['content_type__model'] == 'request':
            # grabbing id, and changing it do display_id
            request_id = row.pop('object_id')
            request = Request.objects.get(pk=request_id)

            # creating link
            request_url = reverse('request_employee', kwargs={"pk": request_id})
            display = "<a href=\"" + request_url + "\" class=\"btn btn-xs grey btn-editable\">  "+request.display_id+"</a>"
            row['object_id'] = display
            row['content_type__model'] = 'Individual'

            # Setting Name
            first_name = request.first_name
            last_name = request.last_name
            combo_name = first_name+" "+last_name
            row['custom_request__name'] = combo_name
            row['request__first_name'] = ''
            row['request__last_name'] = ''

            # Setting completed Date
            request_completed_status__datetime = row['request__completed_status__datetime']
            row['custom_request__completed_status__datetime'] = request_completed_status__datetime

            # setting report link
            report_url = reverse('report', kwargs={'company_date_id': request.report_url})
            row['content_type__model'] = "<a target=\"_blank\" download="+request.report_url+" href="+report_url+">"+request.report_url+"</a>"

        elif row['content_type__model'] == 'customrequest':
            request_id = row.pop('object_id')
            request = CustomRequest.objects.get(pk=request_id)
            request_url = reverse('request_employee_for_custom', kwargs={"pk": int(request_id)})
            display = "<a href=\"" + request_url + "\" class=\"btn btn-xs grey btn-editable\">"+request.display_id+"</a>"
            row['object_id'] = display

            # Setting report link
            report_url = reverse('custom_report', kwargs={'company_date_id': request.report_url})
            row['content_type__model'] = "<a target=\"_blank\" download="+request.report_url+" href="+report_url+">"+request.report_url+"</a>"

        elif row['content_type__model'] == 'corporaterequest':
            # Creating Link
            request_id = row.pop('object_id')
            request = CorporateRequest.objects.get(pk=request_id)
            request_url = reverse('request_employee_for_corporate', kwargs={"pk": int(request_id)})
            display = "<a href=\"" + request_url + "\" class=\"btn btn-xs grey btn-editable\">"+request.display_id+"</a>"
            row['object_id'] = display

            # setting request type
            row['content_type__model'] = 'Corporate'

            # Setting name
            row['custom_request__name'] = row['corporate_request__company_name']
            row['corporate_request__company_name'] = ''

            # Setting End Date
            corporate_request__completed_status__datetime = row['corporate_request__completed_status__datetime']
            row['custom_request__completed_status__datetime'] = corporate_request__completed_status__datetime

            # setting report link
            report_url = reverse('corporate_report', kwargs={'company_date_id': request.report_url})
            row['content_type__model'] = "<a target=\"_blank\" download="+request.report_url+" href="+report_url+">"+request.report_url+"</a>"

        datetime = row.pop('custom_request__completed_status__datetime')
        cst_datetime = datetime.astimezone(timezone('US/Central'))
        formatted_date = formats.date_format(cst_datetime, "SHORT_DATETIME_FORMAT")
        row['custom_request__completed_status__datetime'] = formatted_date

        row['request__completed_status__datetime'] = ''
        row['corporate_request__completed_status__datetime'] = ''

        return super(RestrictedAttachments, self).get_row(row)
    def get_queryset(self):
        current_user = self.request.user
        search = self.request.GET['sSearch']
        try:
            sort = self.request.GET['iSortCol_0']
        except Exception, e:
            sort = None

        ids = list(Status.get_all_current_ids_queryset_for_user(current_user))


        '''
         Below is code to find submitted requests with there last completed date
        '''
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


        length = len(statuses)

        if length == 0:
            return Status.objects.none()

        if sort and length > 0:
            statuses = self.sort_employee_datatable(statuses)

        if (len(search) > 0):
            statuses = self.search_col_name(search, statuses) | self.search_col_id(search, statuses)

        return statuses

    def search_col_id(self, search, queryset):
        corp_set = queryset
        corp_set = corp_set.filter(corporate_request__display_id__icontains=search)

        ind_set = queryset
        ind_set = ind_set.filter(request__display_id__icontains=search)

        cust_set = queryset
        cust_set = cust_set.filter(custom_request__display_id__icontains=search)

        searched_set = cust_set | ind_set | corp_set
        return searched_set

    def search_col_name(self, search, queryset):
        corp_set = queryset
        corp_set = corp_set.filter(corporate_request__company_name__icontains=search)

        ind_set_first_name = queryset
        ind_set_last_name = queryset
        ind_set_first_name = ind_set_first_name.filter(request__first_name__icontains=search)
        ind_set_last_name = ind_set_last_name.filter(request__last_name__icontains=search)

        cust_set = queryset
        cust_set = cust_set.filter(custom_request__name__icontains=search)

        searched_set = corp_set | ind_set_first_name | ind_set_last_name | cust_set
        return searched_set

    def sort_employee_datatable(self, statuses):
        sort_column = self.request.GET['iSortCol_0']
        sort_direction = self.request.GET['sSortDir_0']
        order_by = ''
        if (sort_column == '0'):
            order_by = 'object_id'
        elif (sort_column == '1'):
            corp_name = 'corporate_request__company_name'
            cust_name = 'custom_request__name'
            ind_name = 'request__first_name'
            if (sort_direction == 'desc'):
                corp_name = '-' + corp_name
                cust_name = '-' + cust_name
                ind_name = '-' + ind_name
            statuses = statuses.order_by(corp_name, cust_name, ind_name)
        elif (sort_column == '2'):
            order_by = 'datetime'
        elif (sort_column == '3'):
            order_by = 'content_type'
        elif (sort_column == '4'):
            order_by = 'object_id'
        if (sort_direction == 'desc'):
            order_by = '-' + order_by
        if len(order_by) > 2:
            statuses = statuses.order_by(order_by)
        return statuses

    def json_response(self, data):
        return HttpResponse(
            json.dumps(data, cls=DjangoJSONEncoder),
            content_type='application/json'
        )


class EmployeeAllRequestsDatatablesView(DatatablesView):
    model = Status
    fields = (
        'object_id',
        'custom_request__name',
        'status',
        'datetime',
        'content_type__model',
        'request__first_name',
        'request__last_name',
        'corporate_request__company_name',
    )

    def get_row(self, row):
        # Setting the links to display the details for each row.
        if row['content_type__model'] == 'request':
            # grabbing id, and changing it do display_id
            request_id = row.pop('object_id')
            request = Request.objects.get(pk=request_id)

            # creating link
            request_url = reverse('request_employee', kwargs={"pk": request_id})
            display = "<a href=\"" + request_url + "\" class=\"btn btn-xs grey btn-editable\">  "+request.display_id+"</a>"
            row['object_id'] = display
            row['content_type__model'] = 'Individual'

            # Setting Name
            first_name = request.first_name
            last_name = request.last_name
            combo_name = first_name+" "+last_name
            row['custom_request__name'] = combo_name
            row['request__first_name'] = ''
            row['request__last_name'] = ''
            # if row['status'] == Status.SUBMITTED_STATUS:
            #     row['datetime'] = row['request__completed_status__datetime']

        elif row['content_type__model'] == 'customrequest':
            request_id = row.pop('object_id')
            request_url = reverse('request_employee_for_custom', kwargs={"pk": int(request_id)})
            display = "<a href=\"" + request_url + "\" class=\"btn btn-xs grey btn-editable\">"+CustomRequest.objects.get(pk=request_id).display_id+"</a>"
            row['object_id'] = display
            row['content_type__model'] = 'Custom'
            # if row['status'] == Status.SUBMITTED_STATUS:
            #     row['datetime'] =row['custom_request__completed_status__datetime']

        elif row['content_type__model'] == 'corporaterequest':
            request_id = row.pop('object_id')
            request_url = reverse('request_employee_for_corporate', kwargs={"pk": int(request_id)})
            display = "<a href=\"" + request_url + "\" class=\"btn btn-xs grey btn-editable\">"+CorporateRequest.objects.get(pk=request_id).display_id+"</a>"
            row['object_id'] = display
            row['content_type__model'] = 'Corporate'
            row['custom_request__name'] = row['corporate_request__company_name']
            row['corporate_request__company_name'] = ''
            # if row['status'] == Status.SUBMITTED_STATUS:
            #     row['datetime'] = row['corporate_request__completed_status__datetime']

        status = row.pop('status')
        display_status = Status.SUPERVISOR_STATUS_CHOICES[status]
        row['status'] = display_status

        datetime = row.pop('datetime')
        cst_datetime = datetime.astimezone(timezone('US/Central'))
        formatted_date = formats.date_format(cst_datetime, "SHORT_DATETIME_FORMAT")
        row['datetime'] = formatted_date


        return super(EmployeeAllRequestsDatatablesView, self).get_row(row)

    def get_queryset(self):
        current_user = self.request.user
        search = self.request.GET['sSearch']
        try:
            sort = self.request.GET['iSortCol_0']
        except Exception, e:
            sort = None

        supervisor = get_company_employee(current_user)
        company = supervisor.company.name

        ids = list(Status.get_all_current_ids_queryset_for_user(current_user))

        statuses = Status.objects.filter(id__in=ids)

        length = len(statuses)

        if length == 0:
            return Status.objects.none()

        if sort and length > 0:
            statuses = self.sort_supervisor_datatable(statuses)

        if (len(search) > 0):
            statuses = self.search_col_name(search, statuses) | self.search_col_id(search, statuses)

        # ID
        id_search = ifCustomReturnVal(self.request.GET['sSearch_0'])
        if (len(id_search) > 0):
            cust_id_filt = statuses.filter(custom_request__display_id__icontains=id_search)
            corp_id_filt = statuses.filter(corporate_request__display_id__icontains=id_search)
            ind_id_filt = statuses.filter(request__display_id__icontains=id_search)
            statuses = cust_id_filt | corp_id_filt | ind_id_filt

        # NAME
        name_search = ifCustomReturnVal(self.request.GET['sSearch_1'])
        if (len(name_search) > 0):
            cust_name = statuses.filter(custom_request__name__icontains=name_search)
            corp_name = statuses.filter(corporate_request__company_name__icontains=name_search)
            ind_first_name = statuses.filter(request__first_name__icontains=name_search)
            ind_last_name = statuses.filter(request__last_name__icontains=name_search)
            statuses = cust_name | corp_name | ind_first_name | ind_last_name


        # Created By
        # created_by_id = ifCustomReturnVal(self.request.GET['sSearch_2'])
        # if (len(created_by_id) > 0):
        #     cust_ids = statuses.filter(custom_request__created_by__user__id=created_by_id).values_list('id', flat=True)
        #     corp_ids = statuses.filter(corporate_request__created_by__user__id=created_by_id).values_list('id', flat=True)
        #     ind_ids = statuses.filter(request__created_by__user__id=created_by_id).values_list('id', flat=True)
        #     comb_ids = list(chain(cust_ids, corp_ids, ind_ids))
        #     statuses = statuses.filter(id__in=comb_ids)


        # STATUS
        status_search = ifCustomReturnVal(self.request.GET['sSearch_3'])
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
            elif int(status_search) == Status.ARCHIVED_STATUS:
                supervisor_search_statuses = [Status.ARCHIVED_STATUS]

            statuses = statuses.filter(status__in=supervisor_search_statuses)


        # TYPE
        type_search = ifCustomReturnVal(self.request.GET['sSearch_4'])
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
        start_end_date = self.request.GET['sSearch_5']
        if (len(start_end_date) > 3):
            array = start_end_date.split('+')
            start = fix_start(array[0])
            end = fix_end(array[1])
            statuses = statuses.filter(id__in=ids).filter(datetime__range=[start, end])


        # CUSTOM FIELD
        custom_field = ifCustomReturnVal(self.request.GET['sSearch_7'])
        if (len(custom_field) > 0):
            field_ids = list(
                CustomRequestFields.objects.filter(custom_request__dynamic_request_form__render_form=True,
                                                   form_field__id=custom_field).exclude(
                    value__isnull=True).exclude(value__exact='').values_list('custom_request__id', flat=True))

            statuses = statuses.filter(custom_request__id__in=field_ids)


        # CUSTOM FIELD VALUE
        custom_field_value = ifCustomReturnVal(self.request.GET['sSearch_8'])
        if (len(custom_field_value) > 0):
            field_ids = list(
                CustomRequestFields.objects.filter(custom_request__dynamic_request_form__render_form=True,
                                                   value__icontains=custom_field_value).values_list(
                                                    'custom_request__id', flat=True))
            statuses = statuses.filter(custom_request__id__in=field_ids)

        # FORM NAME
        dynamic_request_form_id = ifCustomReturnVal(self.request.GET['sSearch_9'])
        if (len(dynamic_request_form_id) > 0):
            statuses = statuses.filter(custom_request__dynamic_request_form__id=dynamic_request_form_id)


        # REQUEST TYPE
        request_type = ifCustomReturnVal(self.request.GET['sSearch_10'])
        if len(request_type) > 0:
            statuses = statuses.filter(content_type__model=request_type)


        return statuses

    def search_col_id(self, search, queryset):
        corp_set = queryset
        corp_set = corp_set.filter(corporate_request__display_id__icontains=search)

        ind_set = queryset
        ind_set = ind_set.filter(request__display_id__icontains=search)

        cust_set = queryset
        cust_set = cust_set.filter(custom_request__display_id__icontains=search)

        searched_set = cust_set | ind_set | corp_set
        return searched_set

    def search_col_name(self, search, queryset):
        corp_set = queryset
        corp_set = corp_set.filter(corporate_request__company_name__icontains=search)

        ind_set_first_name = queryset
        ind_set_last_name = queryset
        ind_set_first_name = ind_set_first_name.filter(request__first_name__icontains=search)
        ind_set_last_name = ind_set_last_name.filter(request__last_name__icontains=search)

        cust_set = queryset
        cust_set = cust_set.filter(custom_request__name__icontains=search)

        searched_set = corp_set | ind_set_first_name | ind_set_last_name | cust_set
        return searched_set

    def sort_supervisor_datatable(self, statuses):
        sort_column = self.request.GET['iSortCol_0']
        sort_direction = self.request.GET['sSortDir_0']
        order_by = ''
        if (sort_column == '0'):
            order_by = 'object_id'
        elif (sort_column == '1'):
            corp_name = 'corporate_request__company_name'
            cust_name = 'custom_request__name'
            ind_name = 'request__first_name'
            if (sort_direction == 'desc'):
                corp_name = '-' + corp_name
                cust_name = '-' + cust_name
                ind_name = '-' + ind_name
            statuses = statuses.order_by(corp_name, cust_name, ind_name)


        elif (sort_column == '2'):
            statuses = sort_statuses(statuses,sort_direction)
        elif (sort_column == '3'):
            date = 'datetime'
            # Below is code to change  this to sort on completed dates and all other dates
            # cust_comp_date = 'custom_request__completed_status__datetime'
            # corp_comp_date = 'corporate_request__completed_status__datetime'
            # ind_comp_date = 'request__completed_status__datetime'
            # if (sort_direction == 'desc'):
            #     date = '-' + date
            #     cust_comp_date = '-' + cust_comp_date
            #     corp_comp_date = '-' + corp_comp_date
            #     ind_comp_date = '-' + ind_comp_date
            # statuses = statuses.order_by(date, cust_comp_date, corp_comp_date, ind_comp_date)
        elif (sort_column == '4'):
            order_by = 'content_type__model'
        if (sort_direction == 'desc'):
            order_by = '-' + order_by
        if len(order_by) > 2:
            statuses = statuses.order_by(order_by)
        return statuses

    def json_response(self, data):
        return HttpResponse(
            json.dumps(data, cls=DjangoJSONEncoder),
            content_type='application/json'
        )


class EmployeeInProgressRequestsDatatable(DatatablesView):
    model = Status
    fields = (
        'object_id',
        'custom_request__name',
        'status',
        'datetime',
        'request__first_name',
        'request__last_name',
        'corporate_request__company_name',
        'content_type__model',
    )
    def get_row(self, row):
        # Setting the links to display the details for each row.
        if row['content_type__model'] == 'request':
            # grabbing id, and changing it do display_id
            request_id = row.pop('object_id')
            request = Request.objects.get(pk=request_id)

            # creating link
            request_url = reverse('request_employee', kwargs={"pk": request_id})
            display = "<a href=\"" + request_url + "\" class=\"btn btn-xs grey btn-editable\">  "+request.display_id+"</a>"
            row['object_id'] = display
            row['content_type__model'] = 'Individual'

            # Setting Name
            first_name = request.first_name
            last_name = request.last_name
            combo_name = first_name+" "+last_name
            row['custom_request__name'] = combo_name
            row['request__first_name'] = ''
            row['request__last_name'] = ''


        elif row['content_type__model'] == 'customrequest':
            request_id = row.pop('object_id')
            request_url = reverse('request_employee_for_custom', kwargs={"pk": int(request_id)})
            display = "<a href=\"" + request_url + "\" class=\"btn btn-xs grey btn-editable\">"+CustomRequest.objects.get(pk=request_id).display_id+"</a>"
            row['object_id'] = display
            row['content_type__model'] = 'Custom'

        elif row['content_type__model'] == 'corporaterequest':
            # Creating Link
            request_id = row.pop('object_id')
            request_url = reverse('request_employee_for_corporate', kwargs={"pk": int(request_id)})
            display = "<a href=\"" + request_url + "\" class=\"btn btn-xs grey btn-editable\">"+CorporateRequest.objects.get(pk=request_id).display_id+"</a>"
            row['object_id'] = display

            # setting request type
            row['content_type__model'] = 'Corporate'

            # Setting name
            row['custom_request__name'] = row['corporate_request__company_name']
            row['corporate_request__company_name'] = ''

        status = row.pop('status')
        if status == 0 or status == 4:
            display_status = "Quality Check"
        else:
            display_status = Status.SUPERVISOR_STATUS_CHOICES[status]
        row['status'] = display_status


        datetime = row.pop('datetime')
        cst_datetime = datetime.astimezone(timezone('US/Central'))
        formatted_date = formats.date_format(cst_datetime, "SHORT_DATETIME_FORMAT")
        row['datetime'] = formatted_date

        row['content_type__model'] = ''

        return super(EmployeeInProgressRequestsDatatable, self).get_row(row)

    def get_queryset(self):
        current_user = self.request.user
        search = self.request.GET['sSearch']
        try:
            sort = self.request.GET['iSortCol_0']
        except Exception, e:
            sort = None

        ids = list(Status.get_all_current_ids_queryset_for_user(current_user))
        in_prog_statuses = [Status.NEW_STATUS, Status.ASSIGNED_STATUS, Status.IN_PROGRESS_STATUS,
                            Status.COMPLETED_STATUS, Status.REJECTED_STATUS, Status.REJECTED_STATUS,
                            Status.INCOMPLETE_STATUS, Status.NEW_RETURNED_STATUS, Status.REVIEW_STATUS,Status.AWAITING_DATA_FORM_APPROVAL]

        statuses = Status.objects.filter(id__in=ids, status__in=in_prog_statuses)

        length = len(statuses)

        if length == 0:
            return Status.objects.none()

        if sort and length > 0:
            statuses = self.sort_employee_datatable(statuses)

        if (len(search) > 0):
            statuses = self.search_col_name(search, statuses) | self.search_col_id(search, statuses)

        return statuses

    def search_col_id(self, search, queryset):
        corp_set = queryset
        corp_set = corp_set.filter(corporate_request__display_id__icontains=search)

        ind_set = queryset
        ind_set = ind_set.filter(request__display_id__icontains=search)

        cust_set = queryset
        cust_set = cust_set.filter(custom_request__display_id__icontains=search)

        searched_set = cust_set | ind_set | corp_set
        return searched_set

    def search_col_name(self, search, queryset):
        corp_set = queryset
        corp_set = corp_set.filter(corporate_request__company_name__icontains=search)

        ind_set_first_name = queryset
        ind_set_last_name = queryset
        ind_set_first_name = ind_set_first_name.filter(request__first_name__icontains=search)
        ind_set_last_name = ind_set_last_name.filter(request__last_name__icontains=search)

        cust_set = queryset
        cust_set = cust_set.filter(custom_request__name__icontains=search)

        searched_set = corp_set | ind_set_first_name | ind_set_last_name | cust_set
        return searched_set

    def sort_employee_datatable(self, statuses):
        sort_column = self.request.GET['iSortCol_0']
        sort_direction = self.request.GET['sSortDir_0']
        order_by = ''
        if (sort_column == '0'):
            order_by = 'object_id'
        elif (sort_column == '1'):
            corp_name = 'corporate_request__company_name'
            cust_name = 'custom_request__name'
            ind_name = 'request__first_name'
            if (sort_direction == 'desc'):
                corp_name = '-' + corp_name
                cust_name = '-' + cust_name
                ind_name = '-' + ind_name
            statuses = statuses.order_by(corp_name, cust_name, ind_name)
        elif (sort_column == '2'):
            statuses = sort_statuses(statuses,sort_direction)
        elif (sort_column == '3'):
            order_by = 'datetime'
        if (sort_direction == 'desc'):
            order_by = '-' + order_by
        if len(order_by) > 2:
            statuses = statuses.order_by(order_by)

        return statuses

    def json_response(self, data):
        return HttpResponse(
            json.dumps(data, cls=DjangoJSONEncoder),
            content_type='application/json'
        )


###
# MANAGER
###
class ManagerNewRequestsDatatable(DatatablesView):
    model = Status
    fields = (
        'object_id',
        'custom_request__name',
        'custom_request__created_by__company__name',
        'content_type__model',
        'datetime',
        'request__first_name',
        'request__last_name',
        'corporate_request__company_name',
        'status',
        'corporate_request__created_by__company__name',
        'request__created_by__company__name'
    )

    def get_row(self, row):
        # Setting the links to display the details for each row.
        if row['content_type__model'] == 'request':
            # grabbing id, and changing it do display_id
            request_id = row.pop('object_id')
            request = Request.objects.get(pk=request_id)

            # creating link
            request_url = reverse('request_manager', kwargs={"pk": request_id})
            display = "<a href=\"" + request_url + "\" class=\"btn btn-xs grey btn-editable\">  "+request.display_id+"</a>"
            row['object_id'] = display
            row['content_type__model'] = 'Individual'

            # Setting Name
            first_name = request.first_name
            last_name = request.last_name
            combo_name = first_name+" "+last_name
            row['custom_request__name'] = combo_name
            row['request__first_name'] = ''
            row['request__last_name'] = ''

            # Setting Company Name
            row['custom_request__created_by__company__name'] = row['request__created_by__company__name']
            row['request__created_by__company__name'] = ''




        elif row['content_type__model'] == 'customrequest':
            request_id = row.pop('object_id')
            request_url = reverse('custom_request_manager', kwargs={"pk": int(request_id)})
            display = "<a href=\"" + request_url + "\" class=\"btn btn-xs grey btn-editable\">"+CustomRequest.objects.get(pk=request_id).display_id+"</a>"
            row['object_id'] = display
            row['content_type__model'] = 'Custom'

        elif row['content_type__model'] == 'corporaterequest':
            # Creating Link
            request_id = row.pop('object_id')
            request_url = reverse('corporate_request_manager', kwargs={"pk": int(request_id)})
            display = "<a href=\"" + request_url + "\" class=\"btn btn-xs grey btn-editable\">"+CorporateRequest.objects.get(pk=request_id).display_id+"</a>"
            row['object_id'] = display

            # setting request type
            row['content_type__model'] = 'Corporate'

            # Setting name
            row['custom_request__name'] = row['corporate_request__company_name']
            row['corporate_request__company_name'] = ''

            # setting company name
            row['custom_request__created_by__company__name'] = row['corporate_request__created_by__company__name']
            row['corporate_request__created_by__company__name'] = ''



        row['status'] = ''




        datetime = row.pop('datetime')
        cst_datetime = datetime.astimezone(timezone('US/Central'))
        formatted_date = formats.date_format(cst_datetime, "SHORT_DATETIME_FORMAT")
        row['datetime'] = formatted_date


        return super(ManagerNewRequestsDatatable, self).get_row(row)

    def get_queryset(self):
        current_user = self.request.user
        search = self.request.GET['sSearch']
        try:
            sort = self.request.GET['iSortCol_0']
        except Exception, e:
            sort = None

        ids = list(Status.get_all_current_ids_queryset())

        statuses = Status.objects.filter(id__in=ids, status=Status.NEW_STATUS)

        length = len(statuses)

        if length == 0:
            return Status.objects.none()

        if sort and length > 0:
            statuses = self.sort_supervisor_datatable(statuses)

        if (len(search) > 0):
            statuses = self.search_col_name(search, statuses) | self.search_col_id(search, statuses)

        return statuses

    def search_col_id(self, search, queryset):

        corp_set = queryset
        corp_set = corp_set.filter(corporate_request__display_id__icontains=search)

        ind_set = queryset
        ind_set = ind_set.filter(request__display_id__icontains=search)

        cust_set = queryset
        cust_set = cust_set.filter(custom_request__display_id__icontains=search)

        searched_set = cust_set | ind_set | corp_set
        return searched_set

    def search_col_name(self, search, queryset):
        corp_set = queryset
        corp_set = corp_set.filter(corporate_request__company_name__icontains=search)

        ind_set_first_name = queryset
        ind_set_last_name = queryset
        ind_set_first_name = ind_set_first_name.filter(request__first_name__icontains=search)
        ind_set_last_name = ind_set_last_name.filter(request__last_name__icontains=search)

        cust_set = queryset
        cust_set = cust_set.filter(custom_request__name__icontains=search)

        searched_set = corp_set | ind_set_first_name | ind_set_last_name | cust_set
        return searched_set

    def sort_supervisor_datatable(self, statuses):
        sort_column = self.request.GET['iSortCol_0']
        sort_direction = self.request.GET['sSortDir_0']
        order_by = ''
        if (sort_column == '0'):
            order_by = 'object_id'
        elif (sort_column == '1'):
            corp_name = 'corporate_request__company_name'
            cust_name = 'custom_request__name'
            ind_name = 'request__first_name'
            if (sort_direction == 'desc'):
                corp_name = '-' + corp_name
                cust_name = '-' + cust_name
                ind_name = '-' + ind_name
            statuses = statuses.order_by(corp_name, cust_name, ind_name)
        elif (sort_column == '2'):
            statuses = sort_statuses(statuses,sort_direction)
        elif (sort_column == '3'):
            order_by = 'content_type__model'
        elif (sort_column == '4'):
           order_by = 'datetime'
        if (sort_direction == 'desc'):
            order_by = '-' + order_by
        if len(order_by) > 2:
            statuses = statuses.order_by(order_by)

        return statuses

    def json_response(self, data):
        return HttpResponse(
            json.dumps(data, cls=DjangoJSONEncoder),
            content_type='application/json'
        )


class ManagerAdvancedTable(DatatablesView):
    model = Status
    fields = (
        'object_id',
        'custom_request__name',
        'status',
        'custom_request__created_by__company__name',
        'custom_request__in_progress_status__datetime',
        'content_type__model',
        'custom_request__assignment__user__last_name',
        'request__first_name',
        'request__last_name',
        'request__request_type__price',
        'corporate_request__company_name',
        'request__assignment__user__last_name',
        'corporate_request__assignment__user__last_name',
        'request__created_by__company__name',
        'corporate_request__created_by__company__name',
        'request__in_progress_status__datetime',
        'corporate_request__in_progress_status__datetime',
        'datetime',
        'request__reviewer__user__last_name',
        'corporate_request__reviewer__user__last_name',
        'custom_request__reviewer__user__last_name',
        'request__submitted_status__datetime',
        'corporate_request__submitted_status__datetime',
        'custom_request__submitted_status__datetime',
        'request__due_date',
        'corporate_request__due_date',
        'custom_request__due_date',
    )

    def get_row(self, row):
        # Setting the links to display the details for each row.
        if row['content_type__model'] == 'request':
            # grabbing id, and changing it do display_id
            request_id = row.pop('object_id')
            request = Request.objects.get(pk=request_id)

            # creating link
            request_url = reverse('request_manager', kwargs={"pk": request_id})
            display = "<a href=\"" + request_url + "\" class=\"btn btn-xs grey btn-editable\">  "+request.display_id+"</a>"
            row['object_id'] = display
            row['content_type__model'] = "{} {} {}".format(request.request_type.due_diligence_type, request.request_type.get_level_display(), request.request_type.name)

            # Setting Name
            first_name = request.first_name
            last_name = request.last_name
            combo_name = first_name+" "+last_name
            row['custom_request__name'] = combo_name
            row['request__first_name'] = ''
            row['request__last_name'] = ''
            row['custom_request__assignment__user__last_name'] = row['request__assignment__user__last_name']
            row['request__assignment__user__last_name'] = ''
            row['custom_request__created_by__company__name'] = row['request__created_by__company__name']
            # row['request__created_by__company__name'] = ''
            row['custom_request__in_progress_status__datetime'] = row['request__in_progress_status__datetime']
            row['request__in_progress_status__datetime'] = ''
            if request.request_type.price:
                price = request.request_type.price
            else:
                price = 0
            row['request__request_type__price'] = "${}".format(price)

            surcharges = Surcharge.objects.filter(request_type="Request", request_id=request.display_id)
            total_surcharges = 0
            surcharge_list = []
            for s in surcharges:
                surcharge_list.append(s.charge_type.name)
                total_surcharges = total_surcharges + s.estimated_cost

            row['request__first_name'] = "{}".format(",".join(surcharge_list))
            row['request__last_name'] = "${}".format(total_surcharges)

            total = price + total_surcharges

            row['corporate_request__company_name'] = "${}".format(total)

            row['request__assignment__user__last_name'] = row['request__reviewer__user__last_name']
            row['corporate_request__assignment__user__last_name'] = row['request__submitted_status__datetime']
            row['request__created_by__company__name'] = row["request__due_date"]


        elif row['content_type__model'] == 'customrequest':
            request_id = row.pop('object_id')
            request_url = reverse('custom_request_manager', kwargs={"pk": int(request_id)})
            custom_request = CustomRequest.objects.get(pk=request_id)
            display = "<a href=\"" + request_url + "\" class=\"btn btn-xs grey btn-editable\">"+custom_request.display_id+"</a>"
            row['object_id'] = display
            row['content_type__model'] = "{} {} {}".format(custom_request.request_type.due_diligence_type, custom_request.request_type.get_level_display(), custom_request.request_type.name)
            if custom_request.request_type.price:
                price = custom_request.request_type.price
            else:
                price = 0
            row['request__request_type__price'] = "${}".format(price)

            surcharges = Surcharge.objects.filter(request_type="Custom Request", request_id=custom_request.display_id)
            total_surcharges = 0
            surcharge_list = []
            for s in surcharges:
                surcharge_list.append(s.charge_type.name)
                total_surcharges = total_surcharges + s.estimated_cost

            row['request__first_name'] = "{}".format(",".join(surcharge_list))
            row['request__last_name'] = "${}".format(total_surcharges)

            total = price + total_surcharges

            row['corporate_request__company_name'] = "${}".format(total)

            row['request__assignment__user__last_name'] = row['custom_request__reviewer__user__last_name']
            row['corporate_request__assignment__user__last_name'] = row['custom_request__submitted_status__datetime']
            row['request__created_by__company__name'] = row["custom_request__due_date"]

        elif row['content_type__model'] == 'corporaterequest':
            request_id = row.pop('object_id')
            request_url = reverse('corporate_request_manager', kwargs={"pk": int(request_id)})
            corporate_request = CorporateRequest.objects.get(pk=request_id)
            display = "<a href=\"" + request_url + "\" class=\"btn btn-xs grey btn-editable\">"+corporate_request.display_id+"</a>"
            row['object_id'] = display

            row['content_type__model'] = "{} {} {}".format(corporate_request.request_type.due_diligence_type, corporate_request.request_type.get_level_display(), corporate_request.request_type.name)
            row['custom_request__name'] = row['corporate_request__company_name']
            row['corporate_request__company_name'] = ''
            row['custom_request__assignment__user__last_name'] = row['corporate_request__assignment__user__last_name']
            row['corporate_request__assignment__user__last_name'] = ''
            row['custom_request__created_by__company__name'] = row['corporate_request__created_by__company__name']
            row['corporate_request__created_by__company__name'] = ''
            row['custom_request__in_progress_status__datetime'] = row['request__in_progress_status__datetime']
            row['custom_request__in_progress_status__datetime'] = ''
            if corporate_request.request_type.price:
                price = corporate_request.request_type.price
            else:
                price = 0
            row['request__request_type__price'] = "${}".format(price)

            surcharges = Surcharge.objects.filter(request_type="Corporate Request", request_id=corporate_request.display_id)
            total_surcharges = 0
            surcharge_list = []
            for s in surcharges:
                surcharge_list.append(s.charge_type.name)
                total_surcharges = total_surcharges + s.estimated_cost

            row['request__first_name'] = "{}".format(",".join(surcharge_list))
            row['request__last_name'] = "${}".format(total_surcharges)

            total = price + total_surcharges

            row['corporate_request__company_name'] = "${}".format(total)

            row['request__assignment__user__last_name'] = row['corporate_request__reviewer__user__last_name']
            row['corporate_request__assignment__user__last_name'] = row['corporate_request__submitted_status__datetime']
            row['request__created_by__company__name'] = row["corporate_request__due_date"]

        status = row.pop('status')
        display_status = Status.MANAGER_STATUS_CHOICES[status]
        row['status'] = display_status

        datetime = row['custom_request__in_progress_status__datetime']

        if datetime:
            cst_datetime = datetime.astimezone(timezone('US/Central'))
            formatted_date = formats.date_format(cst_datetime, "SHORT_DATETIME_FORMAT")
            row['custom_request__in_progress_status__datetime'] = formatted_date
        else:
            row['custom_request__in_progress_status__datetime'] = ''

        datetime = row['corporate_request__assignment__user__last_name']

        if datetime:
            cst_datetime = datetime.astimezone(timezone('US/Central'))
            formatted_date = formats.date_format(cst_datetime, "SHORT_DATETIME_FORMAT")
            row['corporate_request__assignment__user__last_name'] = formatted_date
        else:
            row['corporate_request__assignment__user__last_name'] = ''

        sort_column = self.request.GET['iSortCol_0']

        if sort_column == '4':
            datetime = row['datetime']
            cst_datetime = datetime.astimezone(timezone('US/Central'))
            formatted_date = formats.date_format(cst_datetime, "SHORT_DATETIME_FORMAT")
            row['custom_request__in_progress_status__datetime'] = formatted_date

        row['datetime'] = ''
        row['request__reviewer__user__last_name'] = ''
        row['custom_request__reviewer__user__last_name'] = ''
        row['request__submitted_status__datetime'] = ''
        row['custom_request__submitted_status__datetime'] = ''
        row['corporate_request__submitted_status__datetime'] = ''
        row["request__due_date"] = ''
        row["corporate_request__due_date"] = ''
        row["custom_request__due_date"] = ''

        return super(ManagerAdvancedTable, self).get_row(row)

    def get_queryset(self):
        current_user = self.request.user
        search = self.request.GET['sSearch']
        try:
            sort = self.request.GET['iSortCol_0']
        except Exception, e:
            sort = None


        ids = list(Status.get_all_current_ids_queryset())
        statuses = Status.objects.filter(id__in=ids)

        length = len(statuses)

        if length == 0:
            return Status.objects.none()

        if sort and length > 0:
            statuses = self.sort_supervisor_datatable(statuses)

        if (len(search) > 0):
            statuses = self.search_col_name(search, statuses) | self.search_col_id(search, statuses)

        # ID
        id_search = ifCustomReturnVal(self.request.GET['sSearch_0'])
        if (len(id_search) > 0):
            cust_id_filt = statuses.filter(custom_request__display_id__icontains=id_search)
            corp_id_filt = statuses.filter(corporate_request__display_id__icontains=id_search)
            ind_id_filt = statuses.filter(request__display_id__icontains=id_search)
            statuses = cust_id_filt | corp_id_filt | ind_id_filt

        # company
        company_search = ifCustomReturnVal(self.request.GET['sSearch_1'])
        if (len(company_search) > 0):
            cust_company_name = statuses.filter(custom_request__created_by__company=company_search)
            corp_company_name = statuses.filter(corporate_request__created_by__company=company_search)
            ind_company_name = statuses.filter(request__created_by__company=company_search)
            statuses = cust_company_name | corp_company_name | ind_company_name


        # Assigned To
        assigned_to_id = ifCustomReturnVal(self.request.GET['sSearch_2'])
        if (len(assigned_to_id) > 0):
            cust_ids = statuses.filter(custom_request__assignment=assigned_to_id).values_list('id', flat=True)
            corp_ids = statuses.filter(corporate_request__assignment=assigned_to_id).values_list('id', flat=True)
            ind_ids = statuses.filter(request__assignment=assigned_to_id).values_list('id', flat=True)
            comb_ids = list(chain(cust_ids, corp_ids, ind_ids))
            statuses = statuses.filter(id__in=comb_ids)



        name_search = ifCustomReturnVal(self.request.GET['sSearch_3'])


        if len(name_search) > 0:
            cust_names = statuses.filter(custom_request__name__icontains=name_search)
            corp_names = statuses.filter(corporate_request__company_name__icontains=name_search)
            ind_first = statuses.filter(request__first_name__icontains=name_search)
            ind_last = statuses.filter(request__last_name__icontains=name_search)
            statuses = cust_names | corp_names | ind_first | ind_last



        # STATUS
        status_search = ifCustomReturnVal(self.request.GET['sSearch_4'])
        if (status_search != "null" and len(status_search) > 0):
            statuses = statuses.filter(status__in=status_search.split(","))



        # TYPE
        type_search = ifCustomReturnVal(self.request.GET['sSearch_5'])
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
        start_end_date = self.request.GET['sSearch_6']
        if (len(start_end_date) > 3):
            array = start_end_date.split('+')
            start = fix_start(array[0])
            end = fix_end(array[1])
            statuses = statuses.filter(id__in=ids).filter(datetime__range=[start, end])


        # CUSTOM FIELD
        custom_field = ifCustomReturnVal(self.request.GET['sSearch_8'])
        if (len(custom_field) > 0):
            field_ids = list(
                CustomRequestFields.objects.filter(custom_request__dynamic_request_form__render_form=True,
                                                   form_field__id=custom_field).exclude(
                    value__isnull=True).exclude(value__exact='').values_list('custom_request__id', flat=True))

            statuses = statuses.filter(custom_request__id__in=field_ids)


        # CUSTOM FIELD VALUE
        custom_field_value = ifCustomReturnVal(self.request.GET['sSearch_9'])
        if (len(custom_field_value) > 0):
            field_ids = list(
                CustomRequestFields.objects.filter(custom_request__dynamic_request_form__render_form=True,
                                                   value__icontains=custom_field_value).values_list(
                                                    'custom_request__id', flat=True))
            statuses = statuses.filter(custom_request__id__in=field_ids)

        # FORM NAME
        dynamic_request_form_id = ifCustomReturnVal(self.request.GET['sSearch_10'])
        if (len(dynamic_request_form_id) > 0):
            statuses = statuses.filter(custom_request__dynamic_request_form__id=dynamic_request_form_id)


        # REQUEST TYPE
        request_type = ifCustomReturnVal(self.request.GET['sSearch_11'])
        if len(request_type) > 0:
            statuses = statuses.filter(content_type__model=request_type)


        return statuses

    def search_col_id(self, search, queryset):
        corp_set = queryset
        corp_set = corp_set.filter(corporate_request__display_id__icontains=search)

        ind_set = queryset
        ind_set = ind_set.filter(request__display_id__icontains=search)

        cust_set = queryset
        cust_set = cust_set.filter(custom_request__display_id__icontains=search)

        searched_set = cust_set | ind_set | corp_set
        return searched_set

    def search_col_name(self, search, queryset):
        corp_set = queryset
        corp_set = corp_set.filter(corporate_request__company_name__icontains=search)

        ind_set_first_name = queryset
        ind_set_last_name = queryset
        ind_set_first_name = ind_set_first_name.filter(request__first_name__icontains=search)
        ind_set_last_name = ind_set_last_name.filter(request__last_name__icontains=search)

        cust_set = queryset
        cust_set = cust_set.filter(custom_request__name__icontains=search)

        searched_set = corp_set | ind_set_first_name | ind_set_last_name | cust_set
        return searched_set

    def sort_supervisor_datatable(self, statuses):
        sort_column = self.request.GET['iSortCol_0']
        sort_direction = self.request.GET['sSortDir_0']
        order_by = ''
        if (sort_column == '0'):
            order_by = 'object_id'
        elif (sort_column == '1'):
            corp_name = 'corporate_request__company_name'
            cust_name = 'custom_request__name'
            ind_name = 'request__first_name'
            if (sort_direction == 'desc'):
                corp_name = '-' + corp_name
                cust_name = '-' + cust_name
                ind_name = '-' + ind_name
            statuses = statuses.order_by(corp_name, cust_name, ind_name)


        elif (sort_column == '2'):
            statuses = sort_statuses(statuses,sort_direction)

        elif(sort_column == '3'):
            cust_company_name = 'custom_request__created_by__company__name'
            corp_company_name = 'corporate_request__created_by__company__name'
            ind_company_name = 'request__created_by__company__name'
            if sort_direction == 'desc':
                cust_company_name = '-'+cust_company_name
                corp_company_name = '-'+corp_company_name
                ind_company_name = '-'+ind_company_name
            statuses = statuses.order_by(cust_company_name, corp_company_name, ind_company_name)

        elif (sort_column == '4'):
            order_by = 'datetime'

        elif (sort_column == '5'):
            order_by = 'content_type__model'
        elif (sort_column == '6'):
            cust_assignment = 'custom_request__assignment__user__last_name'
            corp_assignment = 'corporate_request__assignment__user__last_name'
            ind_assignment = 'request__assignment__user__last_name'
            if (sort_direction == 'desc'):
                cust_assignment = '-' + cust_assignment
                corp_assignment = '-' + corp_assignment
                ind_assignment = '-' + ind_assignment
            statuses = statuses.order_by(cust_assignment, corp_assignment, ind_assignment)



        if (sort_direction == 'desc'):
            order_by = '-' + order_by
        if len(order_by) > 2:
            statuses = statuses.order_by(order_by)
        return statuses

    def json_response(self, data):
        return HttpResponse(
            json.dumps(data, cls=DjangoJSONEncoder),
            content_type='application/json'
        )


###
# Analyst
###

class AnalystNewRequestsDatatable(DatatablesView):
    model = Status
    fields = (
        'object_id',
        'custom_request__name',
        'custom_request__created_by__company__name',
        'content_type__model',
        'datetime',
        'request__first_name',
        'request__last_name',
        'corporate_request__company_name',
        'status',
        'corporate_request__created_by__company__name',
        'request__created_by__company__name'
    )

    def get_row(self, row):
        # Setting the links to display the details for each row.
        if row['content_type__model'] == 'request':
            # grabbing id, and changing it do display_id
            request_id = row.pop('object_id')
            request = Request.objects.get(pk=request_id)

            # creating link
            request_url = reverse('request_analyst', kwargs={"pk": request_id})
            display = "<a href=\"" + request_url + "\" class=\"btn btn-xs grey btn-editable\">  "+request.display_id+"</a>"
            row['object_id'] = display
            row['content_type__model'] = 'Individual'

            # Setting Name
            first_name = request.first_name
            last_name = request.last_name
            combo_name = first_name+" "+last_name
            row['custom_request__name'] = combo_name
            row['request__first_name'] = ''
            row['request__last_name'] = ''

            # Setting Company Name
            row['custom_request__created_by__company__name'] = row['request__created_by__company__name']
            row['request__created_by__company__name'] = ''




        elif row['content_type__model'] == 'customrequest':
            request_id = row.pop('object_id')
            request_url = reverse('request_analyst_for_custom', kwargs={"pk": int(request_id)})
            display = "<a href=\"" + request_url + "\" class=\"btn btn-xs grey btn-editable\">"+CustomRequest.objects.get(pk=request_id).display_id+"</a>"
            row['object_id'] = display
            row['content_type__model'] = 'Custom'

        elif row['content_type__model'] == 'corporaterequest':
            # Creating Link
            request_id = row.pop('object_id')
            request_url = reverse('request_analyst_for_corporate', kwargs={"pk": int(request_id)})
            display = "<a href=\"" + request_url + "\" class=\"btn btn-xs grey btn-editable\">"+CorporateRequest.objects.get(pk=request_id).display_id+"</a>"
            row['object_id'] = display

            # setting request type
            row['content_type__model'] = 'Corporate'

            # Setting name
            row['custom_request__name'] = row['corporate_request__company_name']
            row['corporate_request__company_name'] = ''

            # setting company name
            row['custom_request__created_by__company__name'] = row['corporate_request__created_by__company__name']
            row['corporate_request__created_by__company__name'] = ''



        row['status'] = ''




        datetime = row.pop('datetime')
        cst_datetime = datetime.astimezone(timezone('US/Central'))
        formatted_date = formats.date_format(cst_datetime, "SHORT_DATETIME_FORMAT")
        row['datetime'] = formatted_date


        return super(AnalystNewRequestsDatatable, self).get_row(row)

    def get_queryset(self):
        current_user = self.request.user
        search = self.request.GET['sSearch']
        try:
            sort = self.request.GET['iSortCol_0']
        except Exception, e:
            sort = None

        ids = list(Status.get_all_current_ids_queryset())

        statuses = Status.objects.filter(id__in=ids, status=Status.NEW_STATUS)

        length = len(statuses)

        if length == 0:
            return Status.objects.none()

        if sort and length > 0:
            statuses = self.sort_supervisor_datatable(statuses)

        if (len(search) > 0):
            statuses = self.search_col_name(search, statuses) | self.search_col_id(search, statuses)

        return statuses

    def search_col_id(self, search, queryset):

        corp_set = queryset
        corp_set = corp_set.filter(corporate_request__display_id__icontains=search)

        ind_set = queryset
        ind_set = ind_set.filter(request__display_id__icontains=search)

        cust_set = queryset
        cust_set = cust_set.filter(custom_request__display_id__icontains=search)

        searched_set = cust_set | ind_set | corp_set
        return searched_set

    def search_col_name(self, search, queryset):
        corp_set = queryset
        corp_set = corp_set.filter(corporate_request__company_name__icontains=search)

        ind_set_first_name = queryset
        ind_set_last_name = queryset
        ind_set_first_name = ind_set_first_name.filter(request__first_name__icontains=search)
        ind_set_last_name = ind_set_last_name.filter(request__last_name__icontains=search)

        cust_set = queryset
        cust_set = cust_set.filter(custom_request__name__icontains=search)

        searched_set = corp_set | ind_set_first_name | ind_set_last_name | cust_set
        return searched_set

    def sort_supervisor_datatable(self, statuses):
        sort_column = self.request.GET['iSortCol_0']
        sort_direction = self.request.GET['sSortDir_0']
        order_by = ''
        if (sort_column == '0'):
            order_by = 'object_id'
        elif (sort_column == '1'):
            corp_name = 'corporate_request__company_name'
            cust_name = 'custom_request__name'
            ind_name = 'request__first_name'
            if (sort_direction == 'desc'):
                corp_name = '-' + corp_name
                cust_name = '-' + cust_name
                ind_name = '-' + ind_name
            statuses = statuses.order_by(corp_name, cust_name, ind_name)
        elif (sort_column == '2'):
            statuses = sort_statuses(statuses,sort_direction)
        elif (sort_column == '3'):
            order_by = 'content_type__model'
        elif (sort_column == '4'):
           order_by = 'datetime'
        if (sort_direction == 'desc'):
            order_by = '-' + order_by
        if len(order_by) > 2:
            statuses = statuses.order_by(order_by)

        return statuses

    def json_response(self, data):
        return HttpResponse(
            json.dumps(data, cls=DjangoJSONEncoder),
            content_type='application/json'
        )

class AnalystAdvancedTable(DatatablesView):
    model = Status
    fields = (
        'object_id',
        'custom_request__name',
        'status',
        'datetime',
        'custom_request__created_by__company__name',
        'request__first_name',
        'request__last_name',
        'corporate_request__company_name',
        'corporate_request__created_by__company__name',
        'request__created_by__company__name',
        'content_type__model',

        'request__assignment__user__last_name',
        'custom_request__assignment__user__last_name',
        'corporate_request__assignment__user__last_name',
        'request__reviewer__user__last_name',
        'corporate_request__reviewer__user__last_name',
        'custom_request__reviewer__user__last_name',
        'request__due_date',
        'corporate_request__due_date',
        'custom_request__due_date',
    )

    def get_row(self, row):
        # Setting the links to display the details for each row.
        if row['content_type__model'] == 'request':
            # grabbing id, and changing it do display_id
            request_id = row.pop('object_id')
            request = Request.objects.get(pk=request_id)

            # creating link
            request_url = reverse('request_analyst', kwargs={"pk": request_id})
            display = "<a href=\"" + request_url + "\" class=\"btn btn-xs grey btn-editable\">  "+request.display_id+"</a>"
            row['object_id'] = display
            row['content_type__model'] = 'Individual'

            # Setting Name
            first_name = request.first_name
            last_name = request.last_name
            combo_name = first_name+" "+last_name
            row['custom_request__name'] = combo_name
            row['request__first_name'] = row['request__assignment__user__last_name']
            row['request__last_name'] = row['request__reviewer__user__last_name']
            # Setting created by company name
            row['custom_request__created_by__company__name'] = row['request__created_by__company__name']
            row['request__created_by__company__name'] = ''
            row['corporate_request__company_name'] = row['request__due_date']

        elif row['content_type__model'] == 'customrequest':
            request_id = row.pop('object_id')
            request_url = reverse('request_analyst_for_custom', kwargs={"pk": int(request_id)})
            display = "<a href=\"" + request_url + "\" class=\"btn btn-xs grey btn-editable\">"+CustomRequest.objects.get(pk=request_id).display_id+"</a>"
            row['object_id'] = display
            row['content_type__model'] = 'Custom'

            row['request__first_name'] = row['custom_request__assignment__user__last_name']
            row['request__last_name'] = row['custom_request__reviewer__user__last_name']
            row['corporate_request__company_name'] = row['custom_request__due_date']

        elif row['content_type__model'] == 'corporaterequest':
            request_id = row.pop('object_id')
            request_url = reverse('request_analyst_for_corporate', kwargs={"pk": int(request_id)})
            display = "<a href=\"" + request_url + "\" class=\"btn btn-xs grey btn-editable\">"+CorporateRequest.objects.get(pk=request_id).display_id+"</a>"
            row['object_id'] = display
            row['content_type__model'] = 'Corporate'
            row['custom_request__name'] = row['corporate_request__company_name']
            row['corporate_request__company_name'] = ''
            row['custom_request__created_by__company__name'] = row['corporate_request__created_by__company__name']
            row['corporate_request__created_by__company__name'] = ''

            row['request__first_name'] = row['corporate_request__assignment__user__last_name']
            row['request__last_name'] = row['corporate_request__reviewer__user__last_name']
            row['corporate_request__company_name'] = row['corporate_request__due_date']

        status = row.pop('status')
        display_status = Status.MANAGER_STATUS_CHOICES[status]
        row['status'] = display_status

        datetime = row.pop('datetime')
        cst_datetime = datetime.astimezone(timezone('US/Central'))
        formatted_date = formats.date_format(cst_datetime, "SHORT_DATETIME_FORMAT")
        row['datetime'] = formatted_date

        row['content_type__model'] = ''
        row['request__assignment__user__last_name'] = ''
        row['custom_request__assignment__user__last_name'] = ''
        row['corporate_request__assignment__user__last_name'] = ''
        row['request__reviewer__user__last_name'] = ''
        row['corporate_request__reviewer__user__last_name'] = ''
        row['custom_request__reviewer__user__last_name'] = ''
        row['request__due_date'] = ''
        row['corporate_request__due_date'] = ''
        row['custom_request__due_date'] = ''

        return super(AnalystAdvancedTable, self).get_row(row)

    def get_queryset(self):
        current_user = self.request.user
        search = self.request.GET['sSearch']
        try:
            sort = self.request.GET['iSortCol_0']
        except Exception, e:
            sort = None

        ids = list(Status.get_all_current_ids_queryset())

        statuses = Status.objects.filter(
            id__in=ids)
        length = len(statuses)

        if length == 0:
            return Status.objects.none()

        if sort and length > 0:
            statuses = self.sort_supervisor_datatable(statuses)

        if (len(search) > 0):
            statuses = self.search_col_name(search, statuses) | self.search_col_id(search, statuses)

        # ID
        id_search = ifCustomReturnVal(self.request.GET['sSearch_0'])
        if (len(id_search) > 0):
            cust_id_filt = statuses.filter(custom_request__display_id__icontains=id_search)
            corp_id_filt = statuses.filter(corporate_request__display_id__icontains=id_search)
            ind_id_filt = statuses.filter(request__display_id__icontains=id_search)
            statuses = cust_id_filt | corp_id_filt | ind_id_filt

        # NAME
        name_search = ifCustomReturnVal(self.request.GET['sSearch_1'])
        if len(name_search) > 0:
            cust_names = statuses.filter(custom_request__name__icontains=name_search)
            corp_names = statuses.filter(corporate_request__company_name__icontains=name_search)
            ind_first = statuses.filter(request__first_name__icontains=name_search)
            ind_last = statuses.filter(request__last_name__icontains=name_search)
            statuses = cust_names | corp_names | ind_first | ind_last


        # TYPE
        type_search = ifCustomReturnVal(self.request.GET['sSearch_2'])
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

        # company
        company_search = ifCustomReturnVal(self.request.GET['sSearch_3'])
        if (len(company_search) > 0):
            cust_company_name = statuses.filter(custom_request__created_by__company=company_search)
            corp_company_name = statuses.filter(corporate_request__created_by__company=company_search)
            ind_company_name = statuses.filter(request__created_by__company=company_search)
            statuses = cust_company_name | corp_company_name | ind_company_name


        # STATUS
        status_search = ifCustomReturnVal(self.request.GET['sSearch_4'])
        if (status_search != "null" and len(status_search) > 0):
            statuses = statuses.filter(status__in=status_search.split(","))


        # Assigned To
        assigned_to_id = ifCustomReturnVal(self.request.GET['sSearch_5'])
        if (len(assigned_to_id) > 0):
            cust_ids = statuses.filter(custom_request__assignment=assigned_to_id).values_list('id', flat=True)
            corp_ids = statuses.filter(corporate_request__assignment=assigned_to_id).values_list('id', flat=True)
            ind_ids = statuses.filter(request__assignment=assigned_to_id).values_list('id', flat=True)
            comb_ids = list(chain(cust_ids, corp_ids, ind_ids))
            statuses = statuses.filter(id__in=comb_ids)

        # START DATE
        start_end_date = self.request.GET['sSearch_6']
        if (len(start_end_date) > 3):
            array = start_end_date.split('+')
            start = fix_start(array[0])
            end = fix_end(array[1])
            statuses = statuses.filter(id__in=ids).filter(datetime__range=[start, end])


        # CUSTOM FIELD
        custom_field = ifCustomReturnVal(self.request.GET['sSearch_8'])
        if (len(custom_field) > 0):
            field_ids = list(
                CustomRequestFields.objects.filter(custom_request__dynamic_request_form__render_form=True,
                                                   form_field__id=custom_field).exclude(
                    value__isnull=True).exclude(value__exact='').values_list('custom_request__id', flat=True))

            statuses = statuses.filter(custom_request__id__in=field_ids)


        # CUSTOM FIELD VALUE
        custom_field_value = ifCustomReturnVal(self.request.GET['sSearch_9'])
        if (len(custom_field_value) > 0):
            field_ids = list(
                CustomRequestFields.objects.filter(custom_request__dynamic_request_form__render_form=True,
                                                   value__icontains=custom_field_value).values_list(
                                                    'custom_request__id', flat=True))
            statuses = statuses.filter(custom_request__id__in=field_ids)

        # FORM NAME
        dynamic_request_form_id = ifCustomReturnVal(self.request.GET['sSearch_10'])
        if (len(dynamic_request_form_id) > 0):
            statuses = statuses.filter(custom_request__dynamic_request_form__id=dynamic_request_form_id)


        # REQUEST TYPE
        request_type = ifCustomReturnVal(self.request.GET['sSearch_11'])
        if len(request_type) > 0:
            statuses = statuses.filter(content_type__model=request_type)


        return statuses

    def sort_supervisor_datatable(self, statuses):
        sort_column = self.request.GET['iSortCol_0']
        sort_direction = self.request.GET['sSortDir_0']
        order_by = ''
        if (sort_column == '0'):
            order_by = 'object_id'
        elif (sort_column == '1'):
            corp_name = 'corporate_request__company_name'
            cust_name = 'custom_request__name'
            ind_name = 'request__first_name'
            if (sort_direction == 'desc'):
                corp_name = '-' + corp_name
                cust_name = '-' + cust_name
                ind_name = '-' + ind_name
            statuses = statuses.order_by(corp_name, cust_name, ind_name)


        elif (sort_column == '2'):
            statuses = sort_statuses(statuses,sort_direction)
        elif (sort_column == '3'):
            order_by = 'datetime'
        elif (sort_column == '4'):
            corp_created_by = 'corporate_request__created_by__company__name'
            cust_created_by = 'custom_request__created_by__company__name'
            ind_created_by = 'request__created_by__company__name'

            if sort_direction == 'desc':
                corp_created_by = "-"+corp_created_by
                cust_created_by = "-"+cust_created_by
                ind_created_by = '-'+ind_created_by
            statuses = statuses.order_by(cust_created_by, corp_created_by, ind_created_by)
        if (sort_direction == 'desc'):
            order_by = '-' + order_by
        if len(order_by) > 2:
            statuses = statuses.order_by(order_by)
        return statuses

    def json_response(self, data):
        return HttpResponse(
            json.dumps(data, cls=DjangoJSONEncoder),
            content_type='application/json'
        )

class ReviewerAdvancedTable(DatatablesView):
    model = Status
    fields = (
        'object_id',
        'custom_request__name',
        'status',
        'datetime',
        'custom_request__created_by__company__name',
        'request__first_name',
        'request__last_name',
        'corporate_request__company_name',
        'corporate_request__created_by__company__name',
        'request__created_by__company__name',
        'content_type__model',

        'request__assignment__user__last_name',
        'custom_request__assignment__user__last_name',
        'corporate_request__assignment__user__last_name',
        'request__reviewer__user__last_name',
        'corporate_request__reviewer__user__last_name',
        'custom_request__reviewer__user__last_name',
        'request__due_date',
        'corporate_request__due_date',
        'custom_request__due_date',
    )

    def get_row(self, row):
        # Setting the links to display the details for each row.
        if row['content_type__model'] == 'request':
            # grabbing id, and changing it do display_id
            request_id = row.pop('object_id')
            request = Request.objects.get(pk=request_id)

            # creating link
            request_url = reverse('request_reviewer', kwargs={"pk": request_id})
            display = "<a href=\"" + request_url + "\" class=\"btn btn-xs grey btn-editable\">  "+request.display_id+"</a>"
            row['object_id'] = display
            row['content_type__model'] = 'Individual'

            # Setting Name
            first_name = request.first_name
            last_name = request.last_name
            combo_name = first_name+" "+last_name
            row['custom_request__name'] = combo_name
            row['request__first_name'] = row['request__assignment__user__last_name']
            row['request__last_name'] = row['request__reviewer__user__last_name']
            # Setting created by company name
            row['custom_request__created_by__company__name'] = row['request__created_by__company__name']
            row['request__created_by__company__name'] = ''
            row['corporate_request__company_name'] = row["request__due_date"]

        elif row['content_type__model'] == 'customrequest':
            request_id = row.pop('object_id')
            request_url = reverse('request_reviewer_for_custom', kwargs={"pk": int(request_id)})
            display = "<a href=\"" + request_url + "\" class=\"btn btn-xs grey btn-editable\">"+CustomRequest.objects.get(pk=request_id).display_id+"</a>"
            row['object_id'] = display
            row['content_type__model'] = 'Custom'

            row['request__first_name'] = row['custom_request__assignment__user__last_name']
            row['request__last_name'] = row['custom_request__reviewer__user__last_name']
            row['corporate_request__company_name'] = row["custom_request__due_date"]

        elif row['content_type__model'] == 'corporaterequest':
            request_id = row.pop('object_id')
            request_url = reverse('request_reviewer_for_corporate', kwargs={"pk": int(request_id)})
            display = "<a href=\"" + request_url + "\" class=\"btn btn-xs grey btn-editable\">"+CorporateRequest.objects.get(pk=request_id).display_id+"</a>"
            row['object_id'] = display
            row['content_type__model'] = 'Corporate'
            row['custom_request__name'] = row['corporate_request__company_name']

            row['custom_request__created_by__company__name'] = row['corporate_request__created_by__company__name']
            row['corporate_request__created_by__company__name'] = ''

            row['request__first_name'] = row['corporate_request__assignment__user__last_name']
            row['request__last_name'] = row['corporate_request__reviewer__user__last_name']
            row['corporate_request__company_name'] = row["corporate_request__due_date"]

        status = row.pop('status')
        display_status = Status.MANAGER_STATUS_CHOICES[status]
        row['status'] = display_status

        datetime = row.pop('datetime')
        cst_datetime = datetime.astimezone(timezone('US/Central'))
        formatted_date = formats.date_format(cst_datetime, "SHORT_DATETIME_FORMAT")
        row['datetime'] = formatted_date

        row['content_type__model'] = ''
        row['request__assignment__user__last_name'] = ''
        row['custom_request__assignment__user__last_name'] = ''
        row['corporate_request__assignment__user__last_name'] = ''
        row['request__reviewer__user__last_name'] = ''
        row['corporate_request__reviewer__user__last_name'] = ''
        row['custom_request__reviewer__user__last_name'] = ''
        row['request__due_date'] = ''
        row["corporate_request__due_date"] = ''
        row["custom_request__due_date"] = ''

        return super(ReviewerAdvancedTable, self).get_row(row)

    def get_queryset(self):
        current_user = self.request.user
        search = self.request.GET['sSearch']
        try:
            sort = self.request.GET['iSortCol_0']
        except Exception, e:
            sort = None

        ids = list(Status.get_all_current_ids_queryset())

        statuses = Status.objects.filter(
            id__in=ids)
        length = len(statuses)

        if length == 0:
            return Status.objects.none()

        if sort and length > 0:
            statuses = self.sort_supervisor_datatable(statuses)

        if (len(search) > 0):
            statuses = self.search_col_name(search, statuses) | self.search_col_id(search, statuses)

        # ID
        id_search = ifCustomReturnVal(self.request.GET['sSearch_0'])
        if (len(id_search) > 0):
            cust_id_filt = statuses.filter(custom_request__display_id__icontains=id_search)
            corp_id_filt = statuses.filter(corporate_request__display_id__icontains=id_search)
            ind_id_filt = statuses.filter(request__display_id__icontains=id_search)
            statuses = cust_id_filt | corp_id_filt | ind_id_filt

        # NAME
        name_search = ifCustomReturnVal(self.request.GET['sSearch_1'])
        if len(name_search) > 0:
            cust_names = statuses.filter(custom_request__name__icontains=name_search)
            corp_names = statuses.filter(corporate_request__company_name__icontains=name_search)
            ind_first = statuses.filter(request__first_name__icontains=name_search)
            ind_last = statuses.filter(request__last_name__icontains=name_search)
            statuses = cust_names | corp_names | ind_first | ind_last


        # TYPE
        type_search = ifCustomReturnVal(self.request.GET['sSearch_2'])
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

        # company
        company_search = ifCustomReturnVal(self.request.GET['sSearch_3'])
        if (len(company_search) > 0):
            cust_company_name = statuses.filter(custom_request__created_by__company=company_search)
            corp_company_name = statuses.filter(corporate_request__created_by__company=company_search)
            ind_company_name = statuses.filter(request__created_by__company=company_search)
            statuses = cust_company_name | corp_company_name | ind_company_name


        # STATUS
        status_search = ifCustomReturnVal(self.request.GET['sSearch_4'])
        if (status_search != "null" and len(status_search) > 0):
            statuses = statuses.filter(status__in=status_search.split(","))

        return statuses

    def sort_supervisor_datatable(self, statuses):
        sort_column = self.request.GET['iSortCol_0']
        sort_direction = self.request.GET['sSortDir_0']
        order_by = ''
        if (sort_column == '0'):
            order_by = 'object_id'
        elif (sort_column == '1'):
            corp_name = 'corporate_request__company_name'
            cust_name = 'custom_request__name'
            ind_name = 'request__first_name'
            if (sort_direction == 'desc'):
                corp_name = '-' + corp_name
                cust_name = '-' + cust_name
                ind_name = '-' + ind_name
            statuses = statuses.order_by(corp_name, cust_name, ind_name)


        elif (sort_column == '2'):
            statuses = sort_statuses(statuses,sort_direction)
        elif (sort_column == '3'):
            order_by = 'datetime'
        elif (sort_column == '4'):
            corp_created_by = 'corporate_request__created_by__company__name'
            cust_created_by = 'custom_request__created_by__company__name'
            ind_created_by = 'request__created_by__company__name'

            if sort_direction == 'desc':
                corp_created_by = "-"+corp_created_by
                cust_created_by = "-"+cust_created_by
                ind_created_by = '-'+ind_created_by
            statuses = statuses.order_by(cust_created_by, corp_created_by, ind_created_by)
        if (sort_direction == 'desc'):
            order_by = '-' + order_by
        if len(order_by) > 2:
            statuses = statuses.order_by(order_by)
        return statuses

    def json_response(self, data):
        return HttpResponse(
            json.dumps(data, cls=DjangoJSONEncoder),
            content_type='application/json'
        )


####################################
#
# TABLE UTILITY METHODS
#
####################################

def ifCustomReturnVal(value):
    if 'custom' in value:
        return value.split(';')[1]
    else:
        return ''


def ifCorporateReturnVal(value):
    if 'corporate' in value:
        return value.split(';')[1]
    else:
        return ''


def ifCustomOrCorporateReturnNothing(value):
    if 'custom' in value or 'corporate' in value:
        return ''
    return value


def sort(request, statuses):
    sort_column = request.GET['iSortCol_0']
    sort_direction = request.GET['sSortDir_0']
    order_by = ''
    if (sort_column == '0'):
        order_by = 'request__id'
    elif (sort_column == '1'):
        order_by = 'request__first_name'
    elif (sort_column == '2'):
        order_by = 'request__last_name'
    elif (sort_column == '3'):
        order_by = 'request__request_type__name'
    elif (sort_column == '4'):
        order_by = 'request__created_by__company__name'
    elif (sort_column == '5'):
        order_by = 'request__assignment__user__last_name'
    elif (sort_column == '6'):
        order_by = 'status'
    elif (sort_column == '7'):
        order_by = 'datetime'
    if (sort_direction == 'desc'):
        order_by = '-' + order_by
    if len(order_by) > 2:
        statuses = statuses.order_by(order_by)
    return statuses


def sort_corporate(request, statuses):
    sort_column = request.GET['iSortCol_0']
    sort_direction = request.GET['sSortDir_0']

    order_by = ''
    if (sort_column == '0'):
        order_by = 'corporate_request__id'
    elif (sort_column == '1'):
        order_by = 'corporate_request__company_name'
    elif (sort_column == '2'):
        order_by = 'corporate_request__created_by__company__name'
    elif (sort_column == '3'):
        order_by = 'corporate_request__assignment__user__last_name'
    elif (sort_column == '4'):
        order_by = 'status'
    elif (sort_column == '5'):
        order_by = 'corporate_request__request_type'
    elif (sort_column == '6'):
        order_by = 'datetime'
    if (sort_direction == 'desc'):
        order_by = '-' + order_by
    if len(order_by) > 2:
        statuses = statuses.order_by(order_by)
    return statuses


def sort_custom_requests(request, statuses):
    sort_column = request.GET['iSortCol_0']
    sort_direction = request.GET['sSortDir_0']

    order_by = ''
    order_by2 = ''
    if (sort_column == '0'):
        order_by = 'request__id'
    elif (sort_column == '1'):
        order_by = 'request__name'
    elif (sort_column == '2'):
        order_by = 'request__created_by__company__name'
    elif (sort_column == '3'):
        order_by = 'request__request_type__name'
    elif (sort_column == '4'):
        order_by = 'request__assignment__user__last_name'
    elif (sort_column == '5'):
        order_by = 'request__dynamic_request_form__name'
    elif (sort_column == '6'):
        order_by = 'request__in_progress_status__datetime'
        if (sort_direction == 'desc'):
            order_by = '-' + order_by
        statuses = statuses.exclude(request__in_progress_status__datetime__isnull=True).order_by(order_by)
        return statuses
    elif (sort_column == '7'):
        order_by = 'status'

    elif (sort_column == '8'):
        order_by = 'datetime'
    if (sort_direction == 'desc'):
        order_by = '-' + order_by

    if len(order_by) > 2:
        statuses = statuses.order_by(order_by)

    return statuses


def fix_end(end):
    if len(end) == 1:
        end = datetime.datetime.now() + datetime.timedelta(days=1)
    else:
        end = datetime.datetime.strptime(str(end), '%Y-%m-%d') + datetime.timedelta(days=1)
    return end


def fix_start(start):
    if len(start) == 1:
        start = '2014-06-01'
    else:
        end = datetime.datetime.strptime(str(start), '%Y-%m-%d') - datetime.timedelta(days=1)
    return start


def fix_created_time(start):
    if len(start) == 1:
        start = '2014-06-01'
    else:
        start = datetime.datetime.strptime(str(start), '%Y-%m-%d')
    return start


def sort_reports(request, reports):
    sort_column = request.GET['iSortCol_0']
    sort_direction = request.GET['sSortDir_0']

    order_by = ''
    if (sort_column == '1'):
        order_by = 'name'
    elif (sort_column == '2'):
        order_by = 'created_by__user__last_name'
    elif (sort_column == '3'):
        order_by = 'created_by__company__name'
    elif (sort_column == '4'):
        order_by = 'report_request_type'
    elif (sort_column == '5'):
        order_by = 'created_date'

    if (sort_direction == 'desc'):
        order_by = '-' + order_by

    if len(order_by) > 2:
        reports = reports.order_by(order_by)

    return reports
