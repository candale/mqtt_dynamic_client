class OpType:
    CALL = 'call'
    RECV = 'recv'

    CHOICES = (
        (CALL, 'Callable'),
        (RECV, 'Data source')
    )


class ArgType:
    INT = 'int'
    STR = 'str'
    BOOL = 'bool'

    CHOICES = (
        (INT, 'Integer'),
        (STR, 'String'),
        (BOOL, 'Boolean')
    )
