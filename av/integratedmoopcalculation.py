import av
from av.avcalculation import AVCalculation
from av.continuancetable import ContinuanceTable

from healthplan.tier import Tier

from lazyproperty.lazyproperty import lazyproperty


class IntegratedMOOPCalculation(AVCalculation):

    def __init__(self, session, health_plan):
        super().__init__(session, health_plan)
        self._medical_deductible = self._health_plan.medical_deductible
        self._drug_deductible = self._health_plan.drug_deductible
        self._check_moop()

    @lazyproperty
    def expenses_below_deductible(self):
        return self._determine_expenses_below_deductible(
            self._health_plan.medical_deductible)

    @lazyproperty
    def coinsurance_expenses(self):
        self._determine_moop(self._medical_deductible, self._drug_deductible)
        return self._determine_coinsurance_expenses(
            self._medical_deductible,
            self._drug_deductible)

    @lazyproperty
    def effective_coinsurance(self):
        preventive_costs = self._integrated_table.slice(
            self._session,
            av.MAX_VALUE,
            columns=['preventive_care_value'])[0]

        drug_expense_subject_to_coinsurance = (
            sum(self._integrated_table.slice(self._session,
                                             av.MAX_VALUE,
                                             columns=av.DRUG_FIELDS)) +
            av.DRUG_BALANCE_ADJUSTMENT)
        medical_expense_subject_to_coinsurance = (
            self._total_cost -
            preventive_costs -
            drug_expense_subject_to_coinsurance)

        return ((medical_expense_subject_to_coinsurance *
                 self._health_plan.medical_coinsurance +
                 drug_expense_subject_to_coinsurance *
                 self._health_plan.drug_coinsurance + preventive_costs) /
                self.total_cost)

    @property
    def moop_cost_level(self):
        self._determine_moop(self._medical_deductible, self._drug_deductible)
        return self._moop_cost_level

    def _check_moop(self):
        self._moop_floor = 0

        deduct_sim = self._health_plan.medical_deductible
        if deduct_sim > 0:
            old_av = self._determine_av(deduct_sim,
                                        self._health_plan.drug_deductible)

            if deduct_sim >= 10:
                deduct_sim -= 10
            else:
                deduct_sim = 0

            while deduct_sim > 0:
                test_av = self._determine_av(deduct_sim,
                                             self._health_plan.drug_deductible)
                if old_av > test_av:
                    self._moop_floor = self._moop_cost_level
                    old_av = test_av
                    if deduct_sim >= 10:
                        deduct_sim -= 10
                    else:
                        deduct_sim = 0
                else:
                    if deduct_sim >= 1000:
                        deduct_sim -= 990
                        break
                    else:
                        deduct_sim = 0

            test_av = self._determine_av(deduct_sim,
                                         self._health_plan.drug_deductible)
            if old_av > test_av:
                self._moop_floor = self._moop_cost_level

        deduct_rx_sim = self._health_plan.drug_deductible
        if deduct_rx_sim > 0:
            old_av = self._determine_av(deduct_sim,
                                        deduct_rx_sim)
            if deduct_rx_sim > 10:
                deduct_rx_sim -= 10
            else:
                deduct_rx_sim = 0

            while deduct_rx_sim > 0:
                test_av = self._determine_av(deduct_sim,
                                             deduct_rx_sim)
                if old_av > test_av:
                    self._moop_floor = self._moop_cost_level
                    old_av = test_av
                    if deduct_rx_sim > 10:
                        deduct_rx_sim -= 10
                    else:
                        deduct_rx_sim = 0
                        test_av = self._determine_av(deduct_sim,
                                                     deduct_rx_sim)
                        if old_av > test_av:
                            self._moop_floor = self._moop_cost_level
                else:
                    if deduct_rx_sim > 1000:
                        break
                    else:
                        deduct_rx_sim = 0

    def _determine_av(self, medical_deductible, drug_deductible):
        self._determine_moop(medical_deductible, drug_deductible)
        expenses_before_deductible = (
            self._determine_expenses_below_deductible(medical_deductible)
        )
        coinsurance_expenses = (
            self._determine_coinsurance_expenses(medical_deductible,
                                                 drug_deductible))
        plan_expenses = (expenses_before_deductible +
                         coinsurance_expenses +
                         self._determine_expenses_above_moop())
        return plan_expenses / self._total_cost

    def _determine_coinsurance_expenses(self,
                                        medical_deductible,
                                        drug_deductible):

        coinsurance_slice = (self._integrated_table.
                             slice(self._session,
                                   self._moop_cost_level)[0])

        medical_deductible_amount = (self._medical_table.
                                     slice(self._session,
                                           medical_deductible)[0])

        drug_deductible_amount = (self._drug_table.slice(self._session,
                                                         drug_deductible)[0])

        effective_deductible = (self._integrated_table.
                                inverse(self._session,
                                        medical_deductible_amount +
                                        drug_deductible_amount))

        preventive_slice = (self._integrated_table.
                            slice(self._session,
                                  self._moop_cost_level,
                                  effective_deductible,
                                  columns=['preventive_care_value'])[0])

        total_drug_coinsurance_slice = self._total_drug_costs()

        amount_subject_to_coinsurance = (coinsurance_slice -
                                         preventive_slice -
                                         total_drug_coinsurance_slice -
                                         medical_deductible_amount)

        drug_coinsurance_amount = (self.
                                   _total_drug_costs(effective_deductible) *
                                   self._health_plan.drug_coinsurance)

        coinsurance_amount = (amount_subject_to_coinsurance *
                              self.effective_coinsurance)

        return coinsurance_amount + drug_coinsurance_amount + preventive_slice

    def _determine_expenses_above_moop(self):
        return (self._integrated_table.avg_cost -
                self._integrated_table.slice(self._session,
                                             self._moop_cost_level)[0])

    def _determine_expenses_below_deductible(self, medical_deductible):
        return self._medical_table.slice(self._session,
                                         medical_deductible,
                                         columns=['preventive_care_value'])[0]

    def _determine_moop(self,
                        medical_deductible,
                        drug_deductible):
        total_deductible = medical_deductible + drug_deductible

        if self.effective_coinsurance == 1:
            self._moop_cost_level = total_deductible
        else:
            self._moop_cost_level = (((self._health_plan.moop -
                                       total_deductible) /
                                      (1 - self.effective_coinsurance)) +
                                     total_deductible)

        if self._moop_floor > self._moop_cost_level:
            self._moop_cost_level = self._moop_floor

    def _set_tier(self, tier):
        super()._set_tier(tier)

        if tier == Tier.na or tier is None:
            tier_name = 'Platinum'
        else:
            tier_name = tier.name.capitalize()

        self._medical_table = (ContinuanceTable.find(self._session,
                                                     tier_name + 'Medical'))

        self._drug_table = (ContinuanceTable.find(self._session,
                                                  tier_name + 'Drug'))

    def _total_drug_costs(self, drug_deductible=0):
        drug_costs = self._integrated_table.slice(self._session,
                                                  self._moop_cost_level,
                                                  drug_deductible,
                                                  av.DRUG_FIELDS)
        return sum(drug_costs)
