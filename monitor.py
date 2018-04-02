from systemd_dbus.manager import Manager
from systemd_dbus.exceptions import SystemdError
from utils import get_logger

logger = get_logger(__name__)

class Monitor():
    def __init__(self):
        self.manager = Manager()
        self.units = {
                "plexmediaserver": "Plex Server",
                "plexpy": "PlexPy",
                "sickrage": "SickRage",
                "couchpotato": "CouchPotato",
                "nzbget": "NZBGet",
                "deluged": "Deluge Daemon",
                "deluge-web": "Deluge Web"
                }
        self.results = list()

    def parse(self, name, unit_name):
        try:
            unit = self.manager.get_unit(unit_name + ".service")
            status = str(unit.properties.SubState)
        except SystemdError as e:
            status = "offline"
        return {
            "name": name,
            "service": unit_name,
            "status": status
            }

    def update(self):
        self.results = list()
        for sname in self.units:
            unit = self.parse(self.units[sname], sname)
            self.results.append(unit)

    def get(self, service):
        try:
            if service.endswith(".service"):
                service = service.split('.')[0]
            name = self.units[service]
            return self.parse(name, service)
        except IndexError:
            return { "error": "Service not found"}

    def check(self):
        self.update()
        errored = list()
        passed = list()
        for result in self.results:
            if result['status'] == "running":
                passed.append(result)
            else:
                errored.append(result)
        return passed, errored

    def errorcheck(self):
        passed, errored = self.check()
        if len(errored) == 0:
            return { "status": "passed" }
        return {
            "status": "failed",
            "errored": errored,
            "passed": passed
            }

    def __call__(self):
        self.update()
        return self.errorcheck()
