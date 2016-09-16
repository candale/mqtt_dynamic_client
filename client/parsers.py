from core import Op, OpArg
from utils import raise_if
from constants import OpType


def bar_separated_spec(self, spec):
    '''
    Parses a string of the format
        <topic>|<op_type(recv|call)>|<function_name>|<description>|<arg_type:arg_name>,...
    '''
    def get_or_raise_if_empty(obj, msg=None):
        if obj is None or obj == '':
            raise ValueError(msg or 'One of more spec details were empty')
        return obj

    split_spec = spec.split('|')
    raise_if(len(split_spec) != 5, 'Missing fields from spec')

    # Parse topic
    validated_data = {}
    validated_data['topic'] = get_or_raise_if_empty(
        split_spec[0], 'Operation topic is mandatory')

    # Parse operation type
    op_type = get_or_raise_if_empty(
        split_spec[1], 'Operation type is mandatory')
    raise_if(
        op_type not in [OpType.CALL, OpType.RECV],
        'Operation type must be one of {} or {}'.format(
            OpType.CALL, OpType.RECV)
    )

    validated_data['type'] = op_type

    # Parse operation name
    validated_data['name'] = get_or_raise_if_empty(
        split_spec[2], 'Operation name is mandatory')

    # Parse description
    validated_data['description'] = split_spec[3]

    # Parse arguments
    args_str = split_spec[4]
    args = []
    if args_str:
        for arg_spec in args_str.split(','):
            # TODO: improve exception messages
            arg_type, arg_name = arg_spec.split(':')
            args.append(OpArg(
                type=get_or_raise_if_empty(arg_type, 'Invalid arg type'),
                name=get_or_raise_if_empty(arg_name, 'Invalid arg name')))

    validated_data['args'] = args
    validated_data['raw'] = spec

    return Op(**validated_data)
