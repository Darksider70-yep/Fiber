class Environment(dict):
    def __init__(self, parent=None):
        self.variables = {}
        self.parent = parent
        self.constants = set()
        self.finals = set()
        self.statics = set()

    def get(self, name):
        # ✅ Look up recursively in parent environments
        if name in self:
            return self[name]
        elif self.parent:
            return self.parent.get(name)
        else:
            raise KeyError(name)

    def set_local(self, name, value):
        # ✅ Always write locally in this environment
        self[name] = value

    def set_upwards(self, name, value):
        # ✅ Assign in parent if exists; otherwise local
        if name in self:
            self[name] = value
        elif self.parent:
            self.parent.set_upwards(name, value)
        else:
            self[name] = value
