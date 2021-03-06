from threading import Lock
from typing import Any
import multiprocessing

class Singleton(type):
    __instances = {}
    __lock: Lock = Lock()

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        with self.__lock:
            if self not in self.__instances:
                instance = super().__call__(*args, **kwds)
                self.__instances[self] = instance
        return self.__instances[self]


class World(metaclass=Singleton):

    def __init__(self) -> None:
        self.__props = multiprocessing.Manager().dict()

    def setProp(self,key: Any, value: Any):
        self.__props[key] = value
    
    def getProp(self,key: Any) -> Any:
        if key in self.__props:
            return self.__props[key]
    
    def __getstate__(self):
        state = self.__dict__.copy()
        return state
    
    def __setstate__(self,state):
        self.__dict__.update(state)

    