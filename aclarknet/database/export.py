from django.http import HttpResponse
from django_xhtml2pdf.utils import generate_pdf

# from io import BytesIO


def render_pdf(request, template, context, pk=None):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename=test.pdf'
    return generate_pdf(
        'pdf_invoice.html', context=context, file_object=response)
