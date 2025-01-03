import logging
from queue import Queue, Full, Empty
from threading import Thread

from lada import LOG_LEVEL

logger = logging.getLogger(__name__)
logging.basicConfig(level=LOG_LEVEL)

def put_closing_queue_marker(queue: Queue, debug_queue_name: str):
    sent_out_none_success = False
    while not sent_out_none_success:
        try:
            queue.put(None, block=False)
            sent_out_none_success = True
        except Full:
            queue.get(block=False)
            queue.task_done()
    logger.debug(f"sent out None to queue {debug_queue_name} to indicate we're stopping")


def empty_out_queue(queue: Queue, debug_queue_name: str):
    while not queue.empty():
        queue.get()
        queue.task_done()
    logger.debug(f"purged all remaining elements from queue {debug_queue_name}")

def empty_out_queue_until_producer_is_done(queue: Queue, debug_queue_name: str, producer_thread: Thread):
    """
    Use it only if producer we're waiting for can produce an unknown number of items before it stops and could therefore
    potentially block on put() if queue size is limited.
    """
    def consumer():
        while (producer_thread and producer_thread.is_alive()) or not queue.empty():
            try:
                queue.get(timeout=0.02)
                queue.task_done()
            except Empty:
                pass
        logger.debug(f"purged all remaining elements from queue {debug_queue_name}")
    consumer_thread = Thread(target=consumer)
    consumer_thread.start()
    return consumer_thread
