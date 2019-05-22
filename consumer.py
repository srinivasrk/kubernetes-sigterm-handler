from builtins import Exception

import signal
import pika
import sys
from contextlib import contextmanager

received_signal = False
processing_callback = False


def signal_handler(signal, frame):
    global received_signal
    print("signal received")
    received_signal = True
    if not processing_callback:
         sys.exit()


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

@contextmanager
def block_signals():
    global processing_callback
    processing_callback = True
    try:
        yield
    finally:
        processing_callback = False
        if received_signal:
            sys.exit()


def callback(ch, method, properties, body):
    with block_signals:
        print(body)
        sum(range(0, 100000000)) # sleep gets interrupted by signals, this doesn't.
        ch.basic_ack(delivery_tag=method.delivery_tag)
        print("Message consumption complete")


if __name__ == "__main__":
    try:
        _credentials = pika.PlainCredentials('guest',
                                             'guest')

        _connection = pika.BlockingConnection(pika.ConnectionParameters(
            'rabbitmq-service',
            5672,
            '/',
            _credentials, heartbeat=0, socket_timeout=360))
        channel = _connection.channel()
        print(' [*] Waiting for messages. To exit press CTRL+C')
        channel.basic_consume(callback, queue='test')
        channel.start_consuming()
    except Exception as e:
        channel.close()
        sys.exit()