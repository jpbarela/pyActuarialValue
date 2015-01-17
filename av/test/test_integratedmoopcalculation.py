from nose.tools import assert_almost_equal

import json

from healthplan.healthplan import HealthPlan
from healthplan.tier import Tier

from av.continuancetable import ContinuanceTable
from av.database import connection
from av.integratedmoopcalculation import IntegratedMOOPCalculation

global session
session = connection.Session()


def check_av(test_plan_array):
    test_health_plan = create_plan_from_dictionary(test_plan_array[0])

    test_calculation = IntegratedMOOPCalculation(session, test_health_plan)
    assert_almost_equal(test_calculation.av,
                        test_plan_array[2],
                        4,
                        "Av is not equal to correct value. Should be {0} is "
                        "{1}".format(test_plan_array[2], test_calculation.av))
    assert test_health_plan.tier == test_plan_array[1], \
        ("Tier does not match expected tier. Expected tier is {0} actual tier"
         " is {1}".format(test_plan_array[1], test_calculation.tier))


def check_coinsurance_expenses(test_plan_array):
    test_health_plan = create_plan_from_dictionary(test_plan_array[0])

    test_calculation = IntegratedMOOPCalculation(session, test_health_plan)
    assert_almost_equal(test_calculation.coinsurance_expenses,
                        test_plan_array[1],
                        2,
                        "Coinsurance expense is not correct. Should be {0} is "
                        "{1}".format(test_plan_array[1],
                                     test_calculation.coinsurance_expenses))


def check_expenses_below_deductible(test_deductible_array):
    test_plan = HealthPlan()
    test_plan.drug_coinsurance = 1
    test_plan.medical_coinsurance = 1
    test_plan.medical_deductible = test_deductible_array[0]
    test_plan.drug_deductible = 0
    test_calculation = IntegratedMOOPCalculation(session, test_plan)

    assert_almost_equal(test_calculation.expenses_below_deductible,
                        test_deductible_array[1],
                        2,
                        "Expected expenses for deductible are not correct, "
                        "actual {0}, expected {1}".format(
                            test_calculation.expenses_below_deductible,
                            test_deductible_array[1]))


def check_moop_cost_level(test_moop_level):
    test_health_plan = create_plan_from_dictionary(test_moop_level[0])

    test_calculation = IntegratedMOOPCalculation(session, test_health_plan)
    assert_almost_equal(test_calculation.moop_cost_level,
                        test_moop_level[1],
                        2,
                        "Coinsurance expense is not correct. Should be {0} is "
                        "{1}".format(test_moop_level[1],
                                     test_calculation.moop_cost_level))


def check_set_tier(test_tier_array):
    test_plan = HealthPlan()
    test_plan.coinsurance = 1
    test_plan.medical_deductible = 0
    test_plan.drug_deductible = 0
    test_plan.tier = test_tier_array[0]
    test_calculation = IntegratedMOOPCalculation(session, test_plan)

    if test_tier_array[0] is not None:
        assert test_calculation.tier == test_tier_array[0], \
            ("Calculation tier not set correctly. Should be {0} is {1}".
             format(test_tier_array[0], test_calculation.tier))

    integrated_table = ContinuanceTable.find(session,
                                             test_tier_array[1] + 'Integrated')
    assert test_calculation._integrated_table == integrated_table, \
        "Integrated Table is not correct for tier {0}, actual {1} expected " \
        "{2}".format(test_tier_array[0],
                     test_calculation._integrated_table,
                     integrated_table)

    medical_table = ContinuanceTable.find(session,
                                          test_tier_array[1] + 'Medical')
    assert test_calculation._medical_table == medical_table, \
        "Medical Table is not correct for tier {0}, actual {1} expected " \
        "{2}".format(test_tier_array[0],
                     test_calculation._medical_table,
                     medical_table)

    drug_table = ContinuanceTable.find(session,
                                       test_tier_array[1] + 'Drug')
    assert test_calculation._drug_table == drug_table, \
        "Drug Table is not correct for tier {0}, actual {1} expected " \
        "{2}".format(test_tier_array[0],
                     test_calculation._drug_table,
                     drug_table)


def create_plan_from_dictionary(plan_dictionary):
    result = HealthPlan()
    result.parse_JSON(json.dumps(plan_dictionary))
    return result


# Test properties
def test_coinsurance_expenses():
    test_plans = [[{'moop': 1500,
                    'medical': {'deductible': 750, 'coinsurance': 0.9},
                    'drug': {'deductible': 0, 'coinsurance': 1}},
                   2928.39],
                  [{'moop': 2500,
                    'medical': {'deductible': 1000, 'coinsurance': 0.9},
                    'drug': {'deductible': 500, 'coinsurance': 1}},
                   4034.70],
                  [{'moop': 5000,
                    'medical': {'deductible': 2000, 'coinsurance': 0.8},
                    'drug': {'deductible': 500, 'coinsurance': 0.9}},
                   2589.07]]
    for plan in test_plans:
        check_coinsurance_expenses(plan)


def test_expenses_below_deductible():
    deductibles = [[0, 0], [500, 25.17], [1000, 57.91]]
    for deductible in deductibles:
        check_expenses_below_deductible(deductible)


def test_moop_cost_level():
    test_plans = [[{'moop': 750,
                    'medical': {'deductible': 750, 'coinsurance': 1},
                    'drug': {'deductible': 0, 'coinsurance': 1}},
                   750],
                  [{'moop': 1500,
                    'medical': {'deductible': 750, 'coinsurance': 0.9},
                    'drug': {'deductible': 0, 'coinsurance': 1}},
                   10747.33],
                  [{'moop': 2500,
                    'medical': {'deductible': 1000, 'coinsurance': 0.9},
                    'drug': {'deductible': 500, 'coinsurance': 1}},
                   28392.54],
                  [{'moop': 5000,
                    'medical': {'deductible': 2000, 'coinsurance': 0.8},
                    'drug': {'deductible': 500, 'coinsurance': 0.9}},
                   17083.52]]

    for plan in test_plans:
        check_moop_cost_level(plan)


def test_set_tier():
    tiers = [[Tier.platinum, 'Platinum'], [Tier.gold, 'Gold'],
             [Tier.silver, 'Silver'], [Tier.bronze, 'Bronze'],
             [Tier.na, 'Platinum'], [None, 'Platinum']]
    for tier in tiers:
        check_set_tier(tier)


# Test complete calculations
def test_av_for_separate_deductible_only():
    test_plans = [[{'moop': 750,
                    'medical': {'deductible': 750, 'coinsurance': 1},
                    'drug': {'deductible': 0, 'coinsurance': 1},
                    'tier': 'platinum'},
                   Tier.platinum, .9148],
                  [{'moop': 2500,
                    'medical': {'deductible': 2500, 'coinsurance': 1},
                    'drug': {'deductible': 0, 'coinsurance': 1},
                    'tier': 'gold'},
                   Tier.gold, .7851],
                  [{'moop': 4750,
                    'medical': {'deductible': 4750, 'coinsurance': 1},
                    'drug': {'deductible': 0, 'coinsurance': 1},
                    'tier': 'silver'},
                   Tier.silver, .6834]]
    for test_plan in test_plans:
        check_av(test_plan)


def test_calculate_av_for_plans_with_different_deductibles():
    test_plans = [[{'moop': 1000,
                    'medical': {'deductible': 500, 'coinsurance': .9},
                    'drug': {'deductible': 400, 'coinsurance': 1},
                    'tier': 'platinum'},
                   Tier.platinum, .9060],
                  [{'moop': 2500,
                    'medical': {'deductible': 1500, 'coinsurance': .8},
                    'drug': {'deductible': 750, 'coinsurance': 1},
                    'tier': 'gold'},
                  Tier.gold, .7945],
                  [{'moop': 5000,
                    'medical': {'deductible': 2750, 'coinsurance': .7},
                    'drug': {'deductible': 400, 'coinsurance': .8},
                    'tier': 'silver'},
                   Tier.silver, .6978],
                  [{'moop': 6850,
                    'medical': {'deductible': 5000, 'coinsurance': .5},
                    'drug': {'deductible': 2500, 'coinsurance': .7},
                    'tier': 'bronze'},
                   Tier.bronze, .5931]]
    for test_plan in test_plans:
        check_av(test_plan)


def test_calculate_av_for_basic_separate_plans():
    test_plans = [[{'moop': 1000,
                    'medical': {'deductible': 500, 'coinsurance': .9},
                    'drug': {'deductible': 0, 'coinsurance': 1},
                    'tier': 'platinum'},
                   Tier.platinum, .9173],
                  [{'moop': 3500,
                    'medical': {'deductible': 1500, 'coinsurance': .8},
                    'drug': {'deductible': 0, 'coinsurance': 1},
                    'tier': 'gold'},
                   Tier.gold, .8013],
                  [{'moop': 5000,
                    'medical': {'deductible': 3500, 'coinsurance': .7},
                    'drug': {'deductible': 0, 'coinsurance': 1},
                    'tier': 'silver'},
                   Tier.silver, .6996]]
    for test_plan in test_plans:
        check_av(test_plan)
