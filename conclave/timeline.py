from itertools import groupby
from typing import Any
import json
import os
import uuid
import datetime
from jinja2 import Environment, FileSystemLoader

from conclave.scenario_result import ScenarioResult


class Timeline:

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

    def generateTimeline(self, taskReport: Any):
        print(f"Generate timeline...")

        groups = []
        items = []
        allSteps = {}
        allScenarios = {}
        for key, group in groupby(sorted(taskReport,key=lambda x:x["feature"]), lambda x: x["feature"]):
            feature = {
                "id": key,
                "content": key,
                "nestedGroups":  [],
                "treeLevel": 1
            }
            #print(f"timeline: {feature}")
            groups.append(feature)

            for t in group:
                feature["nestedGroups"].append(t["id"])
                scenarioResult: ScenarioResult = t["scenario"]
                groupContent = f"<h4>{t['name']}</h4><div><i>elapsed:{round(scenarioResult.elapsed,2)} (s)</i></div>"
                groups.append({
                    "id" : t["id"],
                    "content": groupContent
                })
                items.append({
                    "id": t["id"],
                    "content": "",
                    "group": t["id"],
                    "start": scenarioResult.startTime.strftime("%m/%d/%Y, %H:%M:%S"),
                    "end": scenarioResult.endTime.strftime("%m/%d/%Y, %H:%M:%S"),
                    "type": "background",
                    "className": "negative",
                })
                for step in scenarioResult.steps:
                    if "start" in step and step["start"]:
                        id = uuid.uuid4().hex
                        items.append({
                        "id": id,
                        "content": f"{step['keyword']}{step['text']}",
                        "group": t["id"],
                        "start": step["start"].strftime("%m/%d/%Y, %H:%M:%S"),
                        "end": step["end"].strftime("%m/%d/%Y, %H:%M:%S"),
                        "type": "range",
                        "title": step["elapsed"]
                        })
                        allSteps[id] = step

                dict_filter = lambda x, y: dict([ (i,x[i]) for i in x if i in set(y) ])
                allScenarios[t["id"]] = dict_filter(vars(scenarioResult), ("elapsed","pid","threadId","startTime", "endTime",))
                
                

                
        def datetimeConverter(o):
            if isinstance(o, datetime.datetime):
                return o.__str__()
        
        

        pgroups,pitems = self.__getAllPids(taskReport)

        curdir = os.path.dirname(__file__)
        cssContent = ""
        jsContent = ""
        with open(os.path.join(curdir,'vis-timeline-graph2d.min.css'), "r", encoding='utf8') as fh:
            cssContent = fh.read()
        with open(os.path.join(curdir,'vis-timeline-graph2d.min.js'), "r", encoding='utf8') as fh:
            jsContent = fh.read()
        template = self.templateEnv.get_template("timeline.html")
        str = template.render(groups=json.dumps(groups),
        css=cssContent,
        js=jsContent,
        items=json.dumps(items),
        steps=json.dumps(allSteps, default=datetimeConverter),
        scenarios=json.dumps(allScenarios, default=datetimeConverter),
        plistGroups=json.dumps(pgroups, default=datetimeConverter),
        plistItems=json.dumps(pitems, default=datetimeConverter)
        )
        with open("timeline_output.html", "w", encoding='utf8') as fh:
            fh.write(str)
        
