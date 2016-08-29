import datetime
import sys

from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils.module_loading import import_string

import paho.mqtt.client as mqtt

from device.models import Device, Operation, Arg
from device.utils import match_topic, raise_if


def online(msg, device_id):
    # TODO: change so that if a device is already seen as online,
    #       we should somehow treat that
    #       this may happen when the keepalive time of a device is long enough
    #       such that it is unresponsive but the broker has not yet figured
    #       that out because the keepalive has not expired yet
    device, created = Device.objects.update_or_create(
        device_id=device_id, defaults={'online': True}
    )

    if created:
        sys.stdout.write('Added device with id: {}\n'.format(device_id))
    else:
        if device.last_offline:
            device.operations.filter(
                created_at__lt=device.last_offline).delete()

    parser = import_string(settings.SPEC_PARSER)
    validated_data = parser(msg.payload)
    validated_data['device_id'] = device.id
    args = validated_data.pop('args')

    operation = Operation.objects.create(**validated_data)
    sys.stdout.write(
        'Create operation {} for device {}\n'.format(
            operation.name, device.device_id))
    for arg in args:
        arg['operation'] = operation
        Arg.objects.create(**arg)


def offline(msg, device_id):
    try:
        device = Device.objects.get(device_id=device_id)
    except Device.DoesNotExist:
        pass

    device.online = False
    device.last_offline = datetime.datetime.now()
    device.save()

    sys.stdout.write('Device {} is offline\n'.format('device_id'))


def on_message(client, userdata, msg):
    is_connect, connect_args = match_topic(
        settings.MQTT_DEVICE_SPEC_TOPIC, msg.topic)
    is_disconnect, disconnect_args = match_topic(
        settings.MQTT_DEVICE_OFFLINE, msg.topic)

    if is_connect:
        online(msg, connect_args[0])
    elif is_disconnect:
        offline(msg, disconnect_args[0])


def on_connect(client, userdata, flags, rc):
    sys.stdout.write('Connected to broker\n')
    sys.stdout.write('Waiting for incoming messages ...\n')

    raise_if(
        settings.MQTT_DEVICE_SPEC_TOPIC.count('+') != 1,
        'Spec topic should have a single parameter, device id (one +)')
    raise_if(
        settings.MQTT_DEVICE_OFFLINE.count('+') != 1,
        'Offline topic should have a single parameter, device id (one +)')

    client.subscribe(settings.MQTT_DEVICE_SPEC_TOPIC)
    client.subscribe(settings.MQTT_DEVICE_OFFLINE)


class Command(BaseCommand):

    help = 'Monitor all the devices on a broker'

    def handle(self, *args, **options):
        client = mqtt.Client(settings.MQTT_MONITOR_ID)
        client.on_message = on_message
        client.on_connect = on_connect
        client.connect(
            settings.MQTT_SERVER, settings.MQTT_PORT, settings.MQTT_KEEPALIVE)

        try:
            client.loop_forever()
        except KeyboardInterrupt:
            self.stdout.write('\nTrying to disconnect ... ')
            try:
                client.disconnect()
            except Exception, e:
                self.stdout.write(
                    self.style.ERROR('Fail with message {}'.format(e)))
            else:
                self.stdout.write(self.style.SUCCESS('OK'))
