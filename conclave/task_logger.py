from .color import bcolors
import datetime

class TaskLogger:
    def __init__(self, funcName):
        self.msg = ""
        self.funcName = funcName

    def log(self,msg):
        self.msg += f"[{datetime.datetime.now().strftime('%m/%d/%Y, %H:%M:%S')} {self.funcName}] {msg}\n"
    def error(self,msg):
        self.msg += f"{bcolors.FAIL}[{datetime.datetime.now().strftime('%m/%d/%Y, %H:%M:%S')} {self.funcName}] {msg}{bcolors.ENDC}\n"