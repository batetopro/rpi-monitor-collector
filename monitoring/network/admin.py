from django.contrib import admin
from django.utils.html import format_html


from network.models import DnsRecordModel, NeighbourModel


class DnsAdminModel(admin.ModelAdmin):
    change_list_template = 'admin/dns_change_list.html'

    list_display = ("address", "domain_link", )
    list_filter = ("address", )
    readonly_fields = ("address", "domain", )
    search_fields = ("domain", )

    @admin.display(description="Domain", ordering='domain')
    def domain_link(self, obj):
        return format_html(
            '<a href="http://' + obj.domain + '/" target="_blank">' +
            obj.domain +
            '</a>'
        )

    def get_ordering(self, request):
        return ("address", )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class NeighborAdminModel(admin.ModelAdmin):
    change_list_template = 'admin/neighbour_change_list.html'

    list_display = (
        "address", "type", "physical_address", "mask", "interface",
    )
    list_filter = ("interface", "type", )

    readonly_fields = (
        "address", "type", "physical_address", "mask", "interface",
    )
    search_fields = ("address", )

    def get_ordering(self, request):
        return ("interface", "address")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(DnsRecordModel, DnsAdminModel)
admin.site.register(NeighbourModel, NeighborAdminModel)
