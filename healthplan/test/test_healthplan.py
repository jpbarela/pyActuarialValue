import json
from nose.tools import assert_almost_equal
from nose.tools import raises
from healthplan import healthplan
from healthplan.tier import Tier

def check_tier_determination(av_array):
    test_health_plan = healthplan.HealthPlan()
    test_health_plan.av = av_array[0]
    assert_almost_equal(test_health_plan.av,
                        av_array[0],
                        3,
                        "Av is not equal to correct value. Should be {0} is {1}".format(av_array[0],test_health_plan.av))
    assert test_health_plan.tier == av_array[1], "Tier does not match expected tier. Expected tier is {0} actual tier is {1}".format(av_array[0], test_health_plan.tier)

def test_toJSON():
    test_json = json.dumps({"deductible": 1000, "coinsurance": .80, "moop": 2500})
    testHealthPlan = healthplan.HealthPlan()
    testHealthPlan.parseJSON(test_json)
    assert testHealthPlan.deductible == 1000, "The deductible should be 1000 was {0}".format(testHealthPlan.deductible)
    assert testHealthPlan.coinsurance == .8, "The deductible should be 0.2 was {0}".format(testHealthPlan.coinsurance)
    assert testHealthPlan.moop == 2500, "The deductible should be 2500 was {0}".format(testHealthPlan.moop)

def test_json_includes_deductible():
    test_json = json.dumps({})
    assert healthplan.valid_json(test_json) == False, "Required deductible missing."

def test_json_includes_coinsurance():
    test_json = json.dumps({"deductible": 1000})
    assert healthplan.valid_json(test_json) == False, "Required coinsurance missing."

def test_json_includes_moop():
    test_json = json.dumps({"deductible": 1000, "coinsurance": .80})
    assert healthplan.valid_json(test_json) == False, "Required moop missing."

@raises(ValueError)
def test_toJSON_raises_value_error():
    test_json = '{"deductible": 1000, "coinsurance": .8}'
    assert healthplan.valid_json(test_json)

def test_set_av():
    test_avs = [[.95, Tier.na], [.91, Tier.platinum], [.85, Tier.na], [.79, Tier.gold], [.77, Tier.na],
                [.719, Tier.silver], [.63, Tier.na], [.615, Tier.bronze]]
    for test_av in test_avs:
        check_tier_determination(test_av)