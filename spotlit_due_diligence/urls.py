import socket

from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.conf import settings
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required

# Uncomment the next two lines to enable the admin:
from django.contrib import admin

admin.autodiscover()
from axes.decorators import watch_login
from core import views
from core import data_tables

urlpatterns = patterns('',
                       url(r'^$', views.HomeRedirect.as_view(), name='redirect'),

                       url(r'^charts/$', views.ChartTest.as_view(), name='chart'),

                       url(r'^batch_upload/(?P<dynamic_request_pk>\d+)/$', views.batch_upload, name='batch_upload'),

                       url(r'^login/$', watch_login(views.LoginView.as_view()), name='login'),
                       url(r'^logout/$', views.LogOutView.as_view(), name='logout'),
                       url(r'^customer_registration/$',views.CustomerRegistration.as_view(),name='customer_registration'),
                        url(r'^customer_profile/$',login_required(views.CustomerProfileView.as_view()),name='customer_profile'),

                       url(r'^forgot_password/$', views.forgot_password, name='forgot_password'),
                       # Map the 'app.hello.reset_confirm' view that wraps around built-in password
                       # reset confirmation view, to the password reset confirmation links.
                       url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
                           views.reset_confirm, name='password_reset_confirm'),

                       url(r'^verify_account/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
                           views.VerifyAccount.as_view(), name='verify_account'),
                        url(r'^resend_verification_email/$', views.resend_verification_email,
                           name='resend_verification_email'),

                       url(r'^employee_register/(?P<pk>\d+)$',
                           login_required(views.CompanyEmployeeRegistration.as_view()), name='employee_signup'),
                       url(r'^resend_employee_email/(?P<company_pk>\d+)/(?P<employee_pk>\d+)$',
                           views.resend_signup_email,
                           name='resend_email'),
                       url(r'^employee_update/(?P<pk>\d+)$', login_required(views.CompanyEmployeeUpdate.as_view()),
                           name='employee_update'),

                       url(r'^create_individual_request/$', login_required(views.CreateIndividualRequestView.as_view()),
                           name='create_individual_request'),
                       url(r'^create_corporate_request/$', login_required(views.CreateCorporateRequestView.as_view()),
                           name='create_corporate_request'),
                       url(r'^create_custom_request/(?P<dynamic_request_pk>\d+)/$',
                           login_required(views.CreateCustomRequestView.as_view()),
                           name='create_custom_request'),

                       url(r'^update_request/(?P<pk>\d+)$', login_required(views.UpdateIndividualRequestView.as_view()),
                           name='update_request'),
                       url(r'^update_corporate_request/(?P<pk>\d+)$',
                           login_required(views.UpdateCorporateRequestView.as_view()), name='update_corporate_request'),

                       url(r'^update_custom_request/(?P<pk>\d+)$',
                           login_required(views.UpdateCustomRequestView.as_view()),
                           name='update_custom_request'),
                       url(r'^update_corporate_employee/(?P<pk>\d+)$',
                           login_required(views.UpdateCorporateRequestView.as_view()),
                           name='update_corporate_employee'),
                       url(r'^update_employee/(?P<pk>\d+)$',
                           login_required(views.UpdateIndividualRequestView.as_view()), name='update_employee'),

                        url(r'^update_request_manager/(?P<pk>\d+)$', login_required(views.UpdateIndividualRequestAttachmentManagerView.as_view()),
                           name='update_request_manager'),
                        url(r'^update_corporate_request_manager/(?P<pk>\d+)$', login_required(views.UpdateCorporateRequestAttachmentManagerView.as_view()),
                           name='update_corporate_request_manager'),
                        url(r'^update_custom_request_manager/(?P<pk>\d+)$', login_required(views.UpdateCustomRequestAttachmentManagerView.as_view()),
                           name='update_custom_request_manager'),

                       url(r'^create_company/$', login_required(views.CreateCompanyView.as_view()),
                           name='create_company'),
                       url(r'^update_company/(?P<pk>\d+)$', login_required(views.UpdateCompanyView.as_view()),
                           name='update_company'),
                       url(r'^company_dashboard/$', views.company_dashboard, name='company_dashboard'),
                       url(r'^add_dd_type/(?P<pk>\d+)$', views.add_dd_type, name='add_dd_type'),
                       url(r'^update_dd_type/(?P<company_pk>\d+)/(?P<dd_pk>\d+)$', views.update_dd_type,
                           name='update_dd_type'),

                       url(r'^company/(?P<pk>\d+)$', views.company_detail_view, name='company'),
                       url(r'^company/(?P<company_pk>\d+)/package/(?P<package_pk>\d+)$', 
                            views.change_company_publiic_package_status, name='change_company_publiic_package_status'),
                       url(r'^company_corporate_change/(?P<pk>\d+)/(?P<is_corp>\d+)$',
                           views.change_is_corporate_on_company, name='company_corporate_change'),
                       url(r'^company_individual_change/(?P<pk>\d+)/(?P<is_individual>\d+)$',
                           views.change_is_individual_on_company, name='company_individual_change'),

                       # Dashboard Related Urls

                       url(r'^manager_dashboard/$', views.manager_dashboard, name='manager_dashboard'),
                       url(r'^request_detail_manager/(?P<pk>\d+)$', views.manager_request_detail_view,
                           name='request_manager'),
                       url(r'^corporate_request_detail_manager/(?P<pk>\d+)$',
                           views.manager_request_for_corporate_detail_view, name='corporate_request_manager'),
                       url(r'^custom_request_detail_manager/(?P<pk>\d+)$',
                           views.manager_request_for_custom_detail_view, name='custom_request_manager'),

                       url(r'^analyst_dashboard/$', views.analyst_dashboard, name='analyst_dashboard'),
                       url(r'^request_detail_analyst/(?P<pk>\d+)$', views.analyst_request_detail_view,
                           name='request_analyst'),
                       url(r'^request_corporate_detail_analyst/(?P<pk>\d+)$',
                           views.analyst_request_for_corporate_detail_view, name='request_analyst_for_corporate'),
                       url(r'^request_custom_detail_analyst/(?P<pk>\d+)$',
                           views.analyst_request_for_custom_detail_view, name='request_analyst_for_custom'),

                       url(r'^supervisor_dashboard/$', views.supervisor_dashboard, name='supervisor_dashboard'),
                       url(r'^request_detail_supervisor/(?P<pk>\d+)$', views.supervisor_request_detail_view,
                           name='request_supervisor'),
                       url(r'^request_corporate_detail_supervisor/(?P<pk>\d+)$',
                           views.supervisor_corporate_request_for_detail_view, name='request_supervisor_for_corporate'),
                       url(r'^request_custom_detail_supervisor/(?P<pk>\d+)$',
                           views.supervisor_custom_request_detail_view, name='request_supervisor_for_custom'),

                       url(r'^employee_dashboard/$', views.employee_dashboard, name='employee_dashboard'),
                       url(r'^request_detail_employee/(?P<pk>\d+)$', views.employee_request_detail_view,
                           name='request_employee'),
                       url(r'^request_detail_employee_for_corporate/(?P<pk>\d+)$',
                           views.employee_request_for_corporate_detail_view, name='request_employee_for_corporate'),
                       url(r'^request_detail_employee_for_custom/(?P<pk>\d+)$',
                           views.employee_custom_request_detail_view, name='request_employee_for_custom'),


                       url(r'^request_detail_reviewer/(?P<pk>\d+)$',
                            views.reviewer_request_detail_view, name='request_reviewer'),

                       url(r'^request_detail_reviewer_for_custom/(?P<pk>\d+)$',
                            views.reviewer_custom_request_detail_view, name='request_reviewer_for_custom'),

                       url(r'^request_detail_reviewer_for_corporate/(?P<pk>\d+)$',
                            views.reviewer_corporate_request_detail_view, name='request_reviewer_for_corporate'),


                       url(r'^request/assign/(?P<pk>\d+)$', views.assign_staff, name='assign'),
                       url(r'^request/begin/(?P<pk>\d+)$', views.begin_request, name='begin'),
                       url(r'^request/reject/(?P<pk>\d+)$', views.reject_request, name='reject'),
                       url(r'^request/incomplete/(?P<pk>\d+)$', views.incomplete_request, name='incomplete'),
                       url(r'^request/submit/(?P<pk>\d+)$', views.submit_request, name='submit'),
                       url(r'^request/return/(?P<pk>\d+)$', views.return_request, name='return'),
                       url(r'^request/return_reviewer/(?P<pk>\d+)$',
                           views.return_request_reviewer, name='return_reviewer'),
                       url(r'^request/delete/(?P<pk>\d+)$', views.delete_request, name='delete'),
                       url(r'^request/archive/(?P<pk>\d+)$', views.archive_request, name='archive'),

                       url(r'^request/corporate/assign/(?P<pk>\d+)$', views.assign_corporate_staff,
                           name='corporate_assign'),
                       url(r'^request/corporate/begin/(?P<pk>\d+)$', views.begin_corporate_request,
                           name='corporate_begin'),
                       url(r'^request/corporate/reject/(?P<pk>\d+)$', views.reject_corporate_request,
                           name='corporate_reject'),
                       url(r'^request/corporate/incomplete/(?P<pk>\d+)$', views.incomplete_corporate_request,
                           name='corporate_incomplete'),
                       url(r'^request/corporate/submit/(?P<pk>\d+)$', views.submit_corporate_request,
                           name='corporate_submit'),
                       url(r'^request/corporate/return/(?P<pk>\d+)$', views.return_corporate_request,
                           name='corporate_return'),
                       url(r'^request/corporate/return_reviewer/(?P<pk>\d+)$', views.return_corporate_request_reviewer,
                           name='corporate_return_reviewer'),

                       url(r'^request/corporate/delete/(?P<pk>\d+)$', views.delete_corporate_request,
                           name='corporate_delete'),
                        
                       url(r'^request/corporate/archive/(?P<pk>\d+)$', views.archive_corporate_request,
                           name='corporate_archive'),

                       url(r'^request/custom/assign/(?P<pk>\d+)$', views.assign_custom_staff,
                           name='custom_assign'),
                       url(r'^request/custom/begin/(?P<pk>\d+)$', views.begin_custom_request,
                           name='custom_begin'),
                       url(r'^request/custom/reject/(?P<pk>\d+)$', views.reject_custom_request,
                           name='custom_reject'),
                       url(r'^request/custom/incomplete/(?P<pk>\d+)$', views.incomplete_custom_request,
                           name='custom_incomplete'),
                       url(r'^request/custom/submit/(?P<pk>\d+)$', views.submit_custom_request,
                           name='custom_submit'),
                       url(r'^request/custom/return/(?P<pk>\d+)$', views.return_custom_request,
                           name='custom_return'),
                       url(r'^request/custom/return_reviewer/(?P<pk>\d+)$', views.return_custom_request_reviewer,
                           name='custom_return_reviewer'),

                       url(r'^request/custom/delete/(?P<pk>\d+)$', views.delete_custom_request,
                           name='custom_delete'),
                       url(r'^request/custom/archive/(?P<pk>\d+)$', views.archive_custom_request,
                           name='custom_archive'),

                        url(r'^request/send_data_form/(?P<pk>\d+)$', views.send_data_form_individual, name='send_data_form'),
                        url(r'^corporate_request/send_data_form/(?P<pk>\d+)$', views.send_data_form_corporate, name='send_data_form_corporate'),
                        url(r'^custom_request/send_data_form/(?P<pk>\d+)$', views.send_data_form_custom, name='send_data_form_custom'),

                        url(r'^archive_bulk_requests/$', views.archive_bulk_request,
                           name='archive_bulk_request'),

                        url(r'^bulk_archive/$', views.archive_bulk_page,
                           name='bulk_archive'),

                       # PDF Report Related URL's

                       url(r'^report/(?P<company_date_id>[-\w_]+).pdf$', views.generate_report_view, name='report'),
                       url(r'^report/corporate/(?P<company_date_id>[-\w_]+).pdf$', views.generate_corporate_report_view,
                           name='corporate_report'),
                       url(r'^report/custom/(?P<company_date_id>[-\w_]+).pdf$', views.generate_custom_report_view,
                           name='custom_report'),

                       url(r'^report_dashboard/$', views.archived_reports, name='report_dashboard'),
                       url(r'^archived_report/(?P<archived_report_id>\d+)/(?P<report_name>[-\w_]+).pdf$',
                           views.generate_archived_report_view, name='archived_report'),

                       # Excel Exporting for Custom Fields
                       # url(r'^export_csv/$', views.archived_reports, name='export_csv'),

                       url(r'^export_requests_to_csv/$',
                           views.ManagerRequestExport.as_view(), name='export_requests_to_csv'),

                        url(r'^export_analyst_requests_to_csv/$',
                           views.AnalystRequestExport.as_view(), name='export_analyst_requests_to_csv'),

                        url(r'^export_supervisor_requests_to_csv/$',
                           views.SupervisorRequestExport.as_view(), name='export_supervisor_requests_to_csv'),
                        
                        url(r'^export_employee_requests_to_csv/$',
                           views.EmployeeRequestExport.as_view(), name='export_employee_requests_to_csv'),

                       # Dynamic Request Forms
                       url(r'^dynamic_request_form_create/(?P<pk>\d+)$',
                           login_required(views.DynamicRequestFormCreation.as_view()),
                           name='dynamic_request_form_create'),
                       url(r'^dynamic_request_form_update/(?P<pk>\d+)$',
                           login_required(views.DynamicRequestFormUpdate.as_view()),
                           name='dynamic_request_form_update'),


                       url(r'^dynamic_request_form_configure/(?P<pk>\d+)$',
                           login_required(views.DynamicRequestFormConfiguration.as_view()),
                           name='dynamic_request_form_configure'),
                       url(r'^dynamic_request_form_configure_update/(?P<pk>\d+)$',
                           login_required(views.DynamicRequestFormConfigurationUpdate.as_view()),
                           name='dynamic_request_form_configure_update'),
                       url(r'^dynamic_request_form_field_delete/(?P<dynamic_request_pk>\d+)/(?P<field_pk>\d+)$',
                           views.delete_dynamic_request_form_field, name='dynamic_request_form_field_delete'),

                       url(r'^ajax_edit_employee/$', views.ajax_change_created_by_employee, name='ajax_edit_employee'),
                       url(r'^ajax_edit_corporate/$', views.ajax_change_created_by_employee_corporate,
                           name='ajax_edit_corporate'),
                       url(r'^ajax_edit_custom/$', views.ajax_change_created_by_employee_custom,
                           name='ajax_edit_custom'),

                       # Manager ajax calls for editing employees
                       url(r'^ajax_edit_analyst/$', views.ajax_change_analyst, name='ajax_edit_analyst'),
                       url(r'^ajax_edit_analyst_corporate/$', views.ajax_change_analyst_corporate,
                           name='ajax_edit_analyst_corporate'),
                       url(r'^ajax_edit_analyst_custom/$', views.ajax_change_analyst_custom,
                           name='ajax_edit_analyst_custom'),

                       # Manager ajax calls for editing reviewers
                       url(r'^ajax_edit_reviewer/$', views.ajax_change_reviewer, name='ajax_edit_reviewer'),

                       url(r'^ajax_edit_reviewer_corporate/$', views.ajax_change_reviewer_corporate,
                           name='ajax_edit_reviewer_corporate'),

                       url(r'^ajax_edit_reviewer_custom/$', views.ajax_change_reviewer_custom,
                           name='ajax_edit_reviewer_custom'),

                       # Manager Ajax calls for changing status of the request
                       url(r'^recall_request/(?P<pk>\d+)$', views.recall_request, name='recall_request'),
                       url(r'^recall_corporate_request/(?P<pk>\d+)$', views.recall_corporate_request,
                           name='recall_corporate_request'),
                       url(r'^recall_custom_request/(?P<pk>\d+)$', views.recall_custom_request,
                           name='recall_custom_request'),

                       url(r'^recall_reassign_request/(?P<pk>\d+)/(?P<analyst_id>\d+)$', views.recall_reassign_request,
                           name='recall_reassign_request'),
                       url(r'^recall_reassign_corporate_request/(?P<pk>\d+)/(?P<analyst_id>\d+)$',
                           views.recall_reassign_corporate_request,
                           name='recall_reassign_corporate_request'),
                       url(r'^recall_reassign_custom_request/(?P<pk>\d+)/(?P<analyst_id>\d+)$',
                           views.recall_reassign_custom_request,
                           name='recall_reassign_custom_request'),

                       #############
                       # CSV EXPORT
                       #############

                       # SUPERVISOR CUSTOM
                       url(r'^supervisor_custom_requests_status_csv/$',
                           views.get_all_custom_request_statuses_for_supervisor_csv,
                           name='supervisor_custom_requests_status_csv'),

                       # SUPERVISOR INDIVIDUAL
                       url(r'^supervisor_individual_requests_status_csv/$',
                           views.get_all_individual_request_statuses_for_supervisor_csv,
                           name='supervisor_individual_requests_status_csv'),

                       # SUPERVISOR CORPORATE
                       url(r'^supervisor_corporate_requests_status_csv/$',
                           views.get_all_corporate_request_statuses_for_supervisor_csv,
                           name='supervisor_corporate_requests_csv'),

                       #############
                       # excel export
                       #############

                       url(r'^supervisor_custom_requests_status_excel/$',
                           views.get_all_custom_request_statuses_for_supervisor_excel,
                           name='supervisor_custom_requests_status_excel'),

                       url(r'^supervisor_individual_requests_status_excel/$',
                           views.get_all_individual_request_statuses_for_supervisor_excel,
                           name='supervisor_individual_requests_status_excel'),

                       url(r'^supervisor_corporate_requests_status_excel/$',
                           views.get_all_corporate_request_statuses_for_supervisor_excel,
                           name='supervisor_corporate_requests_excel'),

                       ###################
                       # DATATABLES
                       #####################


                       # ARCHIVED REPORTS
                       url(r'^archived_reports/all$',
                           login_required(data_tables.ArchivedReportsDatatablesView.as_view()),
                           name='archived_reports'),

                       ###################
                       # EMPLOYEE
                       ###################
                       url(r'^advanced_search_employee/$', views.advanced_search_employee,
                           name='advanced_search_employee'),

                       ###################
                       # SUPERVISOR
                       ###################
                       url(r'^advanced_search_supervisor/$', views.advanced_search_supervisor,
                           name='advanced_search_supervisor'),

                       url(r'^supervisor_report_download/$', views.supervisor_report_download,
                           name='supervisor_report_download'),

                        url(r'^supervisor_archives_view/$', views.supervisor_archives_view,
                           name='supervisor_archives_view'),

                       url(r'^get_supervisor_archives_json/$', views.get_supervisor_archives_json,
                           name='get_supervisor_archives_json'),

                       ###################
                       # MANAGER
                       ###################
                       url(r'^manager_completed_requests/$', views.manager_completed_requests,
                           name='manager_completed_requests'),

                       url(r'^manager_new_requests/$', views.manager_new_requests,
                           name='manager_new_requests'),

                       url(r'^manager_in_progress_requests/$', views.manager_in_progress_requests,
                           name='manager_in_progress_requests'),

                       url(r'^manager_advanced_search/$', views.manager_advanced_search,
                           name='manager_advanced_search'),

                       url(r'^manager/average_time/$',
                           login_required(views.manager_average_request_time_json),
                           name='manager_average_request_time_json'),

                        url(r'^package_dashboard/$',views.package_dashboard,
                        name='package_dashboard'),
                        url(r'^add_package/$', views.add_package, name='add_package'),
                        url(r'^update_package/(?P<dd_pk>\d+)$', views.update_package,
                           name='update_package'),

                       ###################
                       # ANALYST
                       #####################

                       url(r'^analyst_advanced_search/$', views.analyst_advanced_search,
                           name='analyst_advanced_search'),

                        url(r'^analyst_new_requests/$', views.analyst_new_requests,
                           name='analyst_new_requests'),

                        url(r'^analyst_completed_requests/$', views.analyst_completed_requests,
                           name='analyst_completed_requests'),

                        url(r'^analyst_in_progress_requests/$', views.analyst_in_progress_requests,
                           name='analyst_in_progress_requests'),

                       ###################
                       # REVIEWER
                       #####################

                       url(r'^advanced_search_reviewer/$', views.advanced_search_reviewer,
                           name='advanced_search_reviewer'),

                       url(r'^reviewer_dashboard$', views.reviewer_dashboard,
                           name='reviewer_dashboard'),


                        # DATA TABLES

                       url(r'^requests/new_super_table/$',
                           login_required(data_tables.NewAllRequestsDatatablesView.as_view()),
                           name='new_super_table'),

                       url(r'^supervisor_report_download_datatable/$',
                           login_required(data_tables.SupervisorReportsDatatablesView.as_view()),
                           name='supervisor_report_download_datatable'),

                       url(r'^supervisor_completed_requests_datatable/$',
                           login_required(data_tables.SupervisorCompletedRequestsDatatable.as_view()),
                           name='supervisor_completed_requests_datatable'),

                       url(r'^supervisor_in_progress_requests_datatable/$',
                           login_required(data_tables.SupervisorInProgressRequestsDatatable.as_view()),
                           name='supervisor_in_progress_requests_datatable'),

                       url(r'^employee_completed_requests_datatable/$',
                           login_required(data_tables.EmployeeCompletedRequestsDatatable.as_view()),
                           name='employee_completed_requests_datatable'),

                       url(r'^restricted_attachments_datatable/$',
                           login_required(data_tables.RestrictedAttachments.as_view()),
                           name='restricted_attachments_datatable'),

                       url(r'^employee_in_progress_requests_datatable/$',
                           login_required(data_tables.EmployeeInProgressRequestsDatatable.as_view()),
                           name='employee_in_progress_requests_datatable'),

                       url(r'^employee_advanced_requests_datatable/$',
                           login_required(data_tables.EmployeeAllRequestsDatatablesView.as_view()),
                           name='employee_advanced_requests_datatable'),

                       url(r'^manager_new_requests_datatable/$',
                           login_required(data_tables.ManagerNewRequestsDatatable.as_view()),
                           name='manager_new_requests_datatable'),

                       url(r'^manager_advanced_datatable/$',
                           login_required(data_tables.ManagerAdvancedTable.as_view()),
                           name='manager_advanced_datatable'),
                           

                        url(r'^analyst_new_requests_datatable/$',
                           login_required(data_tables.AnalystNewRequestsDatatable.as_view()),
                           name='analyst_new_requests_datatable'),

                       url(r'^analyst_advanced_datatable/$',
                           login_required(data_tables.AnalystAdvancedTable.as_view()),
                           name='analyst_advanced_datatable'),
                        
                        url(r'^reviewer_advanced_datatable/$',
                           login_required(data_tables.ReviewerAdvancedTable.as_view()),
                           name='reviewer_advanced_datatable'),

                       url(r'^celery_runner/$',
                           login_required(views.celery_runner),
                           name='celery_runner'),

                       url(r'^migrate_attachments/$',
                           login_required(views.migrate_attachments),
                           name='migrate_attachments'),

                       url(r'^survey_view/$', views.survey_view,
                           name='survey_view'),
                       # Admin access
                       url(r'^admin_console/', include(admin.site.urls)),
                       ) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Uncomment the next line to serve media files in dev.
if socket.gethostname() == 'CHI1004':
    # urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # urlpatterns += patterns('django.views.static',(r'^media/(?P<path>.*)','serve',
    #   {'document_root': settings.MEDIA_ROOT}),
    # )
    pass

else:
    pass
#
if settings.DEBUG:
    import debug_toolbar

    urlpatterns += patterns('',
                            url(r'^__debug__/', include(debug_toolbar.urls)),
                            )
