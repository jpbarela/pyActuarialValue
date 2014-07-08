from nose.tools import assert_almost_equal
from av import av
from healthplan.healthplan import HealthPlan
from healthplan.tier import Tier

def create_plan(plan_hash):
    result = HealthPlan()
    result.deductible = plan_hash['deductible']
    result.coinsurance = plan_hash['coinsurance']
    result.moop = plan_hash['moop']
    return result

def check_health_plan(health_plan_array):
    test_health_plan = create_plan(health_plan_array[0])
    av.calculate_av(test_health_plan)
    assert_almost_equal(test_health_plan.av,
                        health_plan_array[2],
                        3,
                        "Av is not equal to correct value. Should be {0} is {1}".format(health_plan_array[2],test_health_plan.av))
    assert test_health_plan.tier == health_plan_array[1],\
        "Tier does not match expected tier. Expected tier is {0} actual tier is {1}".format(health_plan_array[1], test_health_plan.tier)

def test_calculate_av_for_plans():
    test_plans = [
        [{"deductible": 500,  "coinsurance": .9, "moop":1000}, Tier.platinum, .898],
        [{"deductible": 500,  "coinsurance": .8, "moop":3500}, Tier.gold, .819],
        [{"deductible": 3000, "coinsurance": 1,  "moop":3000}, Tier.silver, .717],
        [{"deductible": 2000, "coinsurance": .5, "moop":6850}, Tier.bronze, .619]
    ]
    for test_plan in test_plans:
        check_health_plan(test_plan)

def test_existing_av():
    test_plan = HealthPlan()
    test_plan.deductible = 500
    test_plan.coinsurance = .9
    test_plan.moop = 1000
    test_plan.av = .898
    av.calculate_av(test_plan)
    assert_almost_equal(test_plan.av,
                        .898,
                        3,
                        "Av is not equal to correct value. Should be {0} is {1}".format(.898, test_plan.av))
    assert test_plan.tier == Tier.platinum,\
        "Tier does not match expected tier. Expected tier is {0} actual tier is {1}".format(Tier.platinum, test_health_plan.tier)