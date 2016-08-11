from core import Op, OpArg, OpType
from constants import OpType as ConstOpType


def simple_validator(self, spec):
    def get_or_raise_if_empty(obj, msg=None):
        if obj is None or obj == '':
            raise ValueError(msg or 'One of more spec details were empty')
        return obj

    split_spec = self._spec.split('|')
    assert len(split_spec) == 4, 'Missing fields from spec'

    # Parse topic
    validated_data = {}
    validated_data['topic'] = get_or_raise_if_empty(
        split_spec[0], 'Operation topic is mandatory')

    # Parse operation type
    op_type_str = get_or_raise_if_empty(
        split_spec[1], 'Operation type is mandatory')
    assert ConstOpType.CALL in op_type_str or ConstOpType.RECV in op_type_str, (
        'Operation type must be one of {} or {}'
        .format(ConstOpType.CALL, ConstOpType.RECV))

    if ConstOpType.RECV in op_type_str:
        assert ',' in op_type_str, (
            'For operation type {}, interval is mandatory'
            .format(ConstOpType.RECV))
        op_type, interval = op_type_str.split(',')
        interval = int(
            get_or_raise_if_empty(
                interval,
                'Interval is mandatory for operations of type {}'.format(
                    ConstOpType.RECV)
            )
        )

        validated_data['type'] = OpType(
            type=op_type, interval=interval)
    else:
        validated_data['type'] = OpType(
            type=op_type_str, interval=None)

    # Parse operation name
    validated_data['name'] = get_or_raise_if_empty(
        split_spec[2], 'Operation name is mandatory')

    # Parse description
    validated_data['description'] = split_spec[3]

    # Parse arguments
    args_str = split_spec[4]
    if not args_str:
        args = None
    else:
        args = [
            OpArg(
                type=get_or_raise_if_empty(arg_type, 'Invalid arg type'),
                name=get_or_raise_if_empty(name, 'Invalid arg name'))
            for arg_type, name in args_str.split(',')]

    validated_data['args'] = args

    return Op(**validated_data)
