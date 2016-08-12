from paho.mqtt.client import Client

from client.models import MockModel
from client.core import make_client


mqtt_client = Client('paho_lol')
mqtt_client.connect('212.47.229.77', 1883, 6000)

model = MockModel()

cl = make_client(model, 'my_client', mqtt_client)

cl.no_argument_handler('payload')
cl.one_argument_handler('payload', 'first_arg')
cl.two_argument_handler('payload', 'forst_arg', 'second_arg')
