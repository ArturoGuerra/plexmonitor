import subprocess

from utils import get_logger

logger = get_logger(__name__)

class Monitor():
    def __init__(self):
        self.units = {
                "plexmediaserver": "Plex Server",
                "plexpy": "PlexPy",
                "sickrage": "SickRage",
                "couchpotato": "CouchPotato",
                "nzbget": "NZBGet",
                "deluged": "Deluge Daemon",
                "deluge-web": "Deluge Web",
                "nzbhydra": "Heil Hydra"
                }
        self.results = list()

    def parse(self, name, unit_name):
        cmd = f'systemctl status {unit_name}'
        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        stdout = proc.communicate()[0].decode('utf-8').split('\n')
        status = 'Offline'
        for line in stdout:
            if (('Active:' in line) and '(running)' in line):
                status = 'Running'
                break
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
            if result['status'].lower() == "running":
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
