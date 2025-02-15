from django.contrib import admin
from django.utils.html import format_html


from network.models import NeighbourModel


class NeighborAdminModel(admin.ModelAdmin):
    class Media:
        css = {
             'all': ('css/admin-extra.css',)
        }

    change_list_template = 'admin/neighbour_change_list.html'

    fields = (
        "status_badge", "type", "physical_address", "mask",
    )

    list_display = (
        "status_badge", "address", "type", "physical_address", "mask",
        "interface", "reverse_dns_lookup"
    )
    list_display_links = ("address", )
    list_filter = ("interface", "type", )

    readonly_fields = (
        "status_badge", "address", "type", "physical_address", "mask",
        "interface",
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

    @admin.display(description="Status", ordering='status')
    def status_badge(self, obj):
        if obj.status == 'connected':
            badge_class = 'bg-success'
        elif obj.status == 'disconnected':
            badge_class = 'bg-danger'
        else:
            badge_class = 'bg-light'

        return format_html(
            f'''
            <span class="badge {badge_class}">
            {obj.status}
            </span>
            '''
        )


admin.site.register(NeighbourModel, NeighborAdminModel)
