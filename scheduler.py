import time


class Scheduler():
    def __init__(self):
        self.time = time.time()
        self.events = list()
    def add(self, event):
        self.events.append(event)

    def run(self):
        print("Starting Event dispatcher..")
        while True:
            for event in self.events:
                if (time.time() - event.ctime) >= event.time:
                    print("Running: {}".format(event.name))
                    event()
                    event.ctime = time.time()
