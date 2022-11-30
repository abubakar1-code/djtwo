import StringIO, ho.pisa, os
from django.template.defaultfilters import slugify
from django.http import HttpResponse
from django.template.loader import get_template
from django.template import Context
from .models import Reports, Request, CustomRequest
from django.core.files.base import ContentFile

from pyPdf import PdfFileWriter, PdfFileReader
     
def generate_pdf(template_file, context={}):
    #to avoid using a temporary file StringIO has to be used
    pdf = StringIO.StringIO()
    template = get_template(template_file)

    html_pdf = template.render(Context(context))
    pdf_status = ho.pisa.pisaDocument(StringIO.StringIO(html_pdf), pdf)

    if pdf_status.err:
        #catch it in the invoking view
        raise Exception('PDF generation failed. Please check character encoding.')

    return HttpResponse(pdf.getvalue(), content_type='application/pdf')


def generate_report_pdf_file(template_file, context={}):
    #to avoid using a temporary file StringIO has to be used
    pdf = StringIO.StringIO()
    template = get_template(template_file)

    html_pdf = template.render(Context(context))
    pdf_status = ho.pisa.pisaDocument(StringIO.StringIO(html_pdf), pdf)

    if pdf_status.err:
        #catch it in the invoking view
        raise Exception('PDF generation failed. Please check character encoding.')

    value = pdf.getvalue()

    pdf_file = ContentFile(value)

    return pdf_file


def generate_archived_pdf(html_pdf):
    pdf = StringIO.StringIO()
    pdf_status = ho.pisa.pisaDocument(StringIO.StringIO(html_pdf), pdf)

    if pdf_status.err:
        #catch it in the invoking view
        raise Exception('PDF generation failed. Please check character encoding.')

    return HttpResponse(pdf.getvalue(), content_type='application/pdf')


def archive_pdf(template_file, request, context={}):
    #to avoid using a temporary file StringIO has to be used
    pdf = StringIO.StringIO()
    template_name = template_file[8:]
    template = get_template(template_file)
    html_pdf = template.render(Context(context))
    pdf_status = ho.pisa.pisaDocument(StringIO.StringIO(html_pdf), pdf)

    if pdf_status.err:
        #catch it in the invoking view
        raise Exception('PDF generation failed. Please check character encoding.')


    if isinstance(request, Request):
        report = Reports(name="%s_%s" % (slugify(request.created_by.company.name), request.display_id),
                         data=html_pdf, created_by=request.created_by, report_request_type="Individual Request",
                         report_template=template_name)
    elif isinstance(request, CustomRequest):
        report = Reports(name="%s_%s" % (slugify(request.created_by.company.name), request.display_id),
                         data=html_pdf, created_by=request.created_by, report_request_type=request.dynamic_request_form.name,
                         report_template=template_name)
    else:
        report = Reports(name="%s_%s" % (slugify(request.created_by.company.name), request.display_id),
                         data=html_pdf, created_by=request.created_by, report_request_type="Corporate Request",
                         report_template=template_name)

    report.save()

    return True



def append_pdf(input,output):
    [output.addPage(input.getPage(page_num)) for page_num in range(input.numPages)]

def join_pdf(file_list):
    pdf = StringIO.StringIO()
    output = PdfFileWriter()
    for file in file_list:
        append_pdf(PdfFileReader(file),output)

    output.write(pdf)

    return pdf.getvalue()