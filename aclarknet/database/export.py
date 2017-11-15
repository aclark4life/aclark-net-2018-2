from django.http import HttpResponse
from django_xhtml2pdf.utils import generate_pdf

# from io import BytesIO


def render_pdf(request, template, context, pk=None):
    response = HttpResponse(content_type='application/pdf')
    company_name = context['company_name']
    model_name = context['model_name']
    model_name = model_name.upper()
    if company_name:
        filename = '_'.join([company_name, model_name, pk])
    else:
        filename = '_'.join(['Company', model_name, pk])
    response['Content-Disposition'] = 'filename=%s.pdf' % filename
    return generate_pdf(
        'pdf_invoice.html', context=context, file_object=response)
