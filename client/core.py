from collections import namedtuple
import urlparse
import requests
import re
from requests.exceptions import ConnectionError

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


class ServerClient(object):
    # TODO: turn this into something smarter

    device_list_url = '/device/'
    device_detail = '/device/{}/'
    device_operations = '/device/{}/operations/'

    def __init__(self, domain, token=None):
        # TODO: add token support
        self.token = token
        self.domain = domain

    def _make_url(self, path):
        return urlparse.urljoin(self.domain, path)

    def get_devices(self, pattern=None):
        '''
        :pattern: a regex string onto which the id of the device is matched
        '''
        try:
            response = requests.get(self._make_url(self.device_list_url))
        except ConnectionError:
            raise ValueError('Cannot connect to given server')

        raise_if(
            response.status_code != 200,
            'Failed to get devices with code: {}'.format(response.status_code))

        devices = response.json()

        if pattern:
            devices = filter(
                lambda x: re.match(pattern, x['device_id']), devices)

        return devices

    def get_device(self, id):
        devices = self.get_devices()
        target_device = filter(lambda x: x['device_id'] == id, devices)

        raise_if(len(target_device) == 0, 'No device with id'.format(id))
        raise_if(len(target_device) > 1, 'Multiple devices with given id')

        return target_device[0]

    def get_device_operations(self, device_id):
        device = self.get_device(device_id)
        try:
            response = requests.get(
                self._make_url(self.device_operations.format(device['id'])))
        except ConnectionError:
            raise ValueError('Cannot connect to given server')

        raise_if(
            response.status_code != 200,
            'Failed to get operations with code: {}'.format(
                response.status_code)
        )

        return response.json()
