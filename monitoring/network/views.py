from django.contrib.admin.views.decorators import staff_member_required
from django.core.management import call_command
from django.http import HttpResponseRedirect
from filelock import Timeout


@staff_member_required
def make_pings(request):
    if request.method == 'POST':
        try:
            call_command('make_pings')
        except Timeout:
            pass

    return HttpResponseRedirect(request.META["HTTP_REFERER"])


@staff_member_required
def refresh_arp(request):
    if request.method == 'POST':
        try:
            call_command('refresh_arp')
        except Timeout:
            pass

    return HttpResponseRedirect(request.META["HTTP_REFERER"])
