import logging

FORMAT = '%(asctime)s:%(name)s:%(levelname)s: %(message)s'
logging.basicConfig(filename='plexmonitor.log', filemode='w', level=logging.INFO, format=FORMAT)

def get_logger(name):
    return logging.getLogger(name)
