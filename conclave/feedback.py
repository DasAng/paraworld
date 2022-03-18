from dataclasses import asdict
from multiprocessing import Process
import multiprocessing
import os
import time
import queue
from typing import Any

from .feedback_schema import BaseFeedback, ScenarioFeedback, StepFeedback
from .feedback_adapter import FeedbackAdapter

class Feedback:

    def __init__(self) -> None:
        self.messageQueue = multiprocessing.Manager().Queue()
        self.adapters: list[FeedbackAdapter] = []
        self.process = Process(daemon=True,target=self.runFeedback, args=(self.messageQueue,))

    def runFeedback(self,q: multiprocessing.Queue):
        selfPid = os.getpid()
        while True:
            try:
                msg = q.get(block=True)
                #print(f"message recv: {msg}")
                if msg == "STOP":
                    break
                else:
                    for adapter in self.adapters:
                        fb = asdict(BaseFeedback())
                        fb = BaseFeedback(**{k:(msg[k] if k in msg else v) for k,v in fb.items()})
                        if fb.type == "ScenarioFeedback":
                            sfb = asdict(ScenarioFeedback())
                            sfb = ScenarioFeedback(**{k:(msg[k] if k in msg else v) for k,v in sfb.items()})
                            try:
                                adapter.onNotifyScenario(sfb)
                            except Exception as e:
                                print(f"notify feedback failed: {e}")
                        elif fb.type == "StepFeedback":
                            sfb = asdict(StepFeedback())
                            sfb = StepFeedback(**{k:(msg[k] if k in msg else v) for k,v in sfb.items()})
                            try:
                                adapter.onNotifyStep(sfb)
                            except Exception as e:
                                print(f"notify feedback failed: {e}")
            except queue.Empty:
                pass

    def startFeedback(self):
        self.process.start()
    
    def stopFeedback(self):
        self.messageQueue.put_nowait("STOP")
        self.process.join(timeout=120)
    
    def notify(self, msg: Any):
        try:
            self.messageQueue.put_nowait(msg)
        except Exception as e:
            pass
    
    def addAdapter(self,adapter: FeedbackAdapter):
        self.adapters.append(adapter)
    
