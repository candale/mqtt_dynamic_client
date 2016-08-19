def get_id_from_spec_topic(topic):
    return topic.split('/')[1]


def raise_if(cond, msg=None, exception=ValueError):
    if bool(cond):
        params = [msg] if msg else []
        raise ValueError(*params)
