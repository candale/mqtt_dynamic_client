from core import DeviceModel, ServerClient
from parsers import simple_parser


class MockModel(DeviceModel):
    '''
    Testing, in development, model
    '''

    parse_callable = simple_parser

    def get_specs(self):
        return [
            'call|no_argument_handler|test handler|',
            'call|one_argument_handler|test handler|str:topic_kind',
            (
                'call|two_argument_handler|test handler|'
                'str:topic_kind,str:topic_kind_level'
            ),
        ]


class ServerAPIModel(DeviceModel):

    parse_callable = simple_parser

    def __init__(self, domain, device_id):
        self.device_id = device_id
        self._server_client = ServerClient(domain)
        super(ServerAPIModel, self).__init__()

    def get_specs(self):
        return [
            op['spec']
            for op in self._server_client.get_device_operations(self.device_id)
        ]
