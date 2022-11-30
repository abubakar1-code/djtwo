from django import template
import datetime
import math
import os
from django.contrib.contenttypes.models import ContentType
from ..models import CustomRequest, Request, CorporateRequest, BaseRequestStatus
register = template.Library()

@register.filter(name='timeuntil_in_hours')
def timeuntil_in_hours(value):
    value = value.replace(tzinfo=None)
    time_alive = datetime.datetime.now() - value
    time_alive = time_alive.total_seconds()/3600
    time_alive = math.floor(time_alive * 10 ** 1) / 10 ** 1
    time_left = 72-time_alive
    return time_left

@register.filter(name='is_custom_request')
def is_custom_request(content_type):
    if content_type == ContentType.objects.get_for_model(CustomRequest):
        return True
    return False

@register.filter(name='is_corporate_request')
def is_custom_request(content_type):
    if content_type == ContentType.objects.get_for_model(CorporateRequest):
        return True
    return False

@register.filter(name='is_individual_request')
def is_custom_request(content_type):
    if content_type == ContentType.objects.get_for_model(Request):
        return True
    return False

@register.filter(name='get_status')
def get_status(status):
    status_name = BaseRequestStatus.REQUEST_STATUS_CHOICES[status][1]
    return status_name


@register.filter(name='get_file_base_name')
def get_file_base_name(file_name):
    return os.path.basename(file_name)
