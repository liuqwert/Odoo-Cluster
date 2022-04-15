# -*- coding: utf-8 -*-
##############################################################################
#
#    odoo_cluster
#    author:15251908@qq.com (openliu)
#    license:'LGPL-3
#
##############################################################################
__all__ = ['RedisLRU']

import types
import dill as pickle
# import zlib
from odoo.tools.lru import LRU


def to_str(obj):
    if isinstance(obj, tuple) or isinstance(obj, list) or isinstance(obj, frozenset) or isinstance(obj, set) \
            or isinstance(obj, enumerate):
        return '[' + ",".join(to_str(i) for i in obj) + ']'
    elif isinstance(obj, dict):
        return '{' + ",".join(to_str(kv) for kv in obj.items()) + '}'
    else:
        return str(obj)


class lru_stat(object):
    def __init__(self):
        self.clearcount = 0


LRUSTAT = lru_stat()

FUNC_INC_KEY="FINC"


class RedisLRU(object):

    def __init__(self, redis, namespace):
        self.fncache = LRU(1024)
        self.redis = redis
        self.namespace = namespace
        self.clear_command = "unlink %s" % self.namespace
        self.REGISREGVTY_VER="REGV"+namespace

    def incrRegisty(self):
        return self.redis.execute_command('incr', self.REGISREGVTY_VER)

    def curRegisty(self):
        r= self.redis.execute_command('get', self.REGISREGVTY_VER)
        return r if r else 0


    def __getitem__(self, obj):
        key = to_str(obj)
        # val = None
        # ver = None
        # fn = None
        try:
            val = self.redis.hget(self.namespace, key)
            if val:
                if val.isdigit():
                    if obj in self.fncache:
                        (ver, fn) = self.fncache[obj]
                        if int(val) == ver:
                            return fn
                else:
                    return pickle.loads(val)
        except Exception, e:
            # print "exception:", e
            # print "values:", self.namespace, key, val, val.isdigit(), ver, fn
            raise TypeError(e)
        raise KeyError("None")

    def __setitem__(self, obj, val):
        key = to_str(obj)
        if isinstance(val, types.FunctionType):
            ver = self.redis.execute_command('incr', FUNC_INC_KEY)
            self.fncache[obj] = (ver, val)
            self.redis.hset(self.namespace, key, ver)
        else:
            val = pickle.dumps(val)
            self.redis.hset(self.namespace, key, val)

    def __delitem__(self, obj):
        key = to_str(obj)
        self.redis.hdel(self.namespace, key)

    def get(self, obj):
        return self.__getitem__(obj)

    def set(self, obj, val=None):
        self.__setitem__(obj, val)

    def pop(self, obj):
        res = self.__getitem__(obj)
        self.__delitem__(obj)
        return res

    def clear(self):
        self.fncache.clear()
        self.redis.execute_command(self.clear_command)
        LRUSTAT.clearcount += 1

    def iteritems(self):
        hgetall = self.redis.hgetall(self.namespace)
        for key, val in hgetall.iteritems():
            yield {key, pickle.loads(val)}

    def iterkeys(self):
        return iter(self.redis.hgetall(self.namespace))

    def itervalues(self):
        for key, v in self.redis.hgetall(self.namespace).iteritems():
            yield v

    def keys(self):
        return self.redis.hgetall(self.namespace).keys()
