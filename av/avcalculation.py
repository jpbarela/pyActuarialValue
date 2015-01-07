import abc

from av.continuancetable import ContinuanceTable

from healthplan.tier import Tier

from lazyproperty.lazyproperty import lazyproperty


class AVCalculation(metaclass=abc.ABCMeta):

    def __init__(self, session, health_plan):
        self._health_plan = health_plan
        self._session = session
        self._set_tier(health_plan.tier)

    def __eq__(self, other):
        return ((self.__class__ == other.__class__) and
                (self._session == other._session) and
                (self._health_plan == other._health_plan))

    @lazyproperty
    def av(self):
        return (self.expenses_below_deductible + self.coinsurance_expenses +
                self.expenses_above_moop) / self.total_cost

    @property
    @abc.abstractmethod
    def coinsurance_expenses(self):
        pass

    @lazyproperty
    def expenses_above_moop(self):
        return (self._integrated_table.avg_cost -
                self._integrated_table.slice(self._session,
                                             self.moop_cost_level)[0])

    @property
    @abc.abstractmethod
    def expenses_below_deductible(self):
        pass

    @property
    @abc.abstractmethod
    def moop_cost_level(self):
        pass

    @property
    def tier(self):
        return self._tier

    @property
    def total_cost(self):
        return self._total_cost

    def _set_tier(self, tier):
        self._tier = tier

        if tier == Tier.na or tier is None:
            tier_name = 'Platinum'
        else:
            tier_name = tier.name.capitalize()

        self._integrated_table = (ContinuanceTable.
                                  find(self._session,
                                       tier_name + 'Integrated'))

        self._total_cost = self._integrated_table.avg_cost
