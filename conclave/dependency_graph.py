import os
from typing import Any
from jinja2 import Environment, FileSystemLoader

from .template_base import TemplateBase

from .task import Task

class DependencyGraph(TemplateBase):

    def __init__(self) -> None:
        pass
    
    def __buildDependencyGraph(self, taskReport: Any, groups: Any):
        graph = ""
        for k,v in groups.items():
            graph += f"subgraph {k}\n"
            for node in v:
                graph += f"{node}\n"
            graph += f"end\n"
        for t in taskReport:
            task: Task = t["task"]
            if task.depends is not None:
                for dp in task.depends:
                    graph += f"{dp}-->{task.id}[{task.name}]\n"
            if task.dependsGroups is not None:
                for dp in task.dependsGroups:
                    graph += f"{dp}-->{task.id}[{task.name}]\n"
            graph += f"{task.id}[{task.name}]\n"
        return graph


    def generateGraph(self, fileName: str, taskReport: Any, groups: Any):
        templateFileName = "dependency.html"
        env = Environment(loader=FileSystemLoader(os.path.dirname(__file__)))
        jsContent = self.getTemplatePropertyContent('mermaid.min.js')
        template = env.get_template(templateFileName)
        graph = self.__buildDependencyGraph(taskReport,groups)

        output = template.render(
            js=jsContent,
            graph=graph
        )

        dirs = os.path.dirname(fileName)
        if dirs:
            os.makedirs(os.path.dirname(fileName), exist_ok=True)
        self.writeTemplateContent(fileName,output)

