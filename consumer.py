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
    print("signal received")
    received_signal = True
    if not processing_callback:
         sys.exit()


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def callback(ch, method, properties, body):
    logger.info("Message received")
    logger.info(body)
    global processing_callback
    processing_callback = True
    try:
        logger.info(body)
        sum(range(0, 10000)) # sleep gets interrupted by signals, this doesn't.
        ch.basic_ack(delivery_tag=method.delivery_tag)
        logger.info("Message consumption complete")
    except Exception as e:
        print(e)
    finally:
        processing_callback = False
        if received_signal:
            sys.exit()


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
        logger.info(' [*] Waiting for messages. To exit press CTRL+C')
        channel.queue_declare(queue='test', durable=True)
        channel.basic_consume(queue='test', on_message_callback=callback)
        channel.start_consuming()
    except Exception as e:
        channel.close()
        sys.exit()
