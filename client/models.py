from core import DeviceModel
from parsers import simple_parser


class MockModel(DeviceModel):
    '''
    Testing, in development, model
    '''

    parse_callable = simple_parser

    def get_specs(self):
        return [
            'my/topic|call|no_argument_handler|test handler|',
            'my/+/topic|call|one_argument_handler|test handler|str:topic_kind',
            (
                'my/+/+/topic|call|two_argument_handler|test handler|'
                'str:topic_kind,str:topic_kind_level'
            ),
        ]
