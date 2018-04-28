import sys
import json
import getpass
from os import path, environ


#Config File paths
configfile = path.join(path.realpath(""), "config.json")

#Loads bot config file
class Config():
    def __init__(self, args=None):
        self.args = args
        self.__config = dict()
        try:
            with open(configfile, 'r') as f:
                self.__config = json.load(f)
        except Exception as e:
            return
        for attr in self.__config:
            setattr(self.__class__, attr, self.__config[attr])
