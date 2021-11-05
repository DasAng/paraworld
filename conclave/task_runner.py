from typing import Any, Optional
from gherkin.token_scanner import TokenScanner
from gherkin.parser import Parser

from conclave.timeline import Timeline
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

Dialect.concurrent_keywords = concurrent_keywords
TokenMatcher.match_StepLine = match_stepline

class TaskRunner:

    def __init__(self,debugMode=False) -> None:
        self.parser = Parser()
        self.completedTasks: list[str] = []
        self.groups = {}
        self.pool = ThreadPoolExecutor()
        self.parallelPool = ProcessPoolExecutor(max_workers=multiprocessing.cpu_count())
        self.taskReport = []
        self.setupTasks: list[Task] = []
        self.teardownTasks: list[Task] = []
        self.allTaskIds: list[str] = []
        self.mainTasks: list[Task] = []
        self.debugMode: bool = debugMode

    def run(self, featureFiles: list[str]):
        for file in featureFiles:
            self.__parse(file)
        
        ## run any setup tasks
        error = self.__runSetupTasks()

        if not error:
            ## run sequential tasks
            self.__runMainTasks()

        ## run any teardown tasks
        error = self.__runTeardownTasks()

        ## print test report
        self.__printTestReport()

        return len(list(filter(lambda x: "failed" in x["status"], self.taskReport))) > 0

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
            group = self.__getGroupTag(tg, tag)
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
            taskList = [i for i in taskList if not any(x.name == i.name for x in skipped_tasks)]
        if len(new_tasks) > 0:
            taskList = [i for i in taskList if not any(x.name == i.name for x in new_tasks)]
        return new_tasks, taskList

    def runWorkerThread(self, taskList):
        tasks_to_submit, taskList = self.__getNextTask(taskList)
        futures = {}
        for task in tasks_to_submit:
            if task.isConcurrent:
                futures[self.pool.submit(task.scenario.run)] = task
            elif task.isParallel:
                futures[self.parallelPool.submit(task.scenario.run)] = task
        
        
        self.__print(f"adding new tasks: {[(f'name: {t.name}',f'id:{t.id}') for t in tasks_to_submit]}")
        self.__print(f"tasks in pool: {[(f'name: {t.name}',f'id:{t.id}') for t in futures.values()]}")

        while futures:
            done, _ = wait(futures,return_when=concurrent.futures.FIRST_COMPLETED)
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
                        item = self.pool.submit(t.scenario.run)
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
            print(f"{bcolors.OKCYAN}[task_manager] {msg}{bcolors.ENDC}\n")
    

    def __isParentTaskFailed(self, groups):
        ptask = []
        for t in self.taskReport:
            if 'id' in t:
                if any(t['id'] == x for x in groups):
                    ptask.append(t)
        return any(y['status'] == "failed" or y['status'] == "skipped" for y in ptask)
    
    def __addTaskToReport(self, task: Task, status: str, error: str, elapsed: float, scenarioResult: Any):
        if not any(task.name == x["name"] for x in self.taskReport):
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
    

    def generateTimeline(self):
        timeline = Timeline()
        timeline.generateTimeline(self.taskReport)
    
    def generateDependencyGraph(self):
        depGraph = DependencyGraph()
        depGraph.generateGraph("dependency_output.html",self.taskReport,self.groups)
    

