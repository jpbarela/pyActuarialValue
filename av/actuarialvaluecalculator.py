from av.integratedcalculation import IntegratedCalculation
from av.integratedmoopcalculation import IntegratedMOOPCalculation
from av.separatecalculation import SeparateCalculation


class ActuarialValueCalculator:
    def __init__(self, session):
        self.__session = session

    def calculate_av(self, health_plan):
        if health_plan.medical_deductible is not None:
            if health_plan.medical_moop is not None:
                return SeparateCalculation(self.__session, health_plan)
            else:
                return IntegratedMOOPCalculation(self.__session, health_plan)
        else:
            return IntegratedCalculation(self.__session, health_plan)
