from av.avcalculation import AVCalculation


class IntegratedMOOPCalculation(AVCalculation):

    def __init__(self, session, health_plan):
        AVCalculation.__init__(self, session, health_plan)
