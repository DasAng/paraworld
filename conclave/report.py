from itertools import groupby
import os
import json
from typing import Any
from jinja2 import Environment,FileSystemLoader

from .scenario import Scenario
from .task import Task
from .scenario_result import ScenarioResult
from .template_base import TemplateBase
from .helpers import datetimeConverter


class Report(TemplateBase):

    def __init__(self) -> None:
        pass

    def generateReport(self, taskReport: Any):
        templateFileName = "report.html"
        env = Environment(loader=FileSystemLoader(os.path.dirname(__file__)))
        jsContent = self.getTemplatePropertyContent('report.min.js')
        template = env.get_template(templateFileName)

        #print(f"task reports: {taskReport}")

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
                scenarios.append({"detail": t['scenario'].scenario, "status": t["status"], "elapsed": t["elapsed"], "error": t["error"]})
            features.append({"name": key, "status": featureStatus, "scenarios":scenarios})
            
        output = template.render(
            js=jsContent,
            data=json.dumps(features, default=datetimeConverter)
        )

        self.writeTemplateContent("report_output.html",output)