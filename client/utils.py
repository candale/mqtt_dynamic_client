def raise_if(cond, msg=None, exception=ValueError):
    if bool(cond):
        params = [msg] if msg else []
        raise ValueError(*params)


def make_topic(topic, *args):
    if '+' not in topic:
        return topic

    format_topic = topic.replace('+', '{}')
    return format_topic.format(*args)
