from multiprocessing import Process
import multiprocessing
import os
import time
import psutil
import datetime
import json
import queue
from jinja2 import Environment, FileSystemLoader
from .template_base import TemplateBase
from .helpers import datetimeConverter


def getProcessByName(processName: str) -> list[Process]:
    procs: list[Process] = []
    for proc in psutil.process_iter():
        if processName in proc.name():
            procs.append(proc)
    return procs


def writeDataPoints(data, fileName):
     
    datetimestr = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
    with open(fileName, 'a+') as f:
        f.write(f"{datetimestr}> {json.dumps(data, default=datetimeConverter)}\n")

def getCpuUsageByPid(p: Process):
    iowait = None
    cpunum = None
    if hasattr(psutil.Process, "cpu_num"):
        cpunum = p.cpu_num()
    cputimes = p.cpu_times()
    cpus_percent = p.cpu_percent()
    if hasattr(cputimes, "iowait"):
        iowait = cputimes[4]
    
    return { "pid": p.pid, "cpu": cpus_percent, "iowait": iowait, "core": cpunum}


def runMonitor(q: multiprocessing.Queue):
    fileName = f"monitor.txt"
    selfPid = os.getpid()
    print(f"monitor process running: {selfPid}")
    procList = {}
    while True:
        time.sleep(1)
        procs = getProcessByName("python")
        datapoint = []
        for p in procs:
            if p.pid not in procList and p.pid != selfPid:
                procList[p.pid] = p
            if p.pid != selfPid:
                usage = getCpuUsageByPid(procList[p.pid])
                datapoint.append(usage)
        writeDataPoints(datapoint, fileName)
        try:
            msg = q.get(block=False)
            print(f"got termination signal. Exit monitor now")
            break
        except queue.Empty:
            pass
    

class Monitor(TemplateBase):

    def __init__(self) -> None:
        self.signalQueue = multiprocessing.Queue()
        self.monitorProcess = Process(daemon=True,target=runMonitor, args=(self.signalQueue,))

    def startMonitor(self):
        self.monitorProcess.start()
    
    def stopMonitor(self):
        self.signalQueue.put("STOP")
        self.monitorProcess.join()
    
    def __getAllLines(self, fileName: str):
        with open(fileName, "r", encoding='utf8') as fh:
            lines = [line.rstrip() for line in fh]
            return lines
    
    def generateReport(self):
        templateFileName = "monitor.html"
        dataFile = f"monitor.txt"
        env = Environment(loader=FileSystemLoader(os.path.dirname(__file__)))
        cssContent = self.getTemplatePropertyContent('vis-timeline-graph2d.min.css')
        jsContent = self.getTemplatePropertyContent('vis-timeline-graph2d.min.js')
        template = env.get_template(templateFileName)
        pids = []

        allItems = []
        dataLines = self.__getAllLines(dataFile)
        for line in dataLines:
            date = line.split("> ")[0]
            item = line.split("> ")[-1]
            parsedItem = json.loads(item)
            for p in parsedItem:
                p["x"] = date
                p["y"] = p["cpu"]
                p["group"] = "cpu time"
                pids.append(p["pid"])
            allItems += parsedItem
            parsedItem = json.loads(item)
        
        pids = list(dict.fromkeys(pids))
        #print(f"all pids: {pids}")

        #print(f"all itens: {allItems}")

        output = template.render(
            pids=pids,
            css=cssContent,
            js=jsContent,
            allItems=json.dumps(allItems)
        )
        self.writeTemplateContent("monitor_output.html",output)


        
