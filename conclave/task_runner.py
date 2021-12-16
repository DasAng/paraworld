import datetime
import os
from typing import Any, Optional
from gherkin.token_scanner import TokenScanner
from gherkin.parser import Parser

from conclave.report import Report

from .testresult_info import TestResultInfo

from .timeline import Timeline
from .task import Task
import threading
import concurrent
from .color import bcolors
from concurrent.futures import ThreadPoolExecutor, wait, ProcessPoolExecutor
from .scenario import Scenario
from itertools import groupby
import multiprocessing
from gherkin.token_matcher import TokenMatcher
from gherkin.dialect import Dialect
from .custom_keywords import concurrent_keywords, match_stepline
from .dependency_graph import DependencyGraph
import uuid
import time
import signal
import ctypes
import atexit
from .task_monitor import TaskMonitor

Dialect.concurrent_keywords = concurrent_keywords
TokenMatcher.match_StepLine = match_stepline

#atexit.unregister(concurrent.futures.thread._python_exit)
class TaskRunner:

    def __init__(self,debugMode=False,timeout=3600) -> None:
        self.parser = Parser()
        self.completedTasks: list[str] = []
        self.groups = {}
        self.pool = ThreadPoolExecutor()
        self.parallelPool = ProcessPoolExecutor(max_workers=multiprocessing.cpu_count(),mp_context=multiprocessing.get_context("spawn"))
        self.taskReport = []
        self.setupTasks: list[Task] = []
        self.teardownTasks: list[Task] = []
        self.allTaskIds: list[str] = []
        self.mainTasks: list[Task] = []
        self.debugMode: bool = debugMode
        self.testResult: TestResultInfo = None
        self.timeout = timeout
        self.taskMonitor = TaskMonitor()

    def run(self, featureFiles: list[str]) -> TestResultInfo:
        for file in featureFiles:
            self.__parse(file)
        
        start = time.time()
        startDate = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")

        self.taskMonitor.start()

        ## run any setup tasks
        error = self.__runSetupTasks()

        if not error:
            ## run main tasks
            self.__runMainTasks()

        ## run any teardown tasks
        error = self.__runTeardownTasks()

        end = time.time()
        endDate = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")

        ## print test report
        self.__printTestReport()

        self.testResult = TestResultInfo(
            elapsed=end-start,
            start=startDate,
            end=endDate,
            numCpu=multiprocessing.cpu_count(),
            pid=os.getpid(),
            success=len(list(filter(lambda x: "failed" in x["status"], self.taskReport))) <= 0
        )

        self.taskMonitor.cancel()
        self.taskMonitor.join()
        self.taskMonitor.pids = list(dict.fromkeys(self.taskMonitor.pids))
        self.__print(f"All process ids: {self.taskMonitor.pids}")
        for pid in self.taskMonitor.pids:
            os.kill(pid, signal.SIGTERM)
        #self.pool.shutdown(wait=False)
        # for t in self.pool._threads:
        #     self.__terminateThread(t)

        return self.testResult

    def __parse(self, featureFile: str):
        result = self.parser.parse(TokenScanner(featureFile))
        if not result:
            return
        
        if "feature" not in result:
            return

        if "children" not in result["feature"]:
            return
        
        feature = result["feature"]
        for child in feature["children"]:
            if "scenario" in child:
                sc = child["scenario"]
                self.__getScenario(sc, feature)
    
    # def __getFeatureId(self, feature: Any) -> str:
    #     tags = feature["tags"]
    #     id=uuid.uuid4().hex()
    #     for tag in tags:
    #         tg = tag["name"]
    #         if temp := self.__getIdTag(tg, tag): id = temp
    #     return id
    
    def __getScenario(self, scenario: Any, feature: Any) -> Task:
        tags = scenario["tags"]
        isConcurrent,id,depends,dependsGroups,group,runAlways,isSetup,isTeardown,isParallel = False,uuid.uuid4().hex,[],[],None,False,False,False,False
        for tag in tags:
            tg = tag["name"]
            if temp := self.__getConcurrentTag(tg): isConcurrent = temp
            if temp := self.__getParallelTag(tg): isParallel = temp
            if temp := self.__getRunAlwaysTag(tg): runAlways = temp
            if temp := self.__getSetupTag(tg): isSetup = temp
            if temp := self.__getTeardownTag(tg): isTeardown = temp
            if temp := self.__getIdTag(tg, tag): id = temp
            if temp := self.__getDependsTag(tg, tag): depends.append(temp)
            if temp := self.__getDependsGroupsTag(tg, tag): dependsGroups.append(temp)
            if temp := self.__getGroupTag(tg, tag): group = temp
        sc = Scenario(scenario["name"],scenario,feature,id)
        t = Task(scenario["name"], sc, feature, id,depends,dependsGroups,runAlways,group, isSetup, isConcurrent,isTeardown,isParallel)
        self.allTaskIds.append(t.id)
        if group is not None:
            self.groups.setdefault(group, []).append(id)
        if isSetup:
            self.setupTasks.append(t)
        elif isTeardown:
            self.teardownTasks.append(t)
        else:
            self.mainTasks.append(t)
        return t

    def __getGroupTag(self, name: str, tag: Any) -> Optional[str]:
        return tag["name"].split("@group_")[-1] if name.startswith("@group_") else None

    def __getIdTag(self, name: str, tag: Any) -> Optional[str]:
        return tag["name"].split("@id_")[-1] if name.startswith("@id_") else None
    
    def __getConcurrentTag(self, name: str) -> bool:
        return name == "@concurrent"
    
    def __getParallelTag(self, name: str) -> bool:
        return name == "@parallel"
    
    def __getRunAlwaysTag(self, name: str) -> bool:
        return name == "@runAlways"

    def __getDependsTag(self, name: str, tag: Any) -> Optional[str]:
        return tag["name"].split("@depends_")[-1] if name.startswith("@depends_") else None
    
    def __getDependsGroupsTag(self, name: str, tag: Any) -> Optional[str]:
        return tag["name"].split("@dependsGroups_")[-1] if name.startswith("@dependsGroups_") else None
    
    def __getSetupTag(self, name: str) -> bool:
        return name == "@setup"
    
    def __getTeardownTag(self, name: str) -> bool:
        return name == "@teardown"

    def __getNextTask(self,taskList) -> list[Task]:
        new_tasks: list[Task] = []
        skipped_tasks: list[Task] = []
        self.__print(f"tasks pending: {[(f'name: {t.name}',f'id:{t.id}') for t in taskList]}")
        for task in taskList:
            self.__print(f"check pending task: (name:{task.name},id:{task.id})")
            if len(task.depends) > 0:
                self.__print(f"task (name:{task.name},id:{task.id}) depends on: {task.depends}")
                if not set(task.depends).issubset(self.allTaskIds):
                    self.__addTaskToReport(task, "skipped", None, 0.0, None)
                    skipped_tasks.append(task)
                    self.completedTasks.append(task.id)
                    continue
                if not set(task.depends).issubset(self.completedTasks):
                    continue
                if self.__isParentTaskFailed(task.depends) and not task.runAlways:
                    self.__addTaskToReport(task, "skipped", None, 0.0, None)
                    self.__print(f"skip task: (name:{task.name},id:{task.id})")
                    skipped_tasks.append(task)
                    self.completedTasks.append(task.id)
                    continue
            if len(task.dependsGroups) > 0:
                self.__print(f"task (name:{task.name},id:{task.id}) depends on groups: {task.dependsGroups}")
                combine_groups = []
                for g in task.dependsGroups:
                    if g in self.groups:
                        combine_groups += self.groups[g]
                if not bool(combine_groups):
                    self.__print(f"no groups matching found for task: (name:{task.name},id:{task.id})")
                    self.__addTaskToReport(task, "skipped", None, 0.0, None)
                    skipped_tasks.append(task)
                    self.completedTasks.append(task.id)
                    continue
                if not set(combine_groups).issubset(self.completedTasks):
                    continue
                if self.__isParentTaskFailed(combine_groups) and not task.runAlways:
                    self.__addTaskToReport(task, "skipped", None, 0.0, None)
                    self.__print(f"dependent tasks failed so skip task: (name:{task.name},id:{task.id})")
                    skipped_tasks.append(task)
                    self.completedTasks.append(task.id)
                    continue
            new_tasks.append(task)
        if len(skipped_tasks) > 0:
            taskList = [i for i in taskList if not any(x.id == i.id for x in skipped_tasks)]
        if len(new_tasks) > 0:
            taskList = [i for i in taskList if not any(x.id == i.id for x in new_tasks)]
        return new_tasks, taskList

    def runWorkerThread(self, taskList):
        tasks_to_submit, taskList = self.__getNextTask(taskList)
        futures = {}
        for task in tasks_to_submit:
            if task.isConcurrent:
                futures[self.pool.submit(task.scenario.run,queue=None)] = task
            elif task.isParallel:
                futures[self.parallelPool.submit(task.scenario.run,queue=self.taskMonitor.signalQueue)] = task
        
        
        self.__print(f"adding new tasks: {[(f'name: {t.name}',f'id:{t.id}') for t in tasks_to_submit]}")
        self.__print(f"tasks in pool: {[(f'name: {t.name}',f'id:{t.id}') for t in futures.values()]}")

        while futures:
            startTime = time.time()
            done, notDone = wait(futures,return_when=concurrent.futures.FIRST_COMPLETED,timeout=self.timeout)
            endTime = time.time()
            elapsed = endTime-startTime
            self.__print(f"elapsed time: {elapsed}")
            if elapsed >= self.timeout:
                for c in notDone:
                    self.__print(f"tasks not done: (name:{futures[c].name},id:{futures[c].id}, running:{c.running()},cancelled:{c.cancelled()})")
                    self.__addTaskToReport(futures[c],"failed","timeout waiting for task to complete",self.timeout, None)
                self.__print(f"timeout waiting {self.timeout} (s) for remaining tasks to complete. Aborting.")
                break
            for c in done:
                fut = futures.pop(c)
                result = c.result()
                print(result.message)
                self.__print(f"task completed: (name:{fut.name},id:{result.id})")
                self.completedTasks.append(result.id)
                if result.exception is not None:
                    self.__addTaskToReport(fut,"failed",result.exception,result.elapsed, result)
                else:
                    self.__addTaskToReport(fut,"success",result.exception,result.elapsed, result)
                next_tasks,taskList = self.__getNextTask(taskList)
                if next_tasks is not None:
                    for t in next_tasks:
                        self.__print(f"adding new task (name:{t.name},id:{t.id})")
                        if t.isConcurrent:
                            item = self.pool.submit(t.scenario.run)
                            futures[item] = t
                        elif t.isParallel:
                            item = self.parallelPool.submit(t.scenario.run)
                            futures[item] = t
                self.__print(f"remaining tasks in pool: {[(f'name: {t.name}',f'id:{t.id}') for t in futures.values()]}")
    
    def __printTestReport(self):
        print(f"Test report:\n")

        for key, group in groupby(sorted(self.taskReport,key=lambda x:x["feature"]), lambda x: x["feature"]):
            print(f"\nFeature: {key}\n")
            for t in group:
                if t['status'] == 'success':
                    print(f"\tScenario: {t['name']}: {bcolors.OKGREEN}{t['status']}{bcolors.ENDC} (elapsed {t['elapsed']})")
                elif t['status'] == 'skipped':
                    print(f"\tScenario: {t['name']}: {bcolors.WARNING}{t['status']}{bcolors.ENDC} (elapsed {t['elapsed']})")
                else:
                    print(f"\tScenario: {t['name']}: {bcolors.FAIL}{t['status']}{bcolors.ENDC} (elapsed {t['elapsed']})")
                
                # if t['error'] is not None:
                #     print(f"\t\tError: {bcolors.FAIL}{t['error']}{bcolors.ENDC}")
                
                #print(f"all steps report: {t['scenario']}")
                if 'scenario' in t and t["scenario"] is not None:
                    if t['scenario'].steps:
                        for step in t["scenario"].steps:
                            status = step['status']
                            if status == 'failed':
                                print(f"\t  Step: {step['keyword']}{step['text']}{bcolors.FAIL} {step['status']}{bcolors.ENDC} (elapsed {step['elapsed']})")
                            elif status == 'skipped':
                                print(f"\t  Step: {step['keyword']}{step['text']}{bcolors.WARNING} {step['status']}{bcolors.ENDC} (elapsed {step['elapsed']})")
                            else:
                                print(f"\t  Step: {step['keyword']}{step['text']}{bcolors.OKGREEN} {step['status']}{bcolors.ENDC} (elapsed {step['elapsed']})")
                            if "error" in step and step['error'] is not None:
                                print(f"\t\t{bcolors.FAIL}{step['error']}{bcolors.ENDC}")

                    
    
    def __print(self,msg: str):
        if self.debugMode:
            print(f"{bcolors.OKCYAN}[{datetime.datetime.now().strftime('%m/%d/%Y, %H:%M:%S')} task_manager] {msg}{bcolors.ENDC}\n")
    

    def __isParentTaskFailed(self, groups):
        ptask = []
        for t in self.taskReport:
            if 'id' in t:
                if any(t['id'] == x for x in groups):
                    ptask.append(t)
        return any(y['status'] == "failed" or y['status'] == "skipped" for y in ptask)
    
    def __addTaskToReport(self, task: Task, status: str, error: str, elapsed: float, scenarioResult: Any):
        if not any(task.name == x["name"] and task.feature["name"] == x["feature"] for x in self.taskReport):
            self.taskReport.append({"name":task.name,"status":status,"error":error, "elapsed": elapsed, "id": task.id, "feature": task.feature["name"], "task": task, "scenario": scenarioResult})

    def __runMainTasks(self):
        return self.__runTasks(self.mainTasks)

    def __runSetupTasks(self):
        return self.__runTasks(self.setupTasks)
    
    def __runTeardownTasks(self):
        return self.__runTasks(self.teardownTasks)
    
    def __transformSeqTasks(self, taskList: list[Task]):
        dependTaskId = None
        for t in taskList:
            t.isConcurrent = True
            if dependTaskId is not None and len(t.depends) <= 0 and len(t.dependsGroups) <= 0:
                t.depends.append(dependTaskId)
            dependTaskId = t.id
        return taskList

    def __runTasks(self, taskList):
        error = False
        seqtasks = list(filter(lambda x: not x.isConcurrent and not x.isParallel, taskList))
        contasks = list(filter(lambda x: x.isConcurrent or x.isParallel, taskList))
        seqtasks = self.__transformSeqTasks(seqtasks)
        alltasks = contasks + seqtasks
        self.__print(f"all tasks: {[t.name for t in alltasks]}")

        workerThread = threading.Thread(target=self.runWorkerThread,kwargs={'taskList':alltasks})
        workerThread.start()
        
        workerThread.join()

        if len(list(filter(lambda x: "failed" in x["status"], self.taskReport))) > 0:
            error = True
        
        return error
    
    def __terminateThread(self,thread):
        self.__print(f"terminate thread: {thread.ident}")
        exc = ctypes.py_object(SystemExit)
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
            ctypes.c_long(thread.ident), exc)
        if res == 0:
            self.__print(f"none existent thread id")
            raise ValueError("nonexistent thread id")
        elif res > 1:
            self.__print(f"PyThreadState_SetAsyncExc failed")
            # """if it returns a number greater than one, you're in trouble,
            # and you should call it again with exc=NULL to revert the effect"""
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread.ident, None)
            raise SystemError("PyThreadState_SetAsyncExc failed")
    

    def generateTimeline(self):
        timeline = Timeline()
        timeline.generateTimeline(self.taskReport)
    
    def generateDependencyGraph(self):
        depGraph = DependencyGraph()
        depGraph.generateGraph("dependency_output.html",self.taskReport,self.groups)
    
    def generateReport(self):
        report = Report()
        report.generateReport(self.taskReport, self.testResult)
    

