from av.continuancetable import ContinuanceTable

from healthplan.tier import Tier

class ActuarialValueCalculator:
    def __init__(self, session):
        self._drug_table = None
        self._integrated_table = None
        self._medical_table = None
        self._total_cost = None
        self._moop_cost_level = None
        self.__moop_floor = 0
        self.__separate = None
        self.__session = session
        self.__total_cost = None

    @staticmethod
    def __av_tier(av):
        if av == None:
            tier = None
        else:
            if av > .85:
                tier = Tier.platinum
            elif av > .75:
                tier = Tier.gold
            elif av > .65:
                tier = Tier.silver
            else:
                tier = Tier.bronze
        return tier

    @staticmethod
    def __calculate_moop(deductible, coinsurance, moop):
        if coinsurance == 1:
            moop_level = deductible
        else:
            moop_level = (moop - deductible) / (1 - coinsurance) + deductible
        return moop_level

    def __check_moop(self, healthplan):
        self.__moop_floor = 0
        if self.__separate:
            deduct_sim = healthplan.medical_deductible
            old_av = self.__determine_av(healthplan, deduct_sim, healthplan.drug_deductible)
            deduct_sim -= 10
            while deduct_sim > 0:
                test_av = self.__determine_av(healthplan, deduct_sim, healthplan.drug_deductible)
                if old_av > test_av:
                    self.__moop_floor = self._moop_cost_level
                    old_av = test_av
                    deduct_sim -= 10
                else:
                    deduct_sim -= 990

            deduct_rx_sim = healthplan.drug_deductible
            old_av = self.__determine_av(healthplan, healthplan.medical_deductible, deduct_rx_sim)
            deduct_rx_sim -= 10
            while deduct_rx_sim > 0:
                test_av = self.__determine_av(healthplan, healthplan.medical_deductible, deduct_rx_sim)
                if old_av > test_av:
                    self.__moop_floor = self._moop_cost_level
                    old_av = test_av
                    deduct_rx_sim -= 10
                else:
                    deduct_rx_sim -= 990

    def __determine_av(self, healthplan, medical_deductible, drug_deductible=None):
        self._determine_moop(healthplan, medical_deductible, drug_deductible)
        expenses_before_deductible = self._determine_expenses_before_deductible(medical_deductible)
        coinsurance_expenses = self._determine_coinsurance_expenses(medical_deductible,
                                                                    healthplan, drug_deductible)

        expenses_after_moop = self._determine_expenses_after_moop()
        plan_expenses = expenses_before_deductible + coinsurance_expenses + expenses_after_moop
        return plan_expenses / self._total_cost

    def __determine_coinsurance_expenses_integrated(self, deductible, healthplan):
        coinsurance = healthplan.coinsurance

        coinsurance_slice = self._integrated_table.slice(self.__session, self._moop_cost_level, deductible)[0]

        preventive_slice = self._integrated_table.slice(self.__session,
                                                        self._moop_cost_level,
                                                        deductible,
                                                        columns=['preventive_care_value'])[0]

        amount_subject_to_coinsurance = coinsurance_slice - preventive_slice
        coinsurance_amount = amount_subject_to_coinsurance * coinsurance

        return round(coinsurance_amount + preventive_slice, 2)

    def __determine_coinsurance_expenses_separate(self, medical_deductible, drug_deductible, healthplan):
        coinsurance = healthplan.medical_coinsurance

        coinsurance_slice = self._integrated_table.slice(self.__session, self._moop_cost_level)[0]

        preventive_slice = self._integrated_table.slice(self.__session,
                                                        self._moop_cost_level,
                                                        medical_deductible,
                                                        columns=['preventive_care_value'])[0]

        total_drug_coinsurance_slice = self.__total_drug_costs(drug_deductible)
        medical_deductible = self._medical_table.slice(self.__session, medical_deductible)[0]
        amount_subject_to_coinsurance = coinsurance_slice - preventive_slice - total_drug_coinsurance_slice \
                                        - medical_deductible

        total_drug_slice = self.__total_drug_costs()
        drug_deductible_slice  = self._drug_table.slice(self.__session, drug_deductible)[0]
        if total_drug_slice > drug_deductible_slice:
            drug_coinsurance_amount = (total_drug_slice - drug_deductible_slice) * healthplan.drug_coinsurance
        else:
            drug_coinsurance_amount = 0

        coinsurance_amount = amount_subject_to_coinsurance * coinsurance

        return coinsurance_amount + drug_coinsurance_amount + preventive_slice

    def __total_drug_costs(self, deductible=0):
        drug_fields = ['generic_value', 'preferred_value', 'non_preferred_value', 'specialty_value']
        drug_costs = self._integrated_table.slice(self.__session, self._moop_cost_level, deductible, drug_fields)
        return sum(drug_costs)

    def _determine_coinsurance_expenses(self, medical_deductible, healthplan, drug_deductible=None):
        if self.__separate:
            coinsurance_expenses = self.__determine_coinsurance_expenses_separate(medical_deductible,
                                                                                  drug_deductible,
                                                                                  healthplan)
        else:
            coinsurance_expenses = self.__determine_coinsurance_expenses_integrated(medical_deductible, healthplan)

        return round(coinsurance_expenses, 2)

    def _determine_expenses_after_moop(self):
        return self._integrated_table.avg_cost - self._integrated_table.slice(self.__session, self._moop_cost_level)[0]

    def _determine_expenses_before_deductible(self, deductible):
        return self._medical_table.slice(self.__session, deductible, columns=['preventive_care_value'])[0]

    def _determine_moop(self, healthplan, medical_deductible, drug_deductible=None):
        if self.__separate:
            total_deductible = medical_deductible + drug_deductible
            self._moop_cost_level = self.__calculate_moop(total_deductible,
                                                          healthplan.medical_coinsurance ,
                                                          healthplan.moop)
            if self.__moop_floor > self._moop_cost_level:
                self._moop_cost_level = self.__moop_floor
        else:
            self._moop_cost_level = self.__calculate_moop(medical_deductible, healthplan.coinsurance , healthplan.moop)

    def _determine_total_cost(self):
        self._total_cost = self._integrated_table.avg_cost

    def _set_metal_tier(self, healthplan):
        if healthplan.tier == Tier.na or healthplan.tier == None:
            tier_name = 'Platinum'
        else:
            tier_name = healthplan.tier.name.capitalize()

        self.__separate = (healthplan.medical_deductible != None)

        self._integrated_table = ContinuanceTable.find(self.__session, tier_name + 'Integrated')
        if self.__separate:
            self._medical_table = ContinuanceTable.find(self.__session, tier_name + 'Medical')
            self._drug_table = ContinuanceTable.find(self.__session, tier_name + 'Drug')
        else:
            self._medical_table = self._integrated_table
            self._drug_table = self._integrated_table
        self._determine_total_cost()

    def calculate_av(self, healthplan):
        self._set_metal_tier(healthplan)
        self.__check_moop(healthplan)
        if self.__separate:
            medical_deductible = healthplan.medical_deductible
            drug_deductible = healthplan.drug_deductible
        else:
            medical_deductible = healthplan.deductible
            drug_deductible = None
        test_av = self.__determine_av(healthplan, medical_deductible, drug_deductible)
        test_tier = self.__av_tier(test_av)
        if test_tier == healthplan.tier:
            healthplan.av = round(test_av, 3)
        else:
            healthplan.tier = test_tier
            self._set_metal_tier(healthplan)
            self.__check_moop(healthplan)
            healthplan.av = round(self.__determine_av(healthplan, medical_deductible, drug_deductible), 3)
