import sys
import pathlib
import diskcache
from cachetools import TTLCache


class CacheKey:
    ALL: dict = {}

    def __init__(self, key, ttl=600, ttl2=None, maxsize=100):
        self.key = key
        self.ttl = ttl
        self.ttl2 = ttl2 or (ttl * 2)
        self.cache1 = TTLCache(maxsize=maxsize, ttl=ttl)
        self.cache2 = diskcache.Cache(self.get_cache_dir())

    @staticmethod
    def init(key, ttl=600, ttl2=None, maxsize=100):
        if key in CacheKey.ALL:
            return CacheKey.ALL[key]
        cache = CacheKey(key, ttl, ttl2, maxsize)
        return CacheKey.ALL.setdefault(key, cache)

    def get(self):
        try:
            return self.cache1[self.key]
        except KeyError:
            pass
        return self.cache2.get(self.key)

    def set(self, val):
        self.cache1[self.key] = val
        self.cache2.set(self.key, val, expire=self.ttl2)
        return val

    def delete(self):
        self.cache1.pop(self.key, None)
        self.cache2.delete(self.key)

    def get_cache_dir(self):
        home = pathlib.Path.home()
        name = __package__
        if sys.platform == "win32":
            return home / "AppData" / "Local" / "Cache" / name
        return home / ".cache" / name
