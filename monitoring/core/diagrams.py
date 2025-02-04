import datetime
from io import StringIO
import math


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

    def adjust_ios(self, x, ios, take_log=False):
        if len(ios) <= 1:
            return [], []

        new_x = []
        new_ios = []
        current_io = ios[0]
        for k in range(1, len(ios)):
            if current_io <= ios[k]:
                new_x.append(x[k])
                dio = ios[k] - current_io
                if dio == 0:
                    new_ios.append(0)
                elif take_log:
                    new_ios.append(math.log(dio, 10))
                else:
                    new_ios.append(dio)
                
            current_io = ios[k]

        return new_x, new_ios
    
    def get_queryset(self):
        return DeviceUsageModel.objects.filter(
                device_id=self.device_id,
                time_saved__gt=now() - datetime.timedelta(hours=3)
            ).\
            values_list(
                'time_saved', 'cpu_usage', 'cpu_temperature', 'used_ram',
                'disk_space_available', 'disk_space_used', 'used_swap',
                'total_swap', 'disk_io_read_bytes', 'disk_io_write_bytes',
                'net_io_bytes_recv', 'net_io_bytes_sent',
            ).\
            order_by('time_saved')

    def plot(self):
        x = []
        cpu_usage = []
        cpu_temperature = []
        used_ram = []
        disk_space_usage = []
        used_swap = []
        disk_io_read_bytes = []
        disk_io_write_bytes = []
        net_io_bytes_recv = []
        net_io_bytes_sent = []

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

            if not row[7]:
                used_swap.append(0)
            else:
                used_swap.append(
                    (row[6] / (row[7])) * 100
                )

            disk_io_read_bytes.append(row[8])
            disk_io_write_bytes.append(row[9])
            net_io_bytes_recv.append(row[10])
            net_io_bytes_sent.append(row[11])

        fig, ax = plt.subplots(nrows=9, ncols=1)

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
        ax[2].set_title('Used virtual memory %', fontsize=8)
        ax[2].set_ylim(-5, 105)
        ax[2].set_xlim(x[0], x[-1])
        ax[2].axhline(85, color='r', linestyle='--', linewidth=0.5)
        ax[2].axhline(70, color='y', linestyle='--', linewidth=0.5)

        ax[3].plot(x, used_swap, color='black')
        ax[3].set_title('Used swap memory %', fontsize=8)
        ax[3].set_ylim(-5, 105)
        ax[3].set_xlim(x[0], x[-1])
        ax[3].axhline(85, color='r', linestyle='--', linewidth=0.5)
        ax[3].axhline(70, color='y', linestyle='--', linewidth=0.5)

        ax[4].plot(x, disk_space_usage, color='black')
        ax[4].set_title('Used disk space %', fontsize=8)
        ax[4].set_ylim(-5, 105)
        ax[4].set_xlim(x[0], x[-1])
        ax[4].axhline(85, color='r', linestyle='--', linewidth=0.5)
        ax[4].axhline(70, color='y', linestyle='--', linewidth=0.5)

        dx, disk_io_read_bytes = self.adjust_ios(
            x, disk_io_read_bytes, True
        )
        ax[5].plot(dx, disk_io_read_bytes, color='black')
        ax[5].set_title('Disk read I/O', fontsize=8)
        ax[5].set_xlim(x[0], x[-1])

        dx, disk_io_write_bytes = self.adjust_ios(
            x, disk_io_write_bytes, False
        )
        ax[6].plot(dx, disk_io_write_bytes, color='black')
        ax[6].set_title('Disk write I/O', fontsize=8)
        ax[6].set_xlim(x[0], x[-1])

        dx, net_io_bytes_recv = self.adjust_ios(
            x, net_io_bytes_recv, False
        )
        ax[7].plot(dx, net_io_bytes_recv, color='black')
        ax[7].set_title('Network received bytes', fontsize=8)
        ax[7].set_xlim(x[0], x[-1])

        dx, net_io_bytes_sent = self.adjust_ios(
            x, net_io_bytes_sent, False
        )
        ax[8].plot(dx, net_io_bytes_sent, color='black')
        ax[8].set_title('Network transmitted bytes', fontsize=8)
        ax[8].set_xlim(x[0], x[-1])

        '''
        plt.suptitle(
            host_info.hostname + " on " + str(now().date()),
            fontsize=8, x=-1
        )
        '''

        # plt.plot(x, y)
        plt.gcf().autofmt_xdate()

        fig.autofmt_xdate()
        imgdata = StringIO()
        
        fig.set_size_inches(10, 18)
        fig.tight_layout()
        fig.savefig(imgdata, format='svg')
        imgdata.seek(0)
        data = imgdata.getvalue()

        plt.close()

        return data
