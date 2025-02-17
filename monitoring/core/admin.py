from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html


from core.models import DeviceModel, HostInfoModel, SSHConnectionModel, \
    SSHKeyModel


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


class DeviceAdminModel(admin.ModelAdmin):
    change_form_template = 'admin/device_change_form.html'
    change_list_template = "admin/device_change_list.html"

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}

        device = DeviceModel.objects.get(pk=object_id)

        try:
            host_info = device.host_info
            extra_context['hostname'] = host_info.hostname
            extra_context['platform'] = {
                'model': host_info.model,
                'os_name': host_info.os_name,
                'system': host_info.system,
                'machine': host_info.machine,
                'processor': host_info.processor,
                'platform': host_info.platform,
            }
            extra_context['number_of_cpus'] = host_info.number_of_cpus
            extra_context['max_cpu_frequency'] = \
                round(host_info.max_cpu_frequency)
            extra_context['total_ram'] = \
                round(host_info.total_ram / (1024 * 1024), 2)

        except HostInfoModel.DoesNotExist:
            extra_context['hostname'] = device.ssh_conf.hostname
            extra_context['platform'] = None
            extra_context['number_of_cpus'] = None
            extra_context['max_cpu_frequency'] = None
            extra_context['total_ram'] = None

        extra_context['device_id'] = object_id
        extra_context['status'] = device.status

        if device.status == 'connected':
            extra_context['status_class'] = 'bg-success'
        elif device.status == 'disconnected':
            extra_context['status_class'] = 'bg-danger'
        else:
            extra_context['status_class'] = 'bg-secondary'

        return super(DeviceAdminModel, self).change_view(
            request,
            object_id,
            form_url=form_url,
            extra_context=extra_context
        )

    def has_add_permission(self, request, obj=None):
        return False


class SSHConnectionAdminModel(admin.ModelAdmin):
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
                "fields": ["state", "status"],
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

    list_display = ["state", "target", "config_actions", ]

    list_display_links = ["target", ]

    readonly_fields = ["state", ]

    search_fields = ("username", "hostname")

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def get_ordering(self, request):
        return ("hostname", )

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
                reverse('core:ssh_disable', args=[obj.device_id]) +
                '">Disable</a>'
            )
        else:
            actions.append(
                '<a href="' +
                reverse('core:ssh_enable', args=[obj.device_id]) +
                '">Enable</a>'
            )
        if obj.device_id:
            actions.append(
                '<a href="' +
                reverse(
                    'admin:core_devicemodel_change', args=[obj.device_id]
                ) +
                '">View device</a>'
            )

        return format_html('&nbsp;|&nbsp;'.join(actions))

    @admin.display(description="Target", ordering="hostname")
    def target(self, obj):
        return str(obj)


admin.site.register(DeviceModel, DeviceAdminModel)
admin.site.register(SSHKeyModel, SSHKeyAdminModel)
admin.site.register(SSHConnectionModel, SSHConnectionAdminModel)
