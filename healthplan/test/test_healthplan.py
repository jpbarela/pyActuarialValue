import json
from nose.tools import assert_almost_equal
from nose.tools import raises
from healthplan.healthplan import HealthPlan
from healthplan.tier import Tier


def check_json(json_hash):
    test_health_plan = HealthPlan()
    test_health_plan.parse_JSON(json.dumps(json_hash))
    for key, value in json_hash.items():
        if isinstance(value, dict):
            for subkey, subvalue in value.items():
                check_attribute_value(test_health_plan, key + '_' + subkey,
                                      subvalue)
        else:
            check_attribute_value(test_health_plan, key, value)


def check_attribute_value(plan, attribute, value):
    test_value = getattr(plan, attribute)
    if attribute == 'tier':
        value = Tier[value]
    assert test_value == value, \
        "The {0} should be {1} was {2}".format(attribute, value, test_value)


def check_tier_determination(av_array):
    test_health_plan = HealthPlan()
    test_health_plan.av = av_array[0]
    assert_almost_equal(test_health_plan.av,
                        av_array[0],
                        3,
                        "Av is not equal to correct value. Should be {0} is "
                        "{1}".format(av_array[0], test_health_plan.av))
    assert test_health_plan.tier == av_array[1], \
        ("Tier does not match expected tier. Expected tier is {0} actual tier "
         "is {1}".format(av_array[0], test_health_plan.tier))


def test_parse_JSON():
    check_json({'deductible': 1000, 'coinsurance': .80, 'moop': 2500})
    check_json({'moop': 2500,
                'medical': {'deductible': 1000, 'coinsurance': .9},
                'drug': {'deductible': 250, 'coinsurance': .8}})
    check_json({'medical': {'deductible': 1000,
                            'coinsurance': .9,
                            'moop': 2000},
                'drug': {'deductible': 250, 'coinsurance': .8, 'moop': 500},
                'tier': 'gold'})


def test_set_av_sets_tier():
    test_avs = [[.95, Tier.na], [.91, Tier.platinum], [.85, Tier.na],
                [.79, Tier.gold], [.77, Tier.na], [.719, Tier.silver],
                [.63, Tier.na], [.615, Tier.bronze]]
    for test_av in test_avs:
        check_tier_determination(test_av)


def test_valid_json_includes_coinsurance():
    test_json = json.dumps({'deductible': 1000})
    assert HealthPlan.valid_json(test_json) is False, \
        'Required coinsurance missing.'


def test_valid_json_includes_drug():
    test_json = json.dumps({'moop': 1500, 'medical': {'deductible': 500,
                                                      'coinsurance': .9}})
    assert HealthPlan.valid_json(test_json) is False, \
        'Required drug dictionary missing.'


def test_valid_json_includes_deductible():
    empty_json = json.dumps({})
    assert HealthPlan.valid_json(empty_json) is False, \
        'Required deductible missing.'
    medical_deductible_json = json.dumps({'moop': 2500,
                                          'medical': {'deductible': 1000,
                                                      'coinsurance': .9},
                                          'drug': {'deductible': 250,
                                                   'coinsurance': .8}})
    assert HealthPlan.valid_json(medical_deductible_json) is True, \
        'Valid medical deductible failed'


def test_valid_json_includes_moop():
    test_json = json.dumps({'deductible': 1000, 'coinsurance': .80})
    assert HealthPlan.valid_json(test_json) is False, 'Required moop missing.'


def test_valid_json_includes_seperate_moops():
    test_json = json.dumps({'medical': {'deductible': 1000,
                                        'coinsurance': .8,
                                        'moop': 2500},
                            'drug': {'deductible': 250,
                                     'coinsurance': .8,
                                     'moop': 750}})
    assert HealthPlan.valid_json(test_json) is True, \
        'Seperate moops return false.'


@raises(ValueError)
def test_valid_JSON_raises_value_error():
    test_json = '{"deductible": 1000, "coinsurance": .8}'
    assert HealthPlan.valid_json(test_json)
