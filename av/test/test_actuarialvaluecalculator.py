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
    coinsurance = calc._determine_coinsurance_expenses(test_plan.deductible,
                                                       test_plan)
    assert_almost_equal(coinsurance,
                        test_plan_array[3],
                        2,
                        "Expected expenses for coinsurance are not correct, "
                        "actual {0}, expected {1}".format(
                            coinsurance, test_plan_array[3]))


def check_determine_coinsurance_expenses_separate(test_plan_array):
    test_plan = create_plan_from_hash(test_plan_array[0])

    calc._determine_moop(test_plan, test_plan.medical_deductible,
                         test_plan.drug_deductible)
    coinsurance = (calc._determine_coinsurance_expenses(
        test_plan.medical_deductible,
        test_plan,
        test_plan.drug_deductible))

    assert_almost_equal(coinsurance,
                        test_plan_array[1],
                        2,
                        "Expected expenses for coinsurance are not correct, "
                        "actual {0}, expected {1}".format(coinsurance,
                                                          test_plan_array[1]))


def check_determine_expenses_after_moop(test_plan_array):
    test_plan = HealthPlan()
    test_plan.coinsurance = test_plan_array[2]
    test_plan.deductible = test_plan_array[0]
    test_plan.moop = test_plan_array[1]

    calc._determine_moop(test_plan, test_plan.deductible)
    calc._determine_coinsurance_expenses(test_plan.deductible, test_plan)
    after_moop_exepenses = calc._determine_expenses_after_moop()
    assert_almost_equal(after_moop_exepenses,
                        test_plan_array[3],
                        2,
                        "Expected expenses after moop are not correct, actual "
                        "{0}, expected {1}".format(
                            after_moop_exepenses, test_plan_array[3]))


def check_determine_expenses_before_deductible(test_deductible_array):
    expenses = \
        calc._determine_expenses_before_deductible(test_deductible_array[0])
    assert_almost_equal(expenses,
                        test_deductible_array[1],
                        2,
                        "Expected expenses for deductible are not correct, "
                        "actual {0}, expected {1}".format(
                            expenses,
                            test_deductible_array[1]))


def check_determine_total_expenses(test_totals_array):
    test_plan = create_plan(test_totals_array[0])
    calc._set_metal_tier(test_plan)
    calc._determine_total_cost()
    assert_almost_equal(calc._total_cost,
                        test_totals_array[1],
                        2,
                        "Expected total costs are not correct for tier {0}, "
                        "actual {1}, expected {2}".format(test_totals_array[0],
                                                          calc._total_cost,
                                                          test_totals_array[1]))


def check_effective_coinsurance_integrated(test_plan_array):
    test_plan = create_plan(test_plan_array[0])
    test_plan.coinsurance = test_plan_array[1]

    calc._set_metal_tier(test_plan)
    effective_coinsurance = calc._effective_coinsurance(test_plan)
    assert_almost_equal(effective_coinsurance,
                        test_plan_array[2],
                        4,
                        "Expected effective coinsurance is not correct for "
                        "tier {0}, actual {1}, expected {2}".format(
                            test_plan_array[0],
                            effective_coinsurance,
                            test_plan_array[2]))


def check_effective_coinsurance_separate(test_plan_array):
    test_plan = create_plan(test_plan_array[0])
    test_plan.medical_coinsurance = test_plan_array[1]
    test_plan.drug_coinsurance = test_plan_array[2]
    test_plan.medical_deductible = 1000

    calc._set_metal_tier(test_plan)
    effective_coinsurance = calc._effective_coinsurance(test_plan)
    assert_almost_equal(effective_coinsurance,
                        test_plan_array[3],
                        4,
                        "Expected effective coinsurance is not correct for "
                        "tier {0}, actual {1}, expected {2}".format(
                            test_plan_array[0],
                            effective_coinsurance,
                            test_plan_array[3]))


def check_health_plan(health_plan_array):
    test_health_plan = create_plan_from_hash(health_plan_array[0])
    calc.calculate_av(test_health_plan)
    assert_almost_equal(test_health_plan.av,
                        health_plan_array[2],
                        4,
                        "Av is not equal to correct value. Should be {0} is "
                        "{1}".format(health_plan_array[2],test_health_plan.av))
    assert test_health_plan.tier == health_plan_array[1], \
        "Tier does not match expected tier. Expected tier is {0} actual tier" \
        " is {1}".format(health_plan_array[1], test_health_plan.tier)


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


# test private methods
def test__determine_coinsurance_expenses_integrated():
    test_plan = create_plan(Tier.platinum, separate=False)

    calc._set_metal_tier(test_plan)
    plans = [[0, 500, .9, 2332.96],
             [500, 1000, .8, 1169.82],
             [4500, 6500, .5, 517.31]]
    for plan in plans:
        check_determine_coinsurance_expenses_integrated(plan)


def test__determine_coinsurance_expenses_separate():
    test_plan = create_plan(Tier.platinum, separate=True)

    calc._set_metal_tier(test_plan)
    plans = [[{'moop': 500,
               'medical': {'deductible': 0, 'coinsurance': .9},
               'drug': {'deductible': 0, 'coinsurance': 1}}, 2789.42],
             [{'moop': 1000,
               'medical': {'deductible': 500, 'coinsurance': .8},
               'drug': {'deductible': 0, 'coinsurance': 1}}, 1523.64],
             [{'moop': 6500,
               'medical': {'deductible': 4500, 'coinsurance': .5},
               'drug': {'deductible': 0, 'coinsurance': 1}}, 1001.69],
             [{'moop': 1500,
               'medical': {'deductible': 750, 'coinsurance': .9},
               'drug': {'deductible': 250, 'coinsurance': .8}}, 1723.93],
             [{'moop': 2500,
               'medical': {'deductible': 1000, 'coinsurance': .8},
               'drug': {'deductible': 250, 'coinsurance': .9}}, 2176.72]]
    for plan in plans:
        check_determine_coinsurance_expenses_separate(plan)


def test__effective_coinsurance_integrated():
    plans = [[Tier.platinum, .9, .9036],
             [Tier.gold, .8, .8069],
             [Tier.silver, .7, .7100],
             [Tier.bronze, .6, .6140]]

    for plan in plans:
        check_effective_coinsurance_integrated(plan)


def test__effective_coinsurance_separate():
    plans = [[Tier.platinum, .9, 1, .9250],
             [Tier.gold, .8, .9, .8274],
             [Tier.silver, .7, .8, .7313],
             [Tier.bronze, .6, .7, .6333]]

    for plan in plans:
        check_effective_coinsurance_separate(plan)


def test__determine_expenses_after_moop():
    test_plan = create_plan(Tier.platinum)

    calc._set_metal_tier(test_plan)
    plans = [[0, 500, .9, 3967.81],
             [500, 1000, .8, 4689.49],
             [4500, 6500, .5, 3186.90]]
    for plan in plans:
        check_determine_expenses_after_moop(plan)


def test__determine_expenses_before_deductible_integrated():
    test_plan = create_plan(Tier.platinum, separate=False)

    calc._set_metal_tier(test_plan)
    deductibles = [[0, 0], [500, 18.83], [1000, 45.03]]
    for deductible in deductibles:
        check_determine_expenses_before_deductible(deductible)


def test__determine_expenses_before_deductible_separate():
    test_plan = create_plan(Tier.platinum, separate=True)

    calc._set_metal_tier(test_plan)
    deductibles = [[0, 0], [500, 25.17], [1000, 57.91]]
    for deductible in deductibles:
        check_determine_expenses_before_deductible(deductible)


def test__determine_moop_integrated():
    test_plan = HealthPlan()
    test_plan.deductible = 1000
    test_plan.coinsurance = .9
    test_plan.moop = 2000
    test_plan.tier = Tier.platinum

    calc._set_metal_tier(test_plan)
    calc._determine_moop(test_plan, test_plan.deductible)
    assert_almost_equal(calc._moop_cost_level,
                        11372.76,
                        0,
                        ("Integrated plan moop not correct, actual {0}, "
                         "expected {1}".format(calc._moop_cost_level,
                                               11372.76)))


def test__determine_moop_separate():
    test_plan = HealthPlan()
    test_plan.medical_deductible = 500
    test_plan.medical_coinsurance = .8
    test_plan.drug_deductible = 500
    test_plan.drug_coinsurance = .8
    test_plan.moop = 2000

    calc._set_metal_tier(test_plan)
    calc._determine_moop(test_plan,
                         test_plan.medical_deductible,
                         test_plan.drug_deductible)
    assert_almost_equal(calc._moop_cost_level,
                        6186.38,
                        0,
                        "Seperate plan moop not correct, actual {0}, expected "
                        "{1}".format(calc._moop_cost_level, 6186.38))


def test__determine_moop_floor():
    test_plan = HealthPlan()
    test_plan.medical_deductible = 500
    test_plan.medical_coinsurance = .8
    test_plan.drug_deductible = 500
    test_plan.drug_coinsurance = .8
    test_plan.moop = 2000
    calc._set_metal_tier(test_plan)
    calc._ActuarialValueCalculator__moop_floor = 9000

    calc._determine_moop(test_plan, test_plan.medical_deductible,
                         test_plan.drug_deductible)
    assert_almost_equal(calc._moop_cost_level,
                        9000,
                        0,
                        "Integrated plan moop not correct, actual {0}, "
                        "expected {1}".format(calc._moop_cost_level, 9000))


def test__determine_total_costs():
    test_array = [[Tier.platinum, 6543.47],
                  [Tier.gold, 6088.36],
                  [Tier.silver, 5809.58],
                  [Tier.bronze, 5598.79]]

    for test_tier in test_array:
        check_determine_total_expenses(test_tier)


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


# test public methods
def test_calculate_av_for_basic_integrated_plans():
    test_plans = [
        [{"deductible": 500,  "coinsurance": .9, "moop": 1000},
         Tier.platinum, .9065],
        [{"deductible": 500,  "coinsurance": .8, "moop": 4500},
         Tier.gold, .8164],
        [{"deductible": 3500, "coinsurance": 1,  "moop": 3500},
         Tier.silver, .7116],
        [{"deductible": 3000, "coinsurance": .5, "moop": 6850},
         Tier.bronze, .6175]
    ]
    for test_plan in test_plans:
        check_health_plan(test_plan)


def test_calculate_av_for_basic_separate_plans():
    test_plans = [[{'moop': 1000,
                    'medical': {'deductible': 500, 'coinsurance': .9},
                    'drug': {'deductible': 0, 'coinsurance': 1}},
                   Tier.platinum, .9173],
                  [{'moop': 3500,
                    'medical': {'deductible': 1500, 'coinsurance': .8},
                    'drug': {'deductible': 0, 'coinsurance': 1}},
                   Tier.gold, .8013],
                  [{'moop': 5000,
                    'medical': {'deductible': 3500, 'coinsurance': .7},
                    'drug': {'deductible': 0, 'coinsurance': 1}},
                   Tier.silver, .6996]]
    for test_plan in test_plans:
        check_health_plan(test_plan)


def test_calculate_av_for_plans_with_different_deductibles():
    test_plans = [[{'moop': 1000,
                    'medical': {'deductible': 500, 'coinsurance': .9},
                    'drug': {'deductible': 400, 'coinsurance': 1}},
                   Tier.platinum, .9060],
                  [{'moop': 2500,
                    'medical': {'deductible': 1500, 'coinsurance': .8},
                    'drug': {'deductible': 750, 'coinsurance': 1}},
                   Tier.gold, .7945],
                  [{'moop': 5000,
                    'medical': {'deductible': 2750, 'coinsurance': .7},
                    'drug': {'deductible': 400, 'coinsurance': .8}},
                   Tier.silver, .6978],
                  [{'moop': 6850,
                    'medical': {'deductible': 5000, 'coinsurance': .5},
                    'drug': {'deductible': 2500, 'coinsurance': .7}},
                   Tier.bronze, .5931]]
    for test_plan in test_plans:
        check_health_plan(test_plan)


def test_calculate_av_for_separate_deductible_only():
    test_plans = [[{'moop': 750,
                    'medical': {'deductible': 750, 'coinsurance': 1},
                    'drug': {'deductible': 0, 'coinsurance': 1}},
                   Tier.platinum, .9148],
                  [{'moop': 2500,
                    'medical': {'deductible': 2500, 'coinsurance': 1},
                    'drug': {'deductible': 0, 'coinsurance': 1}},
                   Tier.gold, .7851],
                  [{'moop': 4750,
                    'medical': {'deductible': 4750, 'coinsurance': 1},
                    'drug': {'deductible': 0, 'coinsurance': 1}},
                   Tier.silver, .6834]]
    for test_plan in test_plans:
        check_health_plan(test_plan)


def test_existing_av():
    test_plan = HealthPlan()
    test_plan.deductible = 500
    test_plan.coinsurance = .9
    test_plan.moop = 1000
    test_plan.av = .9065
    calc.calculate_av(test_plan)
    assert_almost_equal(test_plan.av,
                        .9065,
                        3,
                        "Av is not equal to correct value. Should be {0} is "
                        "{1}".format(.9065, test_plan.av))
    assert test_plan.tier == Tier.platinum, \
        "Tier does not match expected tier. Expected tier is {0} actual tier" \
        " is {1}".format(Tier.platinum, test_plan.tier)
