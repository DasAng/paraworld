from .color import bcolors

class TaskLogger:
    def __init__(self, funcName):
        self.msg = ""
        self.funcName = funcName

    def log(self,msg):
        self.msg += f"[{self.funcName}] {msg}\n"
    def error(self,msg):
        self.msg += f"{bcolors.FAIL}[{self.funcName}] {msg}{bcolors.ENDC}\n"