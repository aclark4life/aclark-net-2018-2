from django.http import HttpResponse
from django.utils import timezone
from io import BytesIO
from matplotlib.dates import DateFormatter
from matplotlib.dates import date2num
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
from .query import get_query_string


def get_plot(request):  # http://stackoverflow.com/a/5515994/185820
    """
    """
    costs = get_query_string(request, 'costs')
    grosses = get_query_string(request, 'grosses')
    nets = get_query_string(request, 'nets')
    # Cost
    x1 = [  # http://matplotlib.org/examples/api/date_demo.html
        date2num(timezone.datetime.strptime(i[1], '%Y-%m-%d')) for i in costs
    ]
    y1 = [i[0] for i in costs]
    # Gross
    x2 = [
        date2num(timezone.datetime.strptime(i[1], '%Y-%m-%d')) for i in grosses
    ]
    y2 = [i[0] for i in grosses]
    # Net
    x3 = [date2num(timezone.datetime.strptime(i[1], '%Y-%m-%d')) for i in nets]
    y3 = [i[0] for i in nets]
    figure = Figure()
    canvas = FigureCanvasAgg(figure)
    axes = figure.add_subplot(1, 1, 1)
    axes.grid(True)
    axes.plot(x1, y1)
    axes.plot(x2, y2)
    axes.plot(x3, y3)
    axes.xaxis.set_major_formatter(DateFormatter('%m'))
    # write image data to a string buffer and get the PNG image bytes
    buf = BytesIO()
    canvas.print_png(buf)
    data = buf.getvalue()
    # write image bytes back to the browser
    return HttpResponse(data, content_type="image/png")
