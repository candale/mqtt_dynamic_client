import uuid
import time

from django.conf import settings

import paho.mqtt.client as mqtt

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


def send_message_from_api(topic, args, payload, timeout=0.7,
                          wait_for_received=True):
    '''
    Not the best implementation of this buut...it will do for now, I guess

    This has to be modified to be making use of QoS or some unique  identifier
    Concurrent messages to the same device may receive ack from one another.
    '''
    was_published = []
    was_recv = []

    def on_publish(client, userdata, mid):
        was_published.append(True)

    def on_msg(client, userdata, msg):
        if msg.payload == '+':
            was_recv.append(True)

    def ack_done():
        return (
            was_published and
            was_recv or not wait_for_received
        )

    mqtt_client = mqtt.Client(str(uuid.uuid4())[:16])
    mqtt_client.on_publish = on_publish
    mqtt_client.on_message = on_msg
    mqtt_client.connect(
        settings.MQTT_SERVER, settings.MQTT_PORT, settings.MQTT_KEEPALIVE)
    mqtt_client.subscribe(settings.MQTT_DEVICE_ACK_TOPIC)

    result, mid = mqtt_client.publish(build_topic(topic, args), payload)

    if result:
        return False

    counter = 0
    while not ack_done() and counter < timeout:
        mqtt_client.loop(timeout=0.07)
        counter += 0.07

    mqtt_client.disconnect()

    return (
        (was_published and was_published[0]) and
        (was_recv or not wait_for_received))
