from itertools import groupby
from typing import Any

from .template_base import TemplateBase
from .scenario import Scenario
from .task import Task
from .testresult_info import TestResultInfo
import xml.etree.ElementTree as ET

def encodeXMLText(text: str):
    text = text.replace("&", "&amp;")
    text = text.replace("\"", "&quot;")
    text = text.replace("'", "&apos;")
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")
    text = text.replace('\033[95m', "")
    text = text.replace('\033[94m', "")
    text = text.replace('\033[96m', "")
    text = text.replace('\033[92m', "")
    text = text.replace('\033[93m', "")
    text = text.replace('\033[91m', "")
    text = text.replace('\033[0m', "")
    text = text.replace('\033[1m', "")
    text = text.replace('\033[4m', "")
    return text

class TestSuite:
    
    def __init__(self,name: str,elapsed: float = None, error: str = None, status: str = None, logs: str = None) -> None:
        self.name = name
        self.elapsed = elapsed
        self.error = error
        self.status = status
        self.logs = logs
    
    def toXml(self):
        el = ET.Element("testcase",attrib={"name": self.name,"time": str(self.elapsed)})
        if self.error:
            f = ET.Element("failure")
            f.text = encodeXMLText(self.error)
            el.append(f)
        if self.status == 'skipped':
            f = ET.Element("skipped")
            el.append(f)
        logEl = ET.Element("system-out")
        if self.logs:
            logEl.text = encodeXMLText(self.logs)
        el.append(logEl)
        return el


class JUnitReport(TemplateBase):

    def __init__(self) -> None:
        pass

    def __getFeatureTimeAndDuration(self, scenarios: Any):
        startTime = None
        endTime = None
        for scenario in scenarios:
            if "startTime" in scenario:
                if not startTime:
                    startTime = scenario['startTime']
                elif startTime and scenario['startTime'] < startTime:
                    startTime = scenario['startTime']
            if "endTime" in scenario:
                if not endTime:
                    endTime = scenario['endTime']
                elif endTime and scenario['endTime'] > endTime:
                    endTime = scenario['endTime']
        
        if startTime and endTime:
            return startTime,endTime,(endTime - startTime).total_seconds()
        
        return startTime,endTime,0
        

    def __getAllFailedFeatures(self, features: Any):
        return len(list(filter(lambda f: f['status'] == 'failed', features)))

    def generateReport(self,taskReport: Any, testResult: TestResultInfo):
        features = []
        for key, group in groupby(sorted(taskReport,key=lambda x:x["feature"]), lambda x: x["feature"]):
            scenarios = []
            featureStatus="success"
            for t in group:
                if t["status"] == 'failed':
                    featureStatus = 'failed'
                task: Task = t["task"]
                scenario: Scenario = task.scenario
                feature: Any = task.feature
                if t['scenario']:
                    scenarios.append({"detail": t['scenario'].scenario, "status": t["status"], "elapsed": t["elapsed"], "error": t["error"], "startTime": t['scenario'].startTime, "endTime": t['scenario'].endTime, "logs": t['scenario'].message})
                else:
                    scenarios.append({"detail": scenario.gherkinScenario, "status": t["status"], "elapsed": t["elapsed"], "error": t["error"], "logs": None})
            features.append({"name": key, "status": featureStatus, "scenarios":scenarios, "description": feature['description']})

        root = ET.Element("testsuites", attrib={"time": str(testResult.elapsed)})
        tree = ET.ElementTree(root)        
        for feature in features:
            featureStartTime,featureEndTime,featureElapsed = self.__getFeatureTimeAndDuration(feature['scenarios'])
            testsuite = ET.Element("testsuite",
                attrib={
                    "name": feature["name"], 
                    "time": str(featureElapsed), 
                    "tests": str(len(feature['scenarios'])),
                    "skipped": str(len(list(filter(lambda sc: sc['status'] == 'skipped', feature['scenarios'])))),
                    "failures": str(len(list(filter(lambda sc: sc['status'] == 'failed', feature['scenarios'])))),
                    "timestamp": str(featureStartTime)
                }
            )
            root.append(testsuite)
            if all(sc['status'] == 'skipped' for sc in feature['scenarios']):
                feature['status'] = 'skipped'
            elif not any(sc['status'] == 'failed' for sc in feature['scenarios']) and any(sc['status'] == 'skipped' for sc in feature['scenarios']):
                feature['status'] = 'incomplete'
            
            for scenario in feature['scenarios']:
                tc = TestSuite(
                    name=scenario['detail']['name'],
                    elapsed=scenario['elapsed'],
                    error=scenario['error'],
                    status=scenario['status'],
                    logs=scenario['logs']
                )
                testsuite.append(tc.toXml())
        
        countFailedFeatures = self.__getAllFailedFeatures(features)
        root.attrib["failures"] = str(countFailedFeatures)
        
        self.writeTemplateContent("junit_output.xml",ET.tostring(tree.getroot(),encoding='unicode', method='xml'))
