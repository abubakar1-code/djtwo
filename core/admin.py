from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin

from . import models
from core.forms import CompanyAdminForm

from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django import forms


class RequestAdmin(admin.ModelAdmin):
    # ...
    list_display = ('display_id', 'first_name', 'last_name', 'assignment', 'created_by')
    exclude = ('in_progress_status','completed_status')
    search_fields = ['display_id']
    list_filter = ['created_by']

    def save_form(self,request,form,change):
        if change and "client_attachment" in form.changed_data:
            request = models.Request.objects.get(display_id=form.cleaned_data["display_id"])
            if form.cleaned_data["client_attachment"] == False:
                models.ClientAttachment.objects.filter(request=request).delete()
            elif form.cleaned_data["client_attachment"]:
                models.ClientAttachment.objects.filter(request=request).delete()
                models.ClientAttachment(created_by=request.created_by, request=request,
                                                            attachment=form.cleaned_data["client_attachment"]).save()

        return form.save(commit=False)


class CorporateRequestAdmin(admin.ModelAdmin):
    # ...
    list_display = ('display_id', 'company_name', 'assignment')
    exclude = ('in_progress_status','completed_status')
    search_fields = ['display_id']

    def save_form(self,request,form,change):
        if change and "client_attachment" in form.changed_data:
            corporate_request = models.CorporateRequest.objects.get(display_id=form.cleaned_data["display_id"])
            if form.cleaned_data["client_attachment"] == False:
                models.ClientAttachmentCorporate.objects.filter(request=corporate_request).delete()
            elif form.cleaned_data["client_attachment"]:
                models.ClientAttachmentCorporate.objects.filter(request=corporate_request).delete()
                models.ClientAttachmentCorporate(created_by=corporate_request.created_by, request=corporate_request,
                                                            attachment=form.cleaned_data["client_attachment"]).save()

        return form.save(commit=False)


class CustomRequestAdmin(admin.ModelAdmin):
    # ...
    list_display = ('display_id', 'name', 'assignment', 'request_type', 'created_by')
    exclude = ('in_progress_status', 'completed_status')
    search_fields = ['display_id']

    def save_form(self,request,form,change):
        if change and "client_attachment" in form.changed_data:
            custom_request = models.CustomRequest.objects.get(display_id=form.cleaned_data["display_id"])
            if form.cleaned_data["client_attachment"] == False:
                models.ClientAttachmentCustom.objects.filter(request=custom_request).delete()
            elif form.cleaned_data["client_attachment"]:
                models.ClientAttachmentCustom.objects.filter(request=custom_request).delete()
                models.ClientAttachmentCustom(created_by=custom_request.created_by, request=custom_request,
                                                            attachment=form.cleaned_data["client_attachment"]).save()

        return form.save(commit=False)


class StatusAdmin(admin.ModelAdmin):
    # ...
    list_display = ('content_object', 'content_type', 'status')
    exclude = ('content_object', 'content_type', 'object_id')
    list_filter = ['status']
    search_fields = ['object_id']

class CorporateRequestServiceStatusAdmin(admin.ModelAdmin):
    list_display = ('request', 'service', 'comments')
    exclude = ('request',)


class CustomRequestServiceStatusAdmin(admin.ModelAdmin):
    list_display = ('request', 'service', 'comments')
    search_fields = ['request__id']
    exclude = ('request',)


class RequestServiceStatusAdmin(admin.ModelAdmin):
    list_display = ('request', 'service', 'comments')
    exclude = ('request',)


class CompanyEmployeeAdmin(admin.ModelAdmin):
    # ...
    list_display = ('user', 'company')
    search_fields = ['user__username', 'company__name']


class SpotLitStaffAdmin(admin.ModelAdmin):
    fields = ('user', 'phone_number')


class DueDiligenceTypeAdmin(admin.ModelAdmin):
    pass


class ServiceAdmin(admin.ModelAdmin):
    pass


class DueDiligenceTypeServicesAdmin(admin.ModelAdmin):
    list_display = ('due_diligence_type', 'service')
    list_filter = ['due_diligence_type']


class CompanyDueDiligenceTypeSelectionAdmin(admin.ModelAdmin):
    list_display = ('__unicode__','is_public')
    list_filter = ['is_public']
    pass


class CompanyServiceSelectionAdmin(admin.ModelAdmin):
    pass


class AddressAdmin(admin.ModelAdmin):
    pass

class RequestDetailStatusAdmin(admin.ModelAdmin):
    pass

class CorporateRequestDetailStatusAdmin(admin.ModelAdmin):
    pass

class CustomRequestDetailStatusAdmin(admin.ModelAdmin):
    pass

class CompanyAdmin(admin.ModelAdmin):

    form = CompanyAdminForm

    def save(self, commit=True):
        individual_template = self.cleaned_data.get('individual_request', None)
        corporate_template = self.cleaned_data.get('corporate_request', None)
        return super(CompanyAdminForm,  self).save(commit=commit)


class RequestFormFieldTypesAdmin(admin.ModelAdmin):
    pass


class LayoutGroupSectionsAdmin(admin.ModelAdmin):
    pass


class DynamicRequestFormFieldsAdmin(admin.ModelAdmin):
    pass


class DynamicRequestFormAdmin(admin.ModelAdmin):
    list_display = ('company', 'name')

class SurchargeFormAdmin(admin.ModelAdmin):
    pass

class ChargeTypeFormAdmin(admin.ModelAdmin):
    pass

class CompanyDisabledPackageAdmin(admin.ModelAdmin):
    pass

class ClientAttachmentAdmin(admin.ModelAdmin):
    pass

class ClientAttachmentCorporateAdmin(admin.ModelAdmin):
    pass
class ClientAttachmentCustomAdmin(admin.ModelAdmin):
    pass

admin.site.register(models.Request, RequestAdmin)
admin.site.register(models.Status, StatusAdmin)
admin.site.register(models.CorporateRequest, CorporateRequestAdmin)
admin.site.register(models.CorporateRequestServiceStatus, CorporateRequestServiceStatusAdmin)
admin.site.register(models.RequestServiceStatus, RequestServiceStatusAdmin)
admin.site.register(models.Company, CompanyAdmin)
admin.site.register(models.CompanyEmployee, CompanyEmployeeAdmin)
admin.site.register(models.SpotLitStaff, SpotLitStaffAdmin)
admin.site.register(models.DueDiligenceType, DueDiligenceTypeAdmin)
admin.site.register(models.Service, ServiceAdmin)
admin.site.register(models.CompanyDueDiligenceTypeSelection, CompanyDueDiligenceTypeSelectionAdmin)
admin.site.register(models.DueDiligenceTypeServices, DueDiligenceTypeServicesAdmin)
admin.site.register(models.CompanyServiceSelection, CompanyServiceSelectionAdmin)
admin.site.register(models.Address, AddressAdmin)
admin.site.register(models.RequestFormFieldTypes, RequestFormFieldTypesAdmin)
admin.site.register(models.LayoutGroupSections, LayoutGroupSectionsAdmin)
admin.site.register(models.CustomRequest, CustomRequestAdmin)
admin.site.register(models.CustomRequestServiceStatus, CustomRequestServiceStatusAdmin)
admin.site.register(models.DynamicRequestForm, DynamicRequestFormAdmin)
admin.site.register(models.DynamicRequestFormFields, DynamicRequestFormFieldsAdmin)
admin.site.register(models.Surcharge, SurchargeFormAdmin)
admin.site.register(models.ChargeType, ChargeTypeFormAdmin)
admin.site.register(models.CompanyDisabledPackage,CompanyDisabledPackageAdmin)
admin.site.register(models.ClientAttachment,ClientAttachmentAdmin)
admin.site.register(models.ClientAttachmentCorporate,ClientAttachmentCorporateAdmin)
admin.site.register(models.ClientAttachmentCustom,ClientAttachmentCustomAdmin)
admin.site.register(models.RequestDetailStatus,RequestDetailStatusAdmin)
admin.site.register(models.CorporateRequestDetailStatus,CorporateRequestDetailStatusAdmin)
admin.site.register(models.CustomRequestDetailStatus,CustomRequestDetailStatusAdmin)
