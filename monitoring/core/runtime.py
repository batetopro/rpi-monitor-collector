import json


import redis


from django.conf import settings


class RuntimeRegistry:
    @classmethod
    def get_redis(cls):
        return redis.Redis(
            host=settings.REDIS['host'],
            port=int(settings.REDIS['port']),
            username=settings.REDIS['username'],
            password=settings.REDIS['password'],
            db=int(settings.REDIS['db']),
            decode_responses=True
        )

    @classmethod
    def clean_host_runtime(cls, host_id):
        try:
            conn = cls.get_redis()
            conn.delete(f'host-runtime:{host_id}')
        finally:
            conn.close()

    @classmethod
    def get_host_runtime(cls, host_id):
        try:
            conn = cls.get_redis()

            runtime = conn.hgetall(f'host-runtime:{host_id}')

            if not runtime:
                return dict()

            return runtime
        finally:
            conn.close()

    @classmethod
    def store_host_runtime(
            cls, host_id, cpu_usage, cpu_frequency, cpu_temperature,
            time_on_host, disk_io_read_bytes, disk_io_write_bytes,
            disk_space_available, disk_space_used, disk_space_total,
            disk_partitions,
            net_io_bytes_recv, net_io_bytes_sent, net_io_counters, used_ram,
            used_swap, total_swap, timestamp):

        runtime = {
            'cpu_usage': cpu_usage,
            'cpu_frequency': cpu_frequency,
            'cpu_temperature': cpu_temperature,
            'time_on_host': time_on_host.timestamp(),
            'disk_io_read_bytes': disk_io_read_bytes,
            'disk_io_write_bytes': disk_io_write_bytes,
            'disk_space_available': disk_space_available,
            'disk_space_used': disk_space_used,
            'disk_space_total': disk_space_total,
            'disk_partitions': json.dumps(disk_partitions),
            'net_io_bytes_recv': net_io_bytes_recv,
            'net_io_bytes_sent': net_io_bytes_sent,
            'net_io_counters':  json.dumps(net_io_counters),
            'used_ram': used_ram,
            'used_swap': used_swap,
            'total_swap': total_swap,
            'timestamp': timestamp.timestamp()
        }

        try:
            conn = cls.get_redis()
            conn.hset(f'host-runtime:{host_id}', mapping=runtime)
        finally:
            conn.close()
