from core import ServerClient, OpType, OpArg, Op
from parsers import simple_parser


class ServerAPIModel(object):

    parse_callable = simple_parser

    def __init__(self, domain, device_id):
        self.device_id = device_id
        self._server_client = ServerClient(domain)
        self.operations = self.get_specs()

    def get_specs(self):
        ops = []
        for op in self._server_client.get_device_operations(self.device_id):
            args = [OpArg(**arg) for arg in op.pop('args')]
            op_type = OpType(type=op.pop('type'), interval=op.pop('interval'))
            op['type'] = op_type
            op['args'] = args
            op_obj = Op(**op)
            ops.append(op_obj)

        return ops
