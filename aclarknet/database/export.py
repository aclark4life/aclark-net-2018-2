from django.http import HttpResponse
from django_xhtml2pdf.utils import generate_pdf
from io import BytesIO
from .doc import generate_doc


def render_pdf(request, template, context, pk=None, company_name=None): 
    filename = 'export.pdf'
    if company_name and pk:
        filename = '%s_%s_%s.pdf' % (company_name, 'invoice'.upper(), pk)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename=%s' % filename
    return generate_pdf(
        'invoice_pdf.html', context=context, file_object=response)


def render_doc(request, template, context, pk=None):
    """
    """
    # https://stackoverflow.com/a/24122313/185820
    document = generate_doc(context['item'])
    f = BytesIO()
    document.save(f)
    length = f.tell()
    f.seek(0)
    content_type = 'application/vnd.openxmlformats-'
    content_type += 'officedocument.wordprocessingml.document'
    response = HttpResponse(f.getvalue(), content_type=content_type)
    response['Content-Disposition'] = 'filename=test.docx'
    response['Content-Length'] = length
    return response
