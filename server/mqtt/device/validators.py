def is_integer(value):
    return isinstance(value, (int, long))


def is_string(value):
    return isinstance(value, (str, unicode))


def is_boolean(value):
    return isinstance(value, bool)
