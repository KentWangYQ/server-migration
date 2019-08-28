import os
import sys
import logging


class Service(object):
    IP = '127.0.0.1'
    PORT = 8080

    MAX_RETRY = 3


def _get_path_from_txt(txt):
    result = []
    if os.path.exists(txt):
        with open(txt) as file:
            while True:
                line = file.readline()
                if not line:
                    break
                result.append(line.strip('\n'))
    return result


class Source(object):
    include = _get_path_from_txt('./config/include.txt')
    exclude = _get_path_from_txt('./config/exclude.txt')


logger = logging.getLogger('mig')
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)

che = logging.StreamHandler()
che.setLevel(logging.WARNING)
che.setFormatter(formatter)

logger.addHandler(che)
logger.addHandler(ch)
