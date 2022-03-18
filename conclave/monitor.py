from multiprocessing import Process
from itertools import groupby
import multiprocessing
import os
import time
from typing import Any
import psutil
import datetime
import json
import queue
from jinja2 import Environment, FileSystemLoader
from .template_base import TemplateBase
from .helpers import datetimeConverter
from .scenario_result import ScenarioResult


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
    procList = {}
    while True:
        time.sleep(1)
        procs = getProcessByName("python")
        datapoint = []
        for p in procs:
            if p.pid not in procList and p.pid != selfPid:
                procList[p.pid] = p
            if p.pid != selfPid:
                try:
                    usage = getCpuUsageByPid(procList[p.pid])
                    datapoint.append(usage)
                except Exception as e:
                    print(f"monitor failed to get cpu usage for pid: {e}")
        writeDataPoints(datapoint, fileName)
        try:
            msg = q.get(block=False)
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
    
    def __getAllPids(self, taskReport: Any):
        pids = []
        for key, group in groupby(sorted(taskReport,key=lambda x:x["feature"]), lambda x: x["feature"]):
            for t in group:
                scenarioResult: ScenarioResult = t["scenario"]
                if scenarioResult:
                    for step in scenarioResult.steps:
                        if step["pid"] is not None:
                            pids.append(step["pid"])
        
        return pids

        
    def generateReport(self, taskReport: Any):
        templateFileName = "monitor.html"
        dataFile = f"monitor.txt"
        env = Environment(loader=FileSystemLoader(os.path.dirname(__file__)))
        cssContent = self.getTemplatePropertyContent('vis-timeline-graph2d.min.css')
        jsContent = self.getTemplatePropertyContent('vis-timeline-graph2d.min.js')
        template = env.get_template(templateFileName)
        allPids = self.__getAllPids(taskReport)
        allPids = list(dict.fromkeys(allPids))
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
                if p["pid"] in allPids:
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
        if os.path.exists(dataFile):
            os.remove(dataFile)


        
