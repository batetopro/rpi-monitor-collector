from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponseRedirect


from network.arp import ArpCollector


@staff_member_required
def refresh_arp(request):
    arp_collector = ArpCollector()
    arp_collector.collect()
    return HttpResponseRedirect(request.META["HTTP_REFERER"])
