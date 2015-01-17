from nose.tools import assert_almost_equal

import json

from av.continuancetable import ContinuanceTable
from av.database import connection
from av.integratedcalculation import IntegratedCalculation

from healthplan.healthplan import HealthPlan
from healthplan.tier import Tier

global session
session = connection.Session()


def check_av(test_plan_array):
    test_health_plan = create_plan_from_dictionary(test_plan_array[0])

    test_calculation = IntegratedCalculation(session, test_health_plan)
    assert_almost_equal(test_calculation.av,
                        test_plan_array[2],
                        4,
                        "Av is not equal to correct value. Should be {0} is "
                        "{1}".format(test_plan_array[2], test_calculation.av))
    assert test_health_plan.tier == test_plan_array[1], \
        ("Tier does not match expected tier. Expected tier is {0} actual tier"
         " is {1}".format(test_plan_array[1], test_calculation.tier))


def check_coinsurance_expenses(test_plan_array):
    test_plan = HealthPlan()
    test_plan.coinsurance = test_plan_array[2]
    test_plan.deductible = test_plan_array[0]
    test_plan.moop = test_plan_array[1]

    test_calculation = IntegratedCalculation(session, test_plan)
    assert_almost_equal(test_calculation.coinsurance_expenses,
                        test_plan_array[3],
                        2,
                        "Expected expenses for coinsurance are not correct, "
                        "actual {0}, expected {1}".format(
                            test_calculation.coinsurance_expenses,
                            test_plan_array[3]))


def check_expenses_above_moop(test_plan_array):
    test_plan = HealthPlan()
    test_plan.coinsurance = test_plan_array[2]
    test_plan.deductible = test_plan_array[0]
    test_plan.moop = test_plan_array[1]

    test_calculation = IntegratedCalculation(session, test_plan)
    assert_almost_equal(test_calculation.expenses_above_moop,
                        test_plan_array[3],
                        2,
                        "Expected expenses for coinsurance are not correct, "
                        "actual {0}, expected {1}".format(
                            test_calculation.expenses_above_moop,
                            test_plan_array[3]))


def check_expenses_below_deductible(test_deductible_array):
    test_plan = HealthPlan()
    test_plan.coinsurance = 1
    test_plan.deductible = test_deductible_array[0]
    test_calculation = IntegratedCalculation(session, test_plan)

    assert_almost_equal(test_calculation.expenses_below_deductible,
                        test_deductible_array[1],
                        2,
                        "Expected expenses for deductible are not correct, "
                        "actual {0}, expected {1}".format(
                            test_calculation.expenses_below_deductible,
                            test_deductible_array[1]))


def check_set_tier(test_tier_array):
    test_plan = HealthPlan()
    test_plan.coinsurance = 1
    test_plan.tier = test_tier_array[0]
    test_calculation = IntegratedCalculation(session, test_plan)

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


def check_total_cost(test_tier_array):
    test_plan = HealthPlan()
    test_plan.coinsurance = 1
    test_plan.tier = test_tier_array[0]
    test_calculation = IntegratedCalculation(session, test_plan)

    assert_almost_equal(test_calculation.total_cost,
                        test_tier_array[1],
                        2,
                        "Total costs are not correct for tier {0}. Should be "
                        "{1} are {2}".format(test_tier_array[0],
                                             test_tier_array[1],
                                             test_calculation.total_cost))


def create_plan_from_dictionary(plan_dictionary):
    result = HealthPlan()
    result.parse_JSON(json.dumps(plan_dictionary))
    return result


# Test properties
def test_coinsurance_expenses():
    plans = [[0, 500, .9, 2332.96],
             [500, 1000, .8, 1169.82],
             [4500, 6500, .5, 517.31],
             [2000, 2000, 1, 0]]
    for plan in plans:
        check_coinsurance_expenses(plan)


def test_expenses_above_moop():
    plans = [[0, 500, .9, 3967.81],
             [500, 1000, .8, 4689.49],
             [4500, 6500, .5, 3186.90]]
    for plan in plans:
        check_expenses_above_moop(plan)


def test_expenses_below_deductible():
    deductibles = [[0, 0], [500, 18.83], [1000, 45.03]]
    for deductible in deductibles:
        check_expenses_below_deductible(deductible)


def test_moop_cost_level():
    test_plan = HealthPlan()
    test_plan.deductible = 1000
    test_plan.coinsurance = .9
    test_plan.moop = 2000
    test_plan.tier = Tier.platinum

    test_calculation = IntegratedCalculation(session, test_plan)
    print("moop level {0}".format(test_calculation.moop_cost_level))
    assert_almost_equal(test_calculation.moop_cost_level,
                        11372.76,
                        2,
                        ("Integrated plan moop not correct, actual {0}, "
                         "expected {1}".format(test_calculation.
                                               moop_cost_level,
                                               11372.76)))


def test_set_tier():
    tiers = [[Tier.platinum, 'Platinum'], [Tier.gold, 'Gold'],
             [Tier.silver, 'Silver'], [Tier.bronze, 'Bronze'],
             [Tier.na, 'Platinum'], [None, 'Platinum']]
    for tier in tiers:
        check_set_tier(tier)


def test_total_cost():
    test_array = [[Tier.platinum, 6543.47],
                  [Tier.gold, 6088.36],
                  [Tier.silver, 5809.58],
                  [Tier.bronze, 5598.79]]

    for test_tier in test_array:
        check_total_cost(test_tier)


# Test complete calculations
def test_av_for_basic_integrated_plans():
    test_plans = [[{'deductible': 500,
                    'coinsurance': .9,
                    'moop': 1000,
                    'tier': 'platinum'},
                   Tier.platinum, .9065],
                  [{'deductible': 500,
                    'coinsurance': .8,
                    'moop': 4500,
                    'tier': 'gold'},
                   Tier.gold, .8164],
                  [{'deductible': 3500,
                    'coinsurance': 1,
                    'moop': 3500,
                    'tier': 'silver'},
                   Tier.silver, .7116],
                  [{'deductible': 3000,
                    'coinsurance': .5,
                    'moop': 6850,
                    'tier': 'bronze'},
                   Tier.bronze, .6175]]
    for test_plan in test_plans:
        check_av(test_plan)
