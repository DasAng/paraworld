from .feedback_schema import ScenarioFeedback, StepFeedback

class FeedbackAdapter:

    def __init__(self):
        raise NotImplementedError

    def onNotifyScenario(self,schema: ScenarioFeedback):
        raise NotImplementedError
    
    def onNotifyStep(self,schema: StepFeedback):
        raise NotImplementedError


class NullFeedbackAdapter(FeedbackAdapter):

    def __init__(self):
        pass

    def onNotifyScenario(self,schema: ScenarioFeedback):
        print(f"scenario: {schema}")
    
    def onNotifyStep(self,schema: StepFeedback):
        print(f"step: {schema}")