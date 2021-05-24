import logging

log = logging.getLogger("erminer")
log.setLevel(logging.DEBUG)
log.propagate = False


class ExpandLeftStore(object):
    """LeftStore structure used by the ERMiner algorithm"""
    def __init__(self):
        super().__init__()
        pass