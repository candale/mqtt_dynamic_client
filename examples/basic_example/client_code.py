from paho.mqtt.client import Client as MQTTClient

from client.models import ServerAPIModel
from client.core import make_device_client


# Init mqtt client
mqtt_client = MQTTClient('paho_lol')
mqtt_client.connect('212.47.229.77', 1883, 6000)

# Create the model
model = ServerAPIModel('http://localhost:8000', 'test')

# Create the client
cl = make_device_client(model, 'my_client', mqtt_client)

# Call methods
cl.no_argument_handler('payload')
cl.one_argument_handler('payload', 'first_arg')
cl.two_argument_handler('payload', 'first_arg', 'second_arg')
