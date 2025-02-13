from django.contrib import admin
from network.models import DnsRecordModel, NeighbourModel


class DnsAdminModel(admin.ModelAdmin):
    change_list_template = 'admin/dns_change_list.html'

    list_display = ("address", "domain", )
    list_filter = ("address", )
    readonly_fields = ("address", "domain", )
    search_fields = ("domain", )

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
