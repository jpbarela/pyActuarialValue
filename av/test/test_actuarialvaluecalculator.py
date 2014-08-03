from nose.tools import assert_almost_equal

import json

from av.actuarialvaluecalculator import ActuarialValueCalculator
from av.continuancetable import ContinuanceTable
from av.database import connection

from healthplan.healthplan import HealthPlan
from healthplan.tier import Tier

global session
session = connection.Session()

global calc
calc = ActuarialValueCalculator(session)

def check_determine_coinsurance_expenses_integrated(test_plan_array):
    test_plan = HealthPlan()
    test_plan.coinsurance = test_plan_array[2]
    test_plan.deductible = test_plan_array[0]
    test_plan.moop = test_plan_array[1]

    calc._determine_moop(test_plan, test_plan.deductible)
    coinsurance = calc._determine_coinsurance_expenses(test_plan.deductible, test_plan)
    assert_almost_equal(coinsurance,
                        test_plan_array[3],
                        2,
                        "Expected expenses for coinsurance are not correct, actual {0}, expected {1}".format(
                            coinsurance, test_plan_array[3]))

def check_determine_coinsurance_expenses_separate(test_plan_array):
    print(test_plan_array[0])
    test_plan = create_plan_from_hash(test_plan_array[0])

    calc._determine_moop(test_plan, test_plan.medical_deductible, test_plan.drug_deductible)
    coinsurance = calc._determine_coinsurance_expenses(test_plan.medical_deductible,
                                                       test_plan,
                                                       test_plan.drug_deductible)
    assert_almost_equal(coinsurance,
                        test_plan_array[1],
                        2,
                        "Expected expenses for coinsurance are not correct, actual {0}, expected {1}".format(
                            coinsurance, test_plan_array[1]))


def check_determine_expenses_after_moop(test_plan_array):
    test_plan = HealthPlan()
    test_plan.coinsurance = test_plan_array[2]
    test_plan.deductible = test_plan_array[0]
    test_plan.moop = test_plan_array[1]

    calc._determine_moop(test_plan, test_plan.deductible)
    calc._determine_coinsurance_expenses(test_plan.deductible, test_plan)
    after_moop_exepenses =calc._determine_expenses_after_moop()
    assert_almost_equal(after_moop_exepenses,
                        test_plan_array[3],
                        2,
                        "Expected expenses after moop are not correct, actual {0}, expected {1}".format(
                            after_moop_exepenses, test_plan_array[3]))

def check_determine_expenses_before_deductible(test_deductible_array):
    expenses = calc._determine_expenses_before_deductible(test_deductible_array[0])
    assert_almost_equal(expenses,
                        test_deductible_array[1],
                        2,
                        "Expected expenses for deductible are not correct, actual {0}, expected {1}".format(
                            expenses,
                            test_deductible_array[1]))

def check_health_plan(health_plan_array):
    test_health_plan = create_plan_from_hash(health_plan_array[0])
    calc.calculate_av(test_health_plan)
    assert_almost_equal(test_health_plan.av,
                        health_plan_array[2],
                        3,
                        "Av is not equal to correct value. Should be {0} is {1}".format(health_plan_array[2],test_health_plan.av))
    assert test_health_plan.tier == health_plan_array[1],\
        "Tier does not match expected tier. Expected tier is {0} actual tier is {1}".format(health_plan_array[1], test_health_plan.tier)

def check_set_tier_integrated(test_tier_array):
    test_health_plan = create_plan(test_tier_array[0], separate=False)

    calc._set_metal_tier(test_health_plan)
    integrated_table = ContinuanceTable.find(session, test_tier_array[1] + 'Integrated')
    medical_table = integrated_table
    assert calc._integrated_table == integrated_table, \
        "Integrated Table is not correct for tier {0}, actual {1} expected {2}".format(test_tier_array[0],
                                                                                       calc._integrated_table,
                                                                                       integrated_table)
    assert calc._medical_table == medical_table, \
        "Medical Table is not correct for tier {0}, actual {1} expected {2}".format(test_tier_array[0],
                                                                                    calc._medical_table,
                                                                                    medical_table)

def check_set_tier_separate(test_tier_array):
    test_health_plan = create_plan(test_tier_array[0], separate=True)

    calc._set_metal_tier(test_health_plan)
    integrated_table = ContinuanceTable.find(session, test_tier_array[1] + 'Integrated')
    medical_table = ContinuanceTable.find(session, test_tier_array[1] + 'Medical')
    assert calc._integrated_table == integrated_table, \
        "Integrated Table is not correct for tier {0}, actual {1} expected {2}".format(test_tier_array[0],
                                                                                       calc._integrated_table,
                                                                                       integrated_table)
    assert calc._medical_table == medical_table, \
        "Medical Table is not correct for tier {0}, actual {1} expected {2}".format(test_tier_array[0],
                                                                                   calc._integrated_table,
                                                                                   medical_table)

def create_plan_from_hash(plan_hash):
    result = HealthPlan()
    result.parse_JSON(json.dumps(plan_hash))
    return result

def create_plan(tier, separate=False):
    plan = HealthPlan()
    plan.tier = tier
    if separate:
        plan.medical_deductible = 500
    else:
        plan.deductible = 500
    return plan

#test private methods
def test__determine_coinsurance_expenses_integrated():
    test_plan = create_plan(Tier.platinum, separate=False)

    calc._set_metal_tier(test_plan)
    plans = [[0, 500, .9, 2174.62], [500, 1000, .8, 1089.09], [4500, 6500, .5, 451.58]]
    for plan in plans:
        check_determine_coinsurance_expenses_integrated(plan)

def test__determine_coinsurance_expenses_separate():
    test_plan = create_plan(Tier.platinum, separate=True)

    calc._set_metal_tier(test_plan)
    plans = [[{'moop':500,
               'medical': {'deductible': 0, 'coinsurance': .9},
               'drug': {'deductible': 0, 'coinsurance': 1}}, 2216.35],
             [{'moop':1000,
               'medical': {'deductible': 500, 'coinsurance': .8},
               'drug': {'deductible': 0, 'coinsurance': 1}}, 1158.71],
             [{'moop':6500,
               'medical': {'deductible': 4500, 'coinsurance': .5},
               'drug': {'deductible': 0, 'coinsurance': 1}}, 952.27],
            [{'moop':1500,
               'medical': {'deductible': 750, 'coinsurance': .9},
               'drug': {'deductible': 250, 'coinsurance': .8}},1758.77],
            [{'moop':2500,
               'medical': {'deductible': 1000, 'coinsurance': .8},
               'drug': {'deductible': 250, 'coinsurance': .9}}, 1786.28]]
    for plan in plans:
        check_determine_coinsurance_expenses_separate(plan)

def test__determine_expenses_after_moop():
    test_plan = create_plan(Tier.platinum)

    calc._set_metal_tier(test_plan)
    plans = [[0, 500, .9, 3403.23], [500, 1000, .8, 4053.40], [4500, 6500, .5, 2676.77]]
    for plan in plans:
        check_determine_expenses_after_moop(plan)

def test__determine_expenses_before_deductible_integrated():
    test_plan = create_plan(Tier.platinum, separate=False)

    calc._set_metal_tier(test_plan)
    deductibles = [[0,0], [500,19.79], [1000,44.77]]
    for deductible in deductibles:
        check_determine_expenses_before_deductible(deductible)

def test__determine_expenses_before_deductible_separate():
    test_plan = create_plan(Tier.platinum, separate=True)

    calc._set_metal_tier(test_plan)
    deductibles = [[0,0], [500,26.36], [1000,57.02]]
    for deductible in deductibles:
        check_determine_expenses_before_deductible(deductible)

def test__determine_moop_integrated():
    test_plan = HealthPlan()
    test_plan.deductible = 1000
    test_plan.coinsurance = .9
    test_plan.moop = 2000

    calc._set_metal_tier(test_plan)
    calc._determine_moop(test_plan, test_plan.deductible)
    assert_almost_equal(calc._moop_cost_level,
                        11000,
                        0,
                        "Integrated plan moop not correct, actual {0}, expected {1}".format(calc._moop_cost_level,
                                                                                            11000))

def test__determine_moop_separate():
    test_plan = HealthPlan()
    test_plan.medical_deductible = 500
    test_plan.medical_coinsurance = .8
    test_plan.drug_deductible = 500
    test_plan.moop = 2000

    calc._set_metal_tier(test_plan)
    calc._determine_moop(test_plan, test_plan.medical_deductible, test_plan.drug_deductible)
    assert_almost_equal(calc._moop_cost_level,
                        6000,
                        0,
                        "Seperate plan moop not correct, actual {0}, expected {1}".format(calc._moop_cost_level,
                                                                                            6000))

def test__determine_moop_floor():
    test_plan = HealthPlan()
    test_plan.medical_deductible = 500
    test_plan.medical_coinsurance = .8
    test_plan.drug_deductible = 500
    test_plan.moop = 2000
    calc._set_metal_tier(test_plan)
    calc._ActuarialValueCalculator__moop_floor = 9000

    calc._determine_moop(test_plan, test_plan.medical_deductible, test_plan.drug_deductible)
    assert_almost_equal(calc._moop_cost_level,
                        9000,
                        0,
                        "Integrated plan moop not correct, actual {0}, expected {1}".format(calc._moop_cost_level,
                                                                                            9000))

def test__determine_total_costs():
    test_plan = create_plan(Tier.platinum)
    calc._set_metal_tier(test_plan)
    calc._determine_total_cost()
    assert_almost_equal(calc._total_cost,
                        5804.27,
                        2,
                        'Platinum costs are not correct')

    test_plan.tier = Tier.bronze
    calc._set_metal_tier(test_plan)
    calc._determine_total_cost()
    assert_almost_equal(calc._total_cost,
                        4976.71,
                        2,
                        'Bronze costs are not correct')

def test__set_tier_integrated():
    tiers = [[Tier.platinum, 'Platinum'], [Tier.gold, 'Gold'], [Tier.silver, 'Silver'], [Tier.bronze, 'Bronze'],
             [Tier.na, 'Platinum'], [None, 'Platinum']]
    for tier in tiers:
        check_set_tier_integrated(tier)

def test__set_tier_separate():
    tiers = [[Tier.platinum, 'Platinum'], [Tier.gold, 'Gold'], [Tier.silver, 'Silver'], [Tier.bronze, 'Bronze'],
             [Tier.na, 'Platinum'], [None, 'Platinum']]
    for tier in tiers:
        check_set_tier_separate(tier)

#test public methods
def test_calculate_av_for_basic_integrated_plans():
    test_plans = [
        [{"deductible": 500,  "coinsurance": .9, "moop":1000}, Tier.platinum, .898],
        [{"deductible": 500,  "coinsurance": .8, "moop":3500}, Tier.gold, .819],
        [{"deductible": 3000, "coinsurance": 1,  "moop":3000}, Tier.silver, .717],
        [{"deductible": 2500, "coinsurance": .5, "moop":6500}, Tier.bronze, .613]
    ]
    for test_plan in test_plans:
        check_health_plan(test_plan)

def test_calculate_av_for_basic_separate_plans():
    test_plans = [
        [{'moop':800,
          'medical': {'deductible': 500, 'coinsurance': .9},
          'drug': {'deductible': 0, 'coinsurance': 1}},
         Tier.platinum, .918],
        [{'moop':3500,
          'medical': {'deductible': 1000, 'coinsurance': .8},
          'drug': {'deductible': 0, 'coinsurance': 1}},
         Tier.gold, .819],
        [{'moop':5000,
          'medical': {'deductible': 3500, 'coinsurance': .7},
          'drug': {'deductible': 0, 'coinsurance': 1}},
         Tier.silver, .717]
    ]
    for test_plan in test_plans:
        check_health_plan(test_plan)

def test_calculate_av_for_plans_with_different_deductibles():
    test_plans = [
        [{'moop':1000,
          'medical': {'deductible': 500, 'coinsurance': .9},
          'drug': {'deductible': 400, 'coinsurance': 1}},
         Tier.platinum, .892],
        [{'moop':2500,
          'medical': {'deductible': 1500, 'coinsurance': .8},
          'drug': {'deductible': 750, 'coinsurance': 1}},
         Tier.gold, .785],
        [{'moop':5000,
          'medical': {'deductible': 2750, 'coinsurance': .7},
          'drug': {'deductible': 400, 'coinsurance': .8}},
         Tier.silver, .683],
        [{'moop':6500,
          'medical': {'deductible': 4000, 'coinsurance': .5},
          'drug': {'deductible': 750, 'coinsurance': .7}},
         Tier.bronze, .620]
    ]
    for test_plan in test_plans:
        check_health_plan(test_plan)

def test_calculate_av_for_separate_deductible_only():
    test_plans = [
        [{'moop':750,
          'medical': {'deductible': 750, 'coinsurance': 1},
          'drug': {'deductible': 0, 'coinsurance': 1}},
         Tier.platinum, .913],
        [{'moop':2500,
          'medical': {'deductible': 2500, 'coinsurance': 1},
          'drug': {'deductible': 0, 'coinsurance': 1}},
         Tier.gold, .796],
        [{'moop':4750,
          'medical': {'deductible': 4750, 'coinsurance': 1},
          'drug': {'deductible': 0, 'coinsurance': 1}},
         Tier.silver, .716]
    ]
    for test_plan in test_plans:
        check_health_plan(test_plan)

def test_existing_av():
    test_plan = HealthPlan()
    test_plan.deductible = 500
    test_plan.coinsurance = .9
    test_plan.moop = 1000
    test_plan.av = .898
    calc.calculate_av(test_plan)
    assert_almost_equal(test_plan.av,
                        .898,
                        3,
                        "Av is not equal to correct value. Should be {0} is {1}".format(.898, test_plan.av))
    assert test_plan.tier == Tier.platinum,\
        "Tier does not match expected tier. Expected tier is {0} actual tier is {1}".format(Tier.platinum,
                                                                                            test_plan.tier)