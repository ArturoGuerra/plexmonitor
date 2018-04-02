import time

from utils import get_logger

logger = get_logger(__name__)

class Scheduler():
    def __init__(self):
        self.time = time.time()
        self.events = list()
    def add(self, event):
        self.events.append(event)

    def run(self):
        logger.info("Starting Event dispatcher..")
        while True:
            for event in self.events:
                if (time.time() - event.ctime) >= event.time:
                    logger.info("Running: {}".format(event.name))
                    event()
                    event.ctime = time.time()
