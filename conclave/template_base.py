import os


class TemplateBase:

    def writeTemplateContent(self, fileName: str, content: str):
        with open(fileName, "w", encoding='utf8') as fh:
            fh.write(content)
    
    def getTemplatePropertyContent(self, fileName: str):
        curdir = os.path.dirname(__file__)
        with open(os.path.join(curdir,fileName), "r", encoding='utf8') as fh:
            return fh.read()