from collections import namedtuple

from constants import OpType as ConstOpType


OpType = namedtuple('OpType', ['type', 'interval'])
OpArg = namedtuple('OpArg', ['type', 'name'])
Op = namedtuple('Op', ['topic', 'type', 'name', 'description', 'args', '_raw'])


class DeviceModel:
    '''
    Parses a spec string of the form
        <op_topic>|<op_type[,<interval>]>|<op_name>|<op_description>|<arg_type:arg_name, ...>

    :op_topic: the topic on which the operation can be called/data can be retrieved
    :op_type: the nature of the operation (call/recv). for recv, the interval
        is specified immediately after (separated by comma). the interval must
        be specified in milliseconds
    :op_name: operation name
    :op_description: the description of the operations (docstring)
    :args: the arguments that the operation taskes as a list of type-name pairs

    '''

    parse_callable = None

    def __init__(self):
        '''
        :specs: a list of operations spec
        '''
        self._operations = []
        for spec in self.get_specs():
            self.operations.append(self.parse_callable(spec))

    def get_specs(self):
        '''
        Returns an iterable that contains (as strings) the specs.
        This method is to be overridden to get specs from whatever sources.
        '''


class BaseClient:

    def __init__(self, model, mqtt_client):
        self.model = model
        self.mqtt_client = mqtt_client

    def _make_publish(self, op_name, payload, *args, **kwargs):
        '''
        checks in self model for op_name and issues appropriate publish
        '''
        op = self.get_op(op_name)

        assert len(args) == len(op.args), (
            'Operation takes exactly {} arguments; {} given'.format(
                len(args), len(op_args))


    def get_op(self, op_name):
        ops = filter(lambda x: x.name == op_name, self.model)

        if not ops:
            raise ValueError('No operation with name {}'.format(op_name))

        if len(ops) > 1:
            raise ValueError('Multiple operations for name {}'.format(op_name))

        return ops[0]


def _get_mqtt_publish(op_name):
    def publish(self, payload, *args):
        return self._make_publish(op_name, payload, *args)

    return publish


def make_client(model, cls_name, mqtt_client):
    # TODO: maybe add inheritance support. not needed for now
    cls_props = {}
    for op in model.operations:
        method = _get_mqtt_publish(op.name)
        method.__name__ = op.name
        method.__doc__ = op.description
        cls_props[op.name] = method

    cls = type(cls_name, (BaseClient, ), cls_props)
    return cls(model, mqtt_client)
