import random
import sys
import time
import traceback
from functools import wraps

from kafka import KafkaConsumer


def backoff(tries=10, sleep=10):
    def backoff_deco(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            last_exception = None
            for i in range(tries):
                try:
                    return f(*args, **kwargs)
                except Exception as exc:
                    last_exception = sys.exc_info()
                    print(f'Try {i} from {tries}, {f.__name__} call is failed:', file=sys.stderr)
                    traceback.print_exception(*last_exception)
                    time.sleep(sleep)
            print(f'{f.__name__} failed {tries} times')
            raise last_exception[1]

        return wrapper

    return backoff_deco


@backoff(tries=3, sleep=2)
def message_handler(message):
    result = random.randint(1, 10)
    if result > 5:
        raise Exception("message_handler failed")
    print(message)


def create_consumer():
    print("Connecting to Kafka brokers")
    consumer = KafkaConsumer("itmo2023_processed",
                             group_id="itmo_group",
                             bootstrap_servers='localhost:29092',
                             auto_offset_reset='earliest',
                             enable_auto_commit=True)

    for message in consumer:
        message_handler(message)


if __name__ == '__main__':
    create_consumer()
