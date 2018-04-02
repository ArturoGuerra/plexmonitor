#!/usr/bin/env python
import time

from monitor import Monitor
from mail import Mail
from config import Config
from scheduler import Scheduler
from utils import get_logger

class PlexMonitor:
    def __init__(self, monitor, config, logger):
        self.monitor = monitor
        self.logger = logger
        self.recipients = config.recipients
        self.sender = config.sender
        self.subject = "Plex Monitor"

    def format(self, results, event):
        def get_html(errors, passed):
            return "<html></html>"

        def get_content(errors, passed):
            fstring = "Errored: \n"
            for error in errors:
                fstring = fstring + "{} - {}\n".format(error['name'], error['status'])
            fstring = fstring + "\n\nPassed:\n"
            if len(errors) == 0:
                fstring = "Passed:\n"
            for item in passed:
                fstring = fstring + "{} - {}\n".format(item['name'], item['status'])
            return fstring

        if event == 'errors':
            html = get_html(results['errored'], results['passed'])
            content = get_content(results['errored'], results['passed'])
            return html, content

        else:
            html = get_html(results[1], results[0])
            content = get_content(results[1], results[0])
        return html, content

    def send(self, html, content):
        Mail(
            self.subject,
            html,
            content,
            self.recipients,
            self.sender
        )()

    def full(self):
        results = self.monitor.check()
        html, content = self.format(results, "full")
        self.send(html, content)

    def __call__(self):
        results = self.monitor()
        if results['status'] == 'failed':
            html, content = self.format(results, 'errors')
            self.send(html, content)



class Event():
    def __init__(self, name, stime, callback):
        self.name = name
        self.time = stime
        self.callback = callback
        self.ctime = time.time()
    def __call__(self):
        self.callback()

def start():
    config = Config()
    monitor = Monitor()
    logger = get_logger(__name__)
    pmonitor = PlexMonitor(monitor, config, logger)
    s = Scheduler()
    s.add(Event("Daily Log", 86400, pmonitor.full))
    s.add(Event("Error Log", 300, pmonitor))
    s.run()


if __name__ == "__main__":
    start()
