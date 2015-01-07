import av
from av.avcalculation import AVCalculation

from lazyproperty.lazyproperty import lazyproperty


class IntegratedCalculation(AVCalculation):

    def __init__(self, session, health_plan):
        super().__init__(session, health_plan)
        self._deductible = self._health_plan.deductible
        self._effective_coinsurance = self._determine_effective_coinsurance()

    @lazyproperty
    def coinsurance_expenses(self):

        coinsurance = self._health_plan.coinsurance

        coinsurance_slice = (self._integrated_table.
                             slice(self._session,
                                   self.moop_cost_level,
                                   self._deductible)[0])

        preventive_slice = (self._integrated_table.
                            slice(self._session,
                                  self.moop_cost_level,
                                  self._deductible,
                                  columns=['preventive_care_value'])[0])

        amount_subject_to_coinsurance = coinsurance_slice - preventive_slice
        coinsurance_amount = amount_subject_to_coinsurance * coinsurance

        return round(coinsurance_amount + preventive_slice, 2)

    @lazyproperty
    def expenses_below_deductible(self):
        return (self._integrated_table.
                slice(self._session,
                      self._deductible,
                      columns=['preventive_care_value'])[0])

    @lazyproperty
    def moop_cost_level(self):
        if self._effective_coinsurance == 1:
            moop = self._deductible
        else:
            moop = ((self._health_plan.moop - self._deductible) /
                    (1 - self._effective_coinsurance) + self._deductible)
        return moop

    def _determine_effective_coinsurance(self):
        preventive_costs = self._integrated_table.slice(
            self._session,
            av.MAX_VALUE,
            columns=['preventive_care_value'])[0]

        subject_to_coinsurance = self.total_cost - preventive_costs

        return ((subject_to_coinsurance * self._health_plan.coinsurance
                 + preventive_costs) /
                self._total_cost)
