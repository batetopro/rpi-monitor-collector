import datetime
import json
import os
import time
import threading


from django.template import Context, Template
from paramiko import AutoAddPolicy, SSHClient, SSHConfig


from core.host_info import HostInfo
from core.models import DeviceModel


class SSHCollector:
    @property
    def device(self):
        return self._device

    @property
    def host_info(self):
        return HostInfo(self.device)

    @property
    def ssh_conf_template(self):
        if self._ssh_conf_template is None:
            template_path = os.path.join(
                os.path.dirname(__file__),
                'ssh_conf_template.txt'
            )

            with open(template_path, "r") as fp:
                self._ssh_conf_template = Template(fp.read())

        return self._ssh_conf_template

    def __init__(self, device: DeviceModel):
        self._device = device

        self._host_info = None
        self._ssh_conf_template = None
        self._should_stop = False

    def collect(self):
        while True:
            try:
                conf = self.get_ssh_conf()
            except Exception as ex:
                self.handle_error(ex.__repr__(), 60)
                continue

            with SSHClient() as client:
                client.set_missing_host_key_policy(AutoAddPolicy())

                try:
                    client.connect(
                        hostname=conf['hostname'],
                        port=conf['port'],
                        username=conf['user'],
                        allow_agent=True,
                    )
                except Exception as ex:
                    self.handle_error(ex.__repr__(), 60)
                    continue

                self.device.status = 'connected'
                self.device.message = None
                self.device.save()

                try:
                    if not self.collect_host_info(client):
                        time.sleep(60)
                        continue
                except Exception as ex:
                    self.handle_error(ex.__repr__(), 60)
                    continue

                while True:
                    try:
                        if not self.collect_usage(client):
                            time.sleep(60)
                            break
                    except Exception as ex:
                        self.handle_error(ex.__repr__(), 60)
                        break

                    time.sleep(5)

    def collect_host_info(self, client: SSHClient):
        _, stdout, stderr = client.exec_command(
            'cd ' + self.device.ssh_conf.monitoring_path +
            ' && ./venv/bin/flask host'
        )

        stderr_message = stderr.read()
        if stderr_message:
            self.handle_error(stderr_message)
            return False

        data = json.loads(stdout.read())

        self.host_info.update_info(
            hostname=data['hostname'],
            model=data['model'],
            os_name=data['os_name'],
            system=data['system'],
            machine=data['machine'],
            processor=data['processor'],
            platform=data['platform'],
            up_since=datetime.datetime.fromtimestamp(
                data['up_since'],
                tz=datetime.timezone.utc
            ),
            max_cpu_frequence=data['max_cpu_frequency'],
            total_ram=data['total_ram'],
            number_of_cpus=data['number_of_cpus'],
        )

        return True

    def collect_usage(self, client: SSHClient):
        _, stdout, stderr = client.exec_command(
            'cd ' + self.device.ssh_conf.monitoring_path +
            ' && ./venv/bin/flask usage'
        )

        stderr_message = stderr.read()
        if stderr_message:
            self.handle_error(stderr_message)
            return False

        data = json.loads(stdout.read())

        self.host_info.update_usage(
            cpu_usage=data['cpu_usage'],
            cpu_frequency=data['cpu_frequency'],
            cpu_temperature=data['cpu_temperature'],
            disk_space_available=data['disk_space_available'],
            disk_space_used=data['disk_space_used'],
            used_ram=data['ram'],
            current_date=datetime.datetime.fromtimestamp(
                int(data['current_date']),
                tz=datetime.timezone.utc
            ),
        )

        return True

    def get_ssh_conf(self):
        rendered: str = self.ssh_conf_template.render(
            Context({
                'hostname': self.device.ssh_conf.hostname,
                'username': self.device.ssh_conf.username,
                'port': self.device.ssh_conf.port,
                'identity_file': self.device.ssh_conf.ssh_key.identity_file,
            })
        )

        return SSHConfig.\
            from_text(rendered).\
            lookup(self.device.ssh_conf.hostname)

    def handle_error(self, message, sleep_interval=None):
        self.device.message = message
        self.device.status = 'disconnected'
        self.device.save()

        if sleep_interval is not None:
            time.sleep(sleep_interval)

    def run(self):
        thread = threading.Thread(target=self.collect, daemon=True)
        thread.start()
