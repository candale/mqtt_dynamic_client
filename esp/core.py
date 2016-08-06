import ure

from ucollections import namedtuple
from umqtt.simple import MQTTClient


class MessageHandlerBase:

    def __init__(self, client):
        self._client = client

    def process_message(self, *args, msg=None):
        '''
        This method is called when a message is received on a topic that this
        handler is in charge of
        '''

    def get_spec(self):
        '''
        Gets the specification of this handler, a string of the from
        <func_type (callable, data_source)>|<function_name>|<description>|<arg_type: arg_name, ...>
        '''


class MQTTRouter:

    wildcard_regex_plus = '([^/]+)'
    _RegexTopic = namedtuple('RegexTopic', ['ure_obj', 'group_count'])

    def __init__(self):
        self._handlers_map = []

    def _resolve_handlers(self, topic):

        def get_args(match, group_count):
            args = [match.group(index) for index in range(1, group_count + 1)]

        handlers = []

        for topic_cmp, handler in self.handlers_map:
            if isinstance(topic_cmp, self._RegexTopic):
                match = topic.ure_obj.match(recv_topic)
                if match:
                    args = get_args(match, topic_cmp.group_count)
                    handlers.append((handler, args))
            elif topic_cmp == topic:
                handlers.append((handler, []))

        return handlers

    def __call__(self, topic, msg):
        '''
        This is the method that receives all messages and sends everything
        to the appropriate registered callbacks
        '''
        handlers = self._resolve_handlers(topic)
        for handler, args in handlers:
            handler.process_message(*args, msg=msg)

    def _get_regex_if_needed(self, topic):
        wildcard_count = topic.count(b'+')
        if wildcard_count:
            return namedtuple(
                ure_obj=ure.compile(
                    topic.replace('+', self.wildcard_regex_plus)),
                group_count=wildcard_count)
        else:
            return topic

    def register_handler(self, topic, handler):
        '''
        Registers a handler
        '''
        self._handlers_map.append((self._get_regex_if_needed(topic), handler))


class MQTTRpc:

    router_class = MQTTRouter
    # An iterable of the form ((<topic, <topic_handler_clas), ...)
    handler_classes = None

    def __init__(self, id, server):
        self._client = MQTTClient(id, server)
        self._router = self.router_class()

    def _init_router(self):
        if self.handler_classes is None:
            raise ValueError('Improperly configured: no handlers')

        self.router = self.router_class()
        for topic, handler_cls in self.handler_classes:
            # TODO: maybe pass a wrapper of the client with limited functions
            #       (e.g. subscribe and send)
            self._router.register_handler(topic, handler_cls(self._client))
            self._client.subscribe(topic)

    def start(self):
        if self.router_class is None:
            raise ValueError('Improperly configured: no router configured')
        self._client.set_callback(self._router)
        self._client.connect()
        self._init_router()

        # TODO: replace this with time
        # NOTWORKING: no message is received
        while True:
            self._client.wait_msg()

    def stop(self):
        self._client.disconnect()
