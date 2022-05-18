class ScenarioScope(object):

    def __init__(self):
        self._data = {}
    
    def __getattr__(self, attr):
        if attr[0] == "_":
            try:
                return self.__dict__[attr]
            except KeyError:
                raise AttributeError(attr)

        if attr in self._data:
            return self._data[attr]
            
        msg = "'{0}' object has no attribute '{1}'"
        msg = msg.format(self.__class__.__name__, attr)
        raise AttributeError(msg)
    
    def __setattr__(self, attr, value):
        if attr[0] == "_":
            self.__dict__[attr] = value
            return

        self._data[attr] = value