# wrapper on single redis intance
# this is naive and blocking XD

import redis

_broker = redis.StrictRedis(host='localhost', port=6379, db=0)

class Broker(object):
    def __init__(self, name):
        self.name = name

    def get_broker(self):
        return _broker

