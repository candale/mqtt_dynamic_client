from collections import namedtuple

from utils import raise_if, make_topic
from constants import ArgType


# These classes define the contract for an operation
OpType = namedtuple('OpType', ['type', 'interval'])
OpArg = namedtuple('OpArg', ['type', 'name'])
Op = namedtuple('Op', ['topic', 'type', 'name', 'description', 'args'])


class BaseClient(object):

    def __init__(self, model, mqtt_client):
        '''
        :model: an object that has an iterable `operations` with objects of
                type Op
        '''
        # TODO: think again about this model thingy; maybe simply a dict?
        self.model = model
        self.mqtt_client = mqtt_client

    def validate_args(self, op, args):
        '''
        Right now the arguments can only be strings or integers
        '''
        # TODO: make this more extensible, with validators and stuff ???
        for arg_template, arg in zip(op.args, args):
            if arg_template.type == ArgType.STR:
                raise_if(
                    type(arg) not in [str, unicode],
                    'Invalid parameter sent, should be str/unicode ({})'.format(
                        arg_template.name),
                    TypeError
                )
            elif arg_template.type == ArgType.INT:
                raise_if(
                    type(arg) not in [int, long],
                    'Invalid parameter send, should be int/long ({})'.format(
                        arg_template.name),
                    TypeError
                )

    def _make_publish(self, op_name, payload, *args, **kwargs):
        '''
        checks in self model for op_name and issues appropriate publish
        '''
        op = self.get_op(op_name)
        raise_if(
            len(args) != len(op.args),
            'Operation takes exactly {} arguments; {} given'.format(
                len(args), len(op.args)))
        self.validate_args(op, args)

        publish_topic = make_topic(op.topic, *args)
        self.mqtt_client.publish(publish_topic, payload)

    def get_op(self, op_name):
        ops = filter(lambda x: x.name == op_name, self.model.operations)

        raise_if(len(ops) == 0, 'No operation with name {}'.format(op_name))
        raise_if(len(ops) > 1, 'Multiple operations for name {}'.format(op_name))

        return ops[0]


def _get_mqtt_publish(op_name):
    # TODO: it's awkward to have the payload first; args should be first
    def publish(self, payload, *args):
        return self._make_publish(op_name, payload, *args)

    return publish


def make_device_client(model, cls_name, mqtt_client):
    # TODO: maybe add inheritance support. not needed for now
    cls_props = {}
    for op in model.operations:
        method = _get_mqtt_publish(op.name)
        method.__name__ = (
            str(op.name.decode('utf-8'))
            if isinstance(op.name, unicode) else op.name)
        method.__doc__ = op.description
        cls_props[op.name] = method

    cls = type(cls_name, (BaseClient, ), cls_props)
    return cls(model, mqtt_client)
