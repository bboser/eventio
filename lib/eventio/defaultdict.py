class defaultdict:
    def __init__(self, default_factory):
        self.dict = {}
        self.default_factory = default_factory
    def __getitem__(self, key):
        try:
            return self.dict[key]
        except KeyError:
            v = self.default_factory.copy()
            self.dict[key] = v
            return v
    def __setitem__(self, key, v):
        self.dict[key] = v
