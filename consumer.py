from builtins import Exception

import signal
import pika
import sys
from contextlib import contextmanager
import logging


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger()
logger.info("Created logger")

received_signal = False
processing_callback = False

def signal_handler(signal, frame):
    global received_signal
    global channel
    global connection
    logger.info("signal received")
    received_signal = True
    if not processing_callback and channel is not None and connection is not None:
         channel.cancel()


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def callback(ch, method, properties, body):
    logger.info("Message received")
    logger.info(body)
    global processing_callback
    global channel
    global connection

    processing_callback = True
    try:
        sum(range(0, 10000)) # sleep gets interrupted by signals, this doesn't.
        ch.basic_ack(delivery_tag=method.delivery_tag)
        logger.info("Message consumption complete")
    except Exception as e:
        print(e)
    finally:
        processing_callback = False
        if received_signal:
            channel.cancel()


def closeConnection(method_frame):
    global connection
    global channel
    channel.close()
    connection.close()

if __name__ == "__main__":
    global channel
    global connection

    try:
        _credentials = pika.PlainCredentials('guest',
                                             'guest')

        _connection = pika.BlockingConnection(pika.ConnectionParameters(
            'rabbitmq-service',
            5672,
            '/',
            _credentials, heartbeat=0, socket_timeout=360))
        connection = _connection
        channel = _connection.channel()
        channel.add_on_cancel_callback(closeConnection)
        logger.info(' [*] Waiting for messages. To exit press CTRL+C')
        channel.queue_declare(queue='test', durable=True)
        channel.basic_consume(queue='test', on_message_callback=callback)
        channel.start_consuming()
    except Exception as e:
        logger.info(e)
        channel.cancel()
