from device.constants import OpType
from device.utils import raise_if


def simple_parser(spec):
    split_spec = spec.split('|')
    raise_if(len(split_spec) != 5, 'Missing fields from spec')

    # Parse topic
    validated_data = {}

    raise_if(split_spec[0] in [None, ''], 'Operation topic is mandatory')
    validated_data['topic'] = split_spec[0]

    # Parse operation type
    raise_if(split_spec[1] in [None, ''], 'Operation type is mandatory')
    op_type_str = split_spec[1]
    raise_if(
        not (OpType.CALL in op_type_str or OpType.RECV in op_type_str),
        'Operation type must be one of {} or {}'.format(
            OpType.CALL, OpType.RECV)
    )

    if OpType.RECV in op_type_str:
        raise_if(
            ',' not in op_type_str,
            'For operation type {}, interval is mandatory'.format(OpType.RECV))
        op_type, interval = op_type_str.split(',')
        interval = int(
            raise_if(
                interval in [None, ''],
                'Interval is mandatory for operations of type {}'.format(
                    OpType.RECV)
            )
        )

        validated_data['type'] = op_type
        validated_data['interval'] = interval
    else:
        validated_data['type'] = op_type_str

    # Parse operation name
    raise_if(split_spec[2] in [None, ''], 'Operation name is mandatory')
    validated_data['name'] = split_spec[2]

    # Parse description
    validated_data['description'] = split_spec[3]

    # Parse arguments
    args_str = split_spec[4]
    args = []
    if args_str:
        for arg_spec in args_str.split(','):
            # TODO: improve exception messages
            arg_type, arg_name = arg_spec.split(':')
            raise_if(arg_type in [None, ''], 'Invalid arg type')
            raise_if(arg_name in [None, ''], 'Invalid arg name')
            args.append({'type': arg_type, 'name': arg_name,})

    validated_data['args'] = args

    return validated_data
