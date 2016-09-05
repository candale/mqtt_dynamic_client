from django.conf import settings


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
