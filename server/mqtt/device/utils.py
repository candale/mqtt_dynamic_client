import uuid

from django.conf import settings

import paho.mqtt.client as mqtt
from kombu import Connection

from device import ampq


def get_id_from_spec_topic(topic):
    matches, args = match_topic(settings.MQTT_DEVICE_SPEC_TOPIC, topic)
    raise_if(
        len(args) != 1,
        'Spec should have a single parameter which is the device id')

    return args[0]


def raise_if(cond, msg=None, exception=ValueError):
    if bool(cond):
        params = [msg] if msg else []
        raise ValueError(*params)


def match_topic(raw_topic, to_match):
    '''
    Matches a topic to a raw topic
    Returns a a boolean that indicates if the topics match and a list
    with all the arguments that were send (instead of +)
    '''
    if '+' not in raw_topic:
        return raw_topic == to_match

    raw_topic_split = raw_topic.split('/')
    to_match_split = to_match.split('/')

    if len(raw_topic_split) != len(to_match_split):
        return False, []

    args = []
    for raw, match in zip(raw_topic_split, to_match_split):
        if raw == '+':
            args.append(match)
        elif raw != match:
            return False, []

    return True, args


def build_topic(raw_topic, args):
    raise_if(
        raw_topic.count('+') != len(args),
        'Different number of args than topic has')

    if '+' not in raw_topic:
        return raw_topic

    return raw_topic.replace('+', '{}').format(*args)


def get_ack_token(client_id, mid):
    return '{}-{}'.format(client_id, mid)


def send_message_from_api(topic, args, payload,
                          wait_for_published=True, wait_for_received=False):
    def on_publish(client, userdata, mid):
        ampq.published(
            client._client_id, get_ack_token(client._client_id, mid))

    mqtt_client = mqtt.Client(str(uuid.uuid4())[:16])
    mqtt_client.connect(
        settings.MQTT_SERVER, settings.MQTT_PORT, settings.MQTT_KEEPALIVE)

    result, mid = mqtt_client.publish(build_topic(topic, args), payload)

    if not result:
        return False

    result = ampq.wait_for_published(
        mqtt_client._client_id, get_ack_token(mqtt_client._client_id, mid))

    mqtt_client.disconnect()

    return result
