import os
from typing import Any
from jinja2 import Environment, FileSystemLoader

from .task import Task

class DependencyGraph:

    def __init__(self) -> None:
        pass

    def __getTemplatePropertyContent(self, fileName: str):
        curdir = os.path.dirname(__file__)
        with open(os.path.join(curdir,fileName), "r", encoding='utf8') as fh:
            return fh.read()
    
    def __writeTemplateContent(self, fileName: str, content: str):
        with open(fileName, "w", encoding='utf8') as fh:
            fh.write(content)

    def __buildDependencyGraph(self, taskReport: Any, groups: Any):
        # graph=""
        # for key, group in groupby(sorted(taskReport,key=lambda x:x["feature"]), lambda x: x["feature"]):
        #     keyId = uuid.uuid4().hex
        #     groupList = list(group)
        #     graph += f"subgraph {keyId}[{key}]\n"
        #     for k,v in groups.items():
        #         if any(x["task"].group == k for x in groupList):
        #             graph += f"subgraph {keyId}_{k}[{k}]\n"
        #             for node in v:
        #                 print(f"check node {node}")
        #                 for t in groupList:
        #                     print(f"loop through group, item: {t['task']}")
        #                     if t["task"].id == node:
        #                         graph += f"{node}\n"
        #                         break
        #             graph += f"end\n"
        #     for t in groupList:
        #         task: Task = t["task"]
        #         if task.depends is not None:
        #             for dp in task.depends:
        #                 graph += f"{dp}-->{task.id}[{task.name}]\n"
        #         if task.dependsGroups is not None:
        #             for dp in task.dependsGroups:
        #                 graph += f"{keyId}_{dp}-->{task.id}[{task.name}]\n"
        #         graph += f"{task.id}[{task.name}]\n"
        #     graph += f"end\n"
        # return graph

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
        jsContent = self.__getTemplatePropertyContent('mermaid.min.js')
        template = env.get_template(templateFileName)
        graph = self.__buildDependencyGraph(taskReport,groups)

        output = template.render(
            js=jsContent,
            graph=graph
        )

        self.__writeTemplateContent(fileName,output)

