from django.contrib.admin.views.decorators import staff_member_required
from django.core.management import call_command
from django.http import HttpResponseRedirect


@staff_member_required
def refresh_arp(request):
    call_command('refresh_arp')
    return HttpResponseRedirect(request.META["HTTP_REFERER"])
