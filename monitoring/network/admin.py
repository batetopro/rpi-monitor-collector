from django.contrib import admin


from network.models import NeighbourModel


class NeighborAdminModel(admin.ModelAdmin):
    change_list_template = 'admin/neighbour_change_list.html'

    fields = ("type", "physical_address", "mask",)

    list_display = (
        "address", "type", "physical_address", "mask",
        "interface", "reverse_dns_lookup"
    )
    list_display_links = ("address", )
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


admin.site.register(NeighbourModel, NeighborAdminModel)
