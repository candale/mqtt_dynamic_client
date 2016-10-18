from django.conf import settings

from kombu import Connection


def published(queue, data):
    with Connection(settings.MQTT_ACK_AMQP_CONNECTION_URL) as conn:
        q = conn.SimpleQueue(queue)
        q.put(data)
        q.close()


def wait_for_published(queue, wait_for, timeout=2):
    with Connection(settings.MQTT_ACK_AMQP_CONNECTION_URL) as conn:
        q = conn.SimpleQueue(queue)
        try:
            response = q.get(block=True, timeout=timeout)
        except q.Empty:
            return False
        else:
            response.ack()
            if response.payload == wait_for:
                return True
            return False
