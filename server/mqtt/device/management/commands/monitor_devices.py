import datetime
import importlib
import sys

from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils.module_loading import import_string

import paho.mqtt.client as mqtt

from device.models import Device, Operation, Arg
from device.utils import get_id_from_spec_topic


def on_message(client, userdata, msg):
    device_id = get_id_from_spec_topic(msg.topic)
    device, created = Device.objects.create_or_update(
        device_id=device_id, defaults={'online': True}
    )

    if created:
        sys.stdout.write('Added device with id: {}\n'.format(device_id))
    else:
        device.operations.filter(
            created_at__lt=device.last_offline).delete()

    # TODO: change online state of device somehow
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


def on_connect(client, userdata, flags, rc):
    sys.stdout.write('Connected to broker\n')
    sys.stdout.write('Waiting for incoming messages ...\n')
    client.subscribe(settings.MQTT_DEVICE_SPEC_TOPIC)


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
