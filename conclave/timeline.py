from itertools import groupby
from typing import Any
import json
import os
import uuid
import datetime
from jinja2 import Environment, FileSystemLoader
from .scenario_result import ScenarioResult
from .template_base import TemplateBase
from .helpers import datetimeConverter


class Timeline(TemplateBase):

    def __init__(self) -> None:
        self.templateEnv = Environment(loader=FileSystemLoader(os.path.dirname(__file__)))

    def __getAllPids(self, taskReport: Any):
        processList = {}
        pgroups = []
        threadIds = []
        pitems = []
        for key, group in groupby(sorted(taskReport,key=lambda x:x["feature"]), lambda x: x["feature"]):
            for t in group:
                scenarioResult: ScenarioResult = t["scenario"]
                if scenarioResult:
                    for step in scenarioResult.steps:
                        if step["pid"] is not None:
                            processList.setdefault(step["pid"], []).append(step)
        
        #print(f"process list: {processList}")
        for key,val in processList.items():
            threadIds = [x["threadId"] for x in val]
            threadIds = list(dict.fromkeys(threadIds))
            for threadId in threadIds:
                pgroups.append({
                    "id": f"{key}_{threadId}",
                    "content": f"thread {threadId}"
                })
            threadIdGroups = [f"{key}_{x}" for x in threadIds]
            pgroups.append({
                "id": key,
                "content": f"Process Id {key}",
                "nestedGroups": threadIdGroups,
                "treeLevel": 1
            })
            for item in val:
                if item["threadId"] is not None:
                    pitems.append({
                        "id": uuid.uuid4().hex,
                        "content": "",
                        "group": f"{item['pid']}_{item['threadId']}",
                        "start": item["start"].strftime("%m/%d/%Y, %H:%M:%S"),
                        "end": item["end"].strftime("%m/%d/%Y, %H:%M:%S"),
                        "type": "background"
                    })
        #print(f"all thread ids: {threadIds}")
        return pgroups,pitems

    def __createFeatureItem(self,id):
        item = {
            "id": id,
            "content": id,
            "nestedGroups":  [],
            "treeLevel": 1
        }
        return item
    
    def __createScenarioItem(self, id, name, elapsed, isSkipped):
        if not isSkipped:
            content = f"<h4>{name}</h4><div><i>elapsed:{round(elapsed,2)}</i></div>"
            item = {
                "id" : id,
                "content": content
            }
            return item
        else:
            content = f"<h4>{name}</h4><div><i>elapsed:{round(elapsed,2)} (s)</i></div><div><i>Skipped</i></div>"
            item = {
                "id" : id,
                "content": content,
                "className": "skipped-scenario"
            }
            return item
    
    def __createScenarioBackgroundItem(self, id, startTime, endTime):
        item = {
            "id": id,
            "content": "",
            "group": id,
            "start": startTime.strftime("%m/%d/%Y, %H:%M:%S"),
            "end": endTime.strftime("%m/%d/%Y, %H:%M:%S"),
            "type": "background",
            "className": "negative",
        }
        return item

    def __createStepItem(self,itemId, groupId,step, scenarioStartTime):
        className = "default"
        if step["error"] is not None:
            className = "red"
        elif step["status"] == "skipped":
            className = "orange"
        item = {
            "id": itemId,
            "content": f"{step['keyword']}{step['text']}",
            "group": groupId,
            "start": step["start"].strftime("%m/%d/%Y, %H:%M:%S") if step["start"] is not None else scenarioStartTime.strftime("%m/%d/%Y, %H:%M:%S"),
            "end": step["end"].strftime("%m/%d/%Y, %H:%M:%S") if step["end"] is not None else scenarioStartTime.strftime("%m/%d/%Y, %H:%M:%S"),
            "type": "range",
            "title": step["elapsed"],
            "className": className
        }
        return item
    

    def generateTimeline(self, taskReport: Any, outputFilename="timeline_output.html"):
        print(f"Generate timeline...")

        groups = []
        items = []
        allSteps = {}
        allScenarios = {}
        for key, group in groupby(sorted(taskReport,key=lambda x:x["feature"]), lambda x: x["feature"]):
            feature = self.__createFeatureItem(key)
            
            groups.append(feature)

            for t in group:
                feature["nestedGroups"].append(t["id"])
                scenarioResult: ScenarioResult = t["scenario"]
                if scenarioResult:
                    scenarioItem = self.__createScenarioItem(t["id"], t["name"], scenarioResult.elapsed, False)
                    groups.append(scenarioItem)

                    scenarioBackgroundItem = self.__createScenarioBackgroundItem(t["id"], scenarioResult.startTime, scenarioResult.endTime)

                    items.append(scenarioBackgroundItem)

                    for step in scenarioResult.steps:
                        itemId = uuid.uuid4().hex
                        stepItem = self.__createStepItem(itemId,t["id"], step, scenarioResult.startTime)
                        items.append(stepItem)
                        allSteps[itemId] = step
                            

                    dict_filter = lambda x, y: dict([ (i,x[i]) for i in x if i in set(y) ])
                    allScenarios[t["id"]] = dict_filter(vars(scenarioResult), ("elapsed","pid","threadId","startTime", "endTime",))
                else:
                    scenarioItem = self.__createScenarioItem(t["id"], t["name"], t["elapsed"], True)
                    groups.append(scenarioItem)
                
                
        pgroups,pitems = self.__getAllPids(taskReport)


        cssContent = self.getTemplatePropertyContent('vis-timeline-graph2d.min.css')
        jsContent = self.getTemplatePropertyContent('vis-timeline-graph2d.min.js')

        template = self.templateEnv.get_template("timeline.html")
        output = template.render(groups=json.dumps(groups),
        css=cssContent,
        js=jsContent,
        items=json.dumps(items),
        steps=json.dumps(allSteps, default=datetimeConverter),
        scenarios=json.dumps(allScenarios, default=datetimeConverter),
        plistGroups=json.dumps(pgroups, default=datetimeConverter),
        plistItems=json.dumps(pitems, default=datetimeConverter)
        )

        dirs = os.path.dirname(outputFilename)
        if dirs:
            os.makedirs(os.path.dirname(outputFilename), exist_ok=True)
        self.writeTemplateContent(outputFilename,output)
