import datetime
from io import StringIO


from django.utils.timezone import now
import matplotlib
import matplotlib.pyplot as plt


from core.models import DeviceUsageModel, DeviceModel


matplotlib.use('Agg')


class MonitoringDiagram:
    title = ''

    @property
    def device_id(self):
        return self._device_id

    def __init__(self, device_id):
        self._device_id = device_id

    def get_queryset(self):
        return DeviceUsageModel.objects.filter(
                device_id=self.device_id,
                time_saved__gt=now() - datetime.timedelta(hours=3)
            ).\
            values_list(
                'time_saved', 'cpu_usage', 'cpu_temperature', 'used_ram',
                'disk_space_available', 'disk_space_used',
            ).\
            order_by('time_saved')

    def plot(self):
        x = []
        cpu_usage = []
        cpu_temperature = []
        used_ram = []
        disk_space_usage = []

        host_info = DeviceModel.objects.\
            get(id=self.device_id).\
            host_info

        total_ram = host_info.total_ram

        for row in self.get_queryset():
            x.append(row[0])
            cpu_usage.append(row[1])
            cpu_temperature.append(row[2])
            used_ram.append((row[3] / total_ram) * 100)
            disk_space_usage.append(
                (row[5] / (row[4] + row[5])) * 100
            )

        fig, ax = plt.subplots(nrows=4, ncols=1)

        ax[0].plot(x, cpu_usage, color='black')
        ax[0].set_title('CPU Usage %', fontsize=8)
        ax[0].set_ylim(-5, 105)
        ax[0].set_xlim(x[0], x[-1])
        ax[0].axhline(85, color='r', linestyle='--', linewidth=0.5)
        ax[0].axhline(70, color='y', linestyle='--', linewidth=0.5)

        ax[1].plot(x, cpu_temperature, color='black')
        ax[1].set_title('CPU Temperatire C', fontsize=8)
        ax[1].set_ylim(-5, 105)
        ax[1].set_xlim(x[0], x[-1])
        ax[1].axhline(85, color='r', linestyle='--', linewidth=0.5)
        ax[1].axhline(70, color='y', linestyle='--', linewidth=0.5)

        ax[2].plot(x, used_ram, color='black')
        ax[2].set_title('Used RAM', fontsize=8)
        # ax[2].set_ylim(-5, 105)
        ax[2].set_xlim(x[0], x[-1])
        ax[2].axhline(85, color='r', linestyle='--', linewidth=0.5)
        ax[2].axhline(70, color='y', linestyle='--', linewidth=0.5)

        ax[3].plot(x, disk_space_usage, color='black')
        ax[3].set_title('Used disk space %', fontsize=8)
        ax[3].set_ylim(-5, 105)
        ax[3].set_xlim(x[0], x[-1])
        ax[3].axhline(85, color='r', linestyle='--', linewidth=0.5)
        ax[3].axhline(70, color='y', linestyle='--', linewidth=0.5)

        # plt.suptitle(self.title)
        plt.suptitle(
            host_info.hostname + " on " + str(now().date()),
            fontsize=10
        )

        # plt.plot(x, y)
        plt.gcf().autofmt_xdate()

        fig.autofmt_xdate()
        imgdata = StringIO()
        fig.tight_layout()
        fig.set_size_inches(10, 8)
        fig.savefig(imgdata, format='svg')
        imgdata.seek(0)
        data = imgdata.getvalue()

        plt.close()

        return data
