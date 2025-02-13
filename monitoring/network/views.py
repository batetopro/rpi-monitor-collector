from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponseRedirect


from network.arp import ArpCollector
from network.dns import DnsCollector


@staff_member_required
def refresh_arp(request):
    arp_collector = ArpCollector()
    arp_collector.collect()
    return HttpResponseRedirect(request.META["HTTP_REFERER"])


@staff_member_required
def refresh_dns(request):
    arp_collector = DnsCollector()
    arp_collector.collect()
    return HttpResponseRedirect(request.META["HTTP_REFERER"])
