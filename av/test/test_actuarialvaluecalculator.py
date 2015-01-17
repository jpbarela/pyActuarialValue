import json

from av.actuarialvaluecalculator import ActuarialValueCalculator
from av.integratedcalculation import IntegratedCalculation
from av.integratedmoopcalculation import IntegratedMOOPCalculation
from av.separatecalculation import SeparateCalculation
from av.database import connection

from healthplan.healthplan import HealthPlan

global session
session = connection.Session()

global calc
calc = ActuarialValueCalculator(session)


def create_health_plan(json_dictionary):
    result_plan = HealthPlan()
    result_plan.parse_JSON(json.dumps(json_dictionary))
    return result_plan


def test_calculate_av_integrated():
    test_plan = create_health_plan({'deductible': 500,
                                    'coinsurance': .9,
                                    'moop': 1000})
    test_calculation = calc.calculate_av(test_plan)
    actual_calculation = IntegratedCalculation(session, test_plan)
    assert test_calculation == actual_calculation, \
        "Integrated calculation is not correct"


def test_calculate_av_integrated_moop():
    test_plan = create_health_plan({'moop': 1000,
                                    'medical': {'deductible': 500,
                                                'coinsurance': .9},
                                    'drug': {'deductible': 0,
                                             'coinsurance': .9}})
    test_calculation = calc.calculate_av(test_plan)
    actual_calculation = IntegratedMOOPCalculation(session, test_plan)
    assert test_calculation == actual_calculation, \
        "Integrated MOOP calculation is not correct"


def test_calculate_av_separate():
    test_plan = create_health_plan({'medical': {'deductible': 500,
                                                'coinsurance': .9,
                                                'moop': 1000},
                                    'drug': {'deductible': 0,
                                             'coinsurance': .9,
                                             'moop': 250}})
    test_calculation = calc.calculate_av(test_plan)
    actual_calculation = SeparateCalculation(session, test_plan)
    assert test_calculation == actual_calculation, \
        "Separate calculation is not correct"
