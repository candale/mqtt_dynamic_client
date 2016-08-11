from core import DeviceModel
from parsers import simple_validator


class MockModel(DeviceModel):

    parse_callable = simple_validator

    def get_specs(self):
        return [
            'my/topic|call|no_argument_handler|test handler|',
            'my/+/topic|call|one_argument_handler|test handler|string:topic_kind',
            (
                'my/+/+/topic|call|two_argument_handler|test handler|'
                'string:topic_kind,string:topic_kind_level'
            ),
        ]
