import requests

from core import OpType, OpArg, Op
from parsers import bar_separated_spec


class ServerAPIModel(object):

    parse_callable = bar_separated_spec

    def __init__(self, domain, device_id):
        self.device_id = device_id
        self.domain = domain
        self.operations = self.get_specs()

    def get_specs(self):
        ops = []
        json_operations = requests.get(
            self.domain + '/device/{}/operations'.format(self.device_id)).json()
        for op in json_operations:
            args = [OpArg(**arg) for arg in op.pop('args')]
            op_type = OpType(type=op.pop('type'), interval=op.pop('interval'))
            op['type'] = op_type
            op['args'] = args
            op_obj = Op(**op)
            ops.append(op_obj)

        return ops
