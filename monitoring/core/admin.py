from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html


from core.models import DeviceModel, HostInfoModel, SSHConfigurationModel, \
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
    class Media:
        js = (
            "js/auto_reload.js",
        )
        css = {
             'all': ('css/admin-extra.css',)
        }

    change_form_template = 'admin/device_change_form.html'
    list_display = [
        "id",
        "device_hostname",
        "device_ram",
        "device_cpu",
        "device_cpu_temperature",
        "device_cpu_frequency",
        "device_disk_space",
        "device_last_seen",
        "device_actions",
    ]

    list_display_links = ["id", ]

    list_filter = ('status', )

    def get_ordering(self, request):
        return ("id", )

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    fieldsets = [
        (
            None,
            {
                "fields": [
                    "device_status",
                    "up_for",
                ],
            },
        ),
        (
            'Usage',
            {
                "fields": [
                    "device_ram",
                    "device_cpu",
                    "device_cpu_temperature",
                    "device_cpu_frequency",
                    "device_disk_space",
                ],
            },
        ),
        (
            'Platform',
            {
                "fields": [
                    "up_since",
                    "device_last_seen",
                    "platform_info",
                ],
            },
        ),
        (
            'Message',
            {
                "fields": [
                    "device_message",
                ],
            },
        ),
    ]

    readonly_fields = (
        "device_status",
        "device_ram",
        "device_cpu",
        "device_cpu_temperature",
        "device_cpu_frequency",
        "device_disk_space",
        "device_last_seen",
        "up_for",
        "up_since",
        "platform_info",
        "device_message",
    )

    search_fields = ("host_info__hostname", )

    @admin.display(description="Actions")
    def device_actions(self, obj):
        actions = [
            '<a href="' +
            reverse('admin:core_devicemodel_change', args=[obj.id]) +
            '">Details</a>',
            '<a href="' +
            reverse('core:monitoring_diagram', args=[obj.id]) +
            '" target="_blank">Plots</a>',
        ]

        return format_html('&nbsp;|&nbsp;'.join(actions))

    @admin.display(description="CPU", ordering='cpu_usage')
    def device_cpu(self, obj):
        if obj.cpu_usage is None:
            return 'N/A'

        if obj.cpu_usage >= 85:
            badge_class = 'bg-danger'
        elif obj.cpu_usage >= 70:
            badge_class = 'bg-warning'
        else:
            badge_class = 'bg-secondary'

        return format_html(
            f'<span class="badge {badge_class}">{obj.cpu_usage} %</span>'
        )

    @admin.display(description="Temperature", ordering='cpu_temperature')
    def device_cpu_temperature(self, obj):
        if obj.cpu_temperature is None:
            return 'N/A'

        if obj.cpu_temperature >= 85:
            badge_class = 'bg-danger'
        elif obj.cpu_temperature >= 70:
            badge_class = 'bg-warning'
        else:
            badge_class = 'bg-secondary'

        return format_html(
            f'<span class="badge {badge_class}">{obj.cpu_temperature} C</span>'
        )

    @admin.display(description="CPU Frequency")
    def device_cpu_frequency(self, obj):
        try:
            max_cpu_frequency = obj.host_info.max_cpu_frequency
        except HostInfoModel.DoesNotExist:
            max_cpu_frequency = '-'

        if obj.cpu_frequency is None:
            cpu_frequency = '-'
        else:
            cpu_frequency = obj.cpu_frequency

        if max_cpu_frequency == '-' and cpu_frequency == '-':
            return 'N/A'

        return format_html(
            f'''<span class="badge bg-light">
                {cpu_frequency} / {max_cpu_frequency} GHz
            </span>
            '''
        )

    @admin.display(description="Used disk", ordering='disk_space_used')
    def device_disk_space(self, obj):
        if obj.disk_space_used is not None:
            used_disk_space = obj.disk_space_used
        else:
            used_disk_space = '-'

        if obj.disk_space_available is not None:
            available_disk_space = obj.disk_space_available
        else:
            available_disk_space = '-'

        if available_disk_space != '-' and used_disk_space != '-':
            total_disk_space = available_disk_space + used_disk_space
            used_space_ratio = (used_disk_space / total_disk_space) * 100

            if used_space_ratio >= 85:
                badge_class = 'bg-danger'
            elif used_space_ratio >= 70:
                badge_class = 'bg-warning'
            else:
                badge_class = 'bg-secondary'

            show_used_disk_space = round(used_disk_space / (1024 * 1024), 2)
            show_total_disk_space = round(total_disk_space / (1024 * 1024), 2)
            return format_html(
                f'''<span class="badge {badge_class}">
                    {show_used_disk_space} / {show_total_disk_space} GBi
                </span>
                '''
            )

        else:
            return 'N/A'

    @admin.display(description="Hostname", ordering='host_info__hostname')
    def device_hostname(self, obj):
        if obj.status == 'connected':
            badge_class = 'bg-success'
        elif obj.status == 'disconnected':
            badge_class = 'bg-danger'
        else:
            badge_class = 'bg-light'

        try:
            hostname = obj.host_info.hostname
        except HostInfoModel.DoesNotExist:
            return format_html(
                f'''
                <span class="badge bg-warning">
                    {obj.ssh_conf.hostname}
                </span>
                '''
            )

        return format_html(
            f'<span class="badge {badge_class}">{hostname}</span>'
        )

    @admin.display(description="Last seen", ordering='last_seen')
    def device_last_seen(self, obj):
        if obj.last_seen:
            return obj.last_seen
        return 'N/A'

    @admin.display(description="Message")
    def device_message(self, obj):
        if obj.message:
            return format_html(
                f'''
                <textarea cols="40" rows="10" class="vLargeTextField"
                    readonly>{obj.message}</textarea>
                ''')
        return 'N/A'

    @admin.display(description="Used RAM", ordering='used_ram')
    def device_ram(self, obj):
        if obj.used_ram is not None:
            used_ram = obj.used_ram
        else:
            used_ram = '-'

        try:
            total_ram = obj.host_info.total_ram
        except HostInfoModel.DoesNotExist:
            total_ram = '-'

        if used_ram == '-' and total_ram == '-':
            return 'N/A'

        if used_ram == '-' or total_ram == '-':
            badge_class = 'bg-light'
        else:
            ram_ratio = (used_ram / total_ram) * 100

            if ram_ratio >= 85:
                badge_class = 'bg-danger'
            elif ram_ratio >= 70:
                badge_class = 'bg-warning'
            else:
                badge_class = 'bg-secondary'

        return format_html(
            f'''
            <span class="badge {badge_class}">
                {used_ram} / {total_ram} MB
            </span>'''
        )

    @admin.display(description="Status", ordering='status')
    def device_status(self, obj):
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

    @admin.display(description="Info")
    def platform_info(self, obj):
        return format_html('<pre>' + obj.get_platform_info() + '</pre>')

    @admin.display(description="Up for", ordering='up_since')
    def up_for(self, obj):
        return obj.last_seen - obj.host_info.up_since

    @admin.display(description="Up since", ordering='up_since')
    def up_since(self, obj):
        return obj.host_info.up_since


class SSHConfigruationAdminModel(admin.ModelAdmin):
    fieldsets = [
        (
            "Connection",
            {
                "fields": ["username", "hostname", "port"],
            },
        ),
        (
            "SSH key",
            {
                "fields": ["ssh_key", ],
            },
        ),
        (
            "Monitoring",
            {
                "fields": ["monitoring_path", "monitoring_url"],
            },
        ),
    ]

    list_display = [
        "username", "hostname", "port", "config_actions"
    ]

    list_display_links = ["hostname", ]

    search_fields = ("username", "hostname")

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def get_ordering(self, request):
        return ("hostname", )

    @admin.display(description="Actions")
    def config_actions(self, obj):
        actions = [
            '<a href="' +
            reverse(
                'admin:core_sshconfigurationmodel_change',
                args=[obj.device_id]
            ) +
            '">Edit</a>',
            '<a href="' +
            reverse('admin:core_devicemodel_change', args=[obj.device_id]) +
            '">View device</a>'
        ]

        return format_html('&nbsp;|&nbsp;'.join(actions))


admin.site.register(DeviceModel, DeviceAdminModel)
admin.site.register(SSHKeyModel, SSHKeyAdminModel)
admin.site.register(SSHConfigurationModel, SSHConfigruationAdminModel)
