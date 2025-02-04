from django.http.response import HttpResponse

from core.diagrams import MonitoringDiagram


def monitoring_diagram(request, device_id):
    diagram = MonitoringDiagram(device_id)
    return HttpResponse(
        content=diagram.plot(),
        content_type='image/svg+xml'
    )
