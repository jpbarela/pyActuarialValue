from av.avcalculation import AVCalculation


class IntegratedMOOPCalculation(AVCalculation):

    def expenses_below_deductible(self, deductible):
        return 0

    @property
    def coinsurance_expenses(self):
        return 0

    @property
    def moop_cost_level(self):
        return self._health_plan.moop
