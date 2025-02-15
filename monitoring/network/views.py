from django.contrib.admin.views.decorators import staff_member_required
from django.core.management import call_command
from django.http import HttpResponseRedirect
from filelock import Timeout


@staff_member_required
def refresh_arp(request):
    try:
        call_command('refresh_arp')
    except Timeout:
        pass

    return HttpResponseRedirect(request.META["HTTP_REFERER"])
