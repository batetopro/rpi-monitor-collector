import socket


from django.conf import settings
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html, escape


from core.host import HostRegistry
from core.models import HostModel,  NetworkInterfaceModel, \
    SSHConnectionModel, SSHKeyModel


class SSHKeyAdminModel(admin.ModelAdmin):
    list_display = ("name", )
    search_fields = ("name", )

    def get_ordering(self, request):
        return ("name", )

    fieldsets = [
        (
            None,
            {
                "fields": [
                    "name",
                    "identity_file",
                    "public_key",
                ],
            },
        ),
    ]


class HostAdminModel(admin.ModelAdmin):
    change_form_template = 'admin/device_change_form.html'
    change_list_template = "admin/device_change_list.html"

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}

        info = HostRegistry.get_host(object_id)

        for k, v in info.items():
            if k not in extra_context:
                extra_context[k] = v

        return super().change_view(request, object_id, form_url, extra_context)

    def has_add_permission(self, request, obj=None):
        return False


class NetworkInterfaceAdminModel(admin.ModelAdmin):
    list_display = [
        "host_link", "isup", "name", "ip4_address", "ip6_address",
    ]
    list_display_links = ["name", ]
    list_filter = ("host", )

    ordering = ("host__hostname", "name")

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    @admin.display(description="Host", ordering="host")
    def host_link(self, obj):
        link = reverse("management:core_hostmodel_change", args=[obj.host_id])
        return format_html(f'<a href="{link}">{escape(obj.host.hostname)}</a>')


class SSHConnectionAdminModel(admin.ModelAdmin):
    change_form_template = 'admin/connection_change_form.html'

    fieldsets = [
        (
            "Target",
            {
                "fields": ["username", "hostname", "port"],
            }
        ),
        (
            "Connection",
            {
                "fields": ["state", "status", "message"],
            },
        ),
        (
            "SSH key",
            {
                "fields": ["ssh_key", ],
            },
        ),
        (
            "Virtual environment",
            {
                "fields": ["monitoring_path", ],
            },
        ),
    ]

    list_display = ["runtime_state", "target", "config_actions", ]

    list_display_links = ["target", ]

    ordering = ("-status", "state", "hostname", )

    readonly_fields = ["state", "message", ]

    search_fields = ("username", "hostname")

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}

        host = HostModel.objects.filter(connection_id=object_id).first()
        if host:
            extra_context['host_id'] = host.pk
        else:
            extra_context['host_id'] = None

        return super().change_view(request, object_id, form_url, extra_context)

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def has_delete_permission(self, request, obj=None):
        if obj:
            path = f"{obj._meta.app_label}/{obj._meta.model_name}"
            if path in request.path:
                return False
        return True

    @admin.display(description="Actions")
    def config_actions(self, obj):
        actions = []

        if obj.status == 'enabled':
            actions.append(
                '<a href="' +
                reverse('core:ssh_deploy', args=[obj.pk]) +
                '">Deploy</a>'
            )
            actions.append(
                '<a href="' +
                reverse('core:ssh_disable', args=[obj.pk]) +
                '">Disable</a>'
            )
        else:
            actions.append(
                '<a href="' +
                reverse('core:ssh_enable', args=[obj.pk]) +
                '">Enable</a>'
            )

        return format_html('&nbsp;|&nbsp;'.join(actions))

    @admin.display(description="State", ordering="state")
    def runtime_state(self, obj):
        if obj.status == 'disabled':
            return obj.status
        return obj.state

    @admin.display(description="Target", ordering="hostname")
    def target(self, obj):
        return str(obj)


hostname = socket.gethostname()


class MyAdminSite(admin.AdminSite):
    # Text to put at the end of each page's <title>.
    site_title = settings.LOCATION + '@' + hostname

    # Text to put in each page's <h1> (and above login form).
    site_header = settings.LOCATION + '@' + hostname

    # Text to put at the top of the admin index page.
    index_title = 'Monitor your raspberry'


admin_site = MyAdminSite(name='management')


admin_site.register(HostModel, HostAdminModel)
admin_site.register(NetworkInterfaceModel, NetworkInterfaceAdminModel)
admin_site.register(SSHKeyModel, SSHKeyAdminModel)
admin_site.register(SSHConnectionModel, SSHConnectionAdminModel)
