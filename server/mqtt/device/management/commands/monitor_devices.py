import datetime
import sys

from django.core.management.base import BaseCommand
from django.conf import settings

import paho.mqtt.client as mqtt

from device.models import Device, Operation
from device.utils import get_id_from_spec_topic


def on_message(client, userdata, msg):
    device_id = get_id_from_spec_topic(msg.topic)
    device, created = Device.objects.get_or_create(
        device_id=device_id,
        defaults={
            'last_online': datetime.datetime.now(),
            'online': True
        }
    )

    if created:
        sys.stdout.write('Added device with id: {}\n'.format(device_id))

    # TODO: this sucks. improve how spec is update so no operation is left
    #       hanging.
    # TODO: change online state of device somehow
    if device.operations.filter(spec=msg.payload).exists() is False:
        Operation.objects.create(spec=msg.payload, device=device)
        sys.stdout.write(
            'Create new operation with spec: {}\n'.format(msg.payload))


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
