import json


import psutil


from core.models import NetworkInterfaceModel


class NetworkInterfaceRegistry:
    @classmethod
    def get_duplex_name(cls, value):
        if value == psutil.NIC_DUPLEX_FULL:
            return 'full'
        elif value == psutil.NIC_DUPLEX_HALF:
            return 'half'
        else:
            return 'unknown'

    @classmethod
    def get_network_interfaces(cls, host_id):
        result = list()

        for interface in NetworkInterfaceModel.objects.\
                filter(host_id=host_id).\
                order_by('pk'):
            result.append({
                'name': interface.name,
                'ip4_address': interface.ip4_address,
                'ip6_address': interface.ip6_address,
                'isup': interface.isup,
                'duplex': interface.duplex,
                'speed': interface.speed,
                'mtu': interface.mtu,
                'addresses': interface.addresses
            })

        return result

    @classmethod
    def store(cls, host_id, net_interfaces):
        removed_interfaces = {
            face['name']: face
            for face in cls.get_network_interfaces(host_id)
        }

        for interface in net_interfaces:
            interface['duplex'] = cls.get_duplex_name(interface['duplex'])

            if interface['name'] in removed_interfaces:
                old_face = removed_interfaces[interface['name']]

                if interface['isup'] != old_face['isup'] or \
                        interface['duplex'] != old_face['duplex'] or \
                        interface['speed'] != old_face['speed'] or \
                        interface['mtu'] != old_face['mtu'] or \
                        interface['ip4_address'] != old_face['ip4_address'] \
                        or interface['ip6_address'] != \
                        old_face['ip6_address'] \
                        or json.dumps(interface['addresses']) != \
                        json.dumps(old_face['addresses']):

                    NetworkInterfaceModel.objects.filter(
                        host_id=host_id,
                        name=interface['name']
                    ).update(
                        isup=interface['isup'],
                        duplex=interface['duplex'],
                        speed=interface['speed'],
                        mtu=interface['mtu'],
                        ip4_address=interface['ip4_address'],
                        ip6_address=interface['ip6_address'],
                        addresses=interface['addresses']
                    )

                del removed_interfaces[interface['name']]
            else:
                NetworkInterfaceModel.objects.create(
                    host_id=host_id,
                    name=interface['name'],
                    isup=interface['isup'],
                    duplex=interface['duplex'],
                    speed=interface['speed'],
                    mtu=interface['mtu'],
                    ip4_address=interface['ip4_address'],
                    ip6_address=interface['ip6_address'],
                    addresses=interface['addresses'],
                )

        if removed_interfaces:
            NetworkInterfaceModel.objects.filter(
                host_id=host_id,
                name__in=list(removed_interfaces.keys())
            ).delete()
