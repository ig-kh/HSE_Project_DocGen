import hashlib


class EntityCache:

    def __init__(self):

        self.cache = {}

    def _hash(self, text: str):

        return hashlib.sha256(text.encode()).hexdigest()

    def get(self, text: str):

        key = self._hash(text)

        return self.cache.get(key)

    def set(self, text: str, result: str):

        key = self._hash(text)

        self.cache[key] = result