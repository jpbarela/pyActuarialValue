import json
from healthplan.tier import Tier

def __check_dict(dictionary, key):
    if key in dictionary:
        return True
    else:
        if not 'medical' in dictionary:
            return False
        if not 'drug' in dictionary:
            return False
        return key in dictionary['medical'] and key in dictionary['drug']

def valid_json(json_string):
    values = json.loads(json_string)
    return __check_dict(values, 'deductible') \
        and __check_dict(values, 'coinsurance') \
        and __check_dict(values, 'moop')

class HealthPlan:

    def __init__(self):
        self.deductible             = None
        self.coinsurance            = None
        self.moop                   = None
        self._av                    = None
        self.tier                   = None
        self.drug_deductible        = None
        self.drug_coinsurance       = None
        self.medical_deductible     = None
        self.medical_coinsurance    = None

    def parse_JSON(self, json_string):
        if valid_json(json_string):
            values = json.loads(json_string)
            if 'medical' in values:
                self.medical_deductible     = values['medical']['deductible']
                self.medical_coinsurance    = values['medical']['coinsurance']
                self.drug_deductible        = values['drug']['deductible']
                self.drug_coinsurance       = values['drug']['coinsurance']
            else:
                self.deductible     = values['deductible']
                self.coinsurance    = values['coinsurance']
            self.moop = values['moop']
            if 'tier' in values:
                self.tier = Tier[values['tier']]

    @property
    def av(self):
        return self._av

    @av.setter
    def av(self, value):
        self._av = value
        self.__determine_tier()

    def __determine_tier(self):
        if (self.av <= .920) and (self.av >= .880):
            self.tier = Tier.platinum
        elif (self.av <= .820) and (self.av >= .780):
            self.tier = Tier.gold
        elif (self.av <= .720) and (self.av >= .680):
            self.tier = Tier.silver
        elif (self.av <= .620) and (self.av >= .580):
            self.tier = Tier.bronze
        else:
            self.tier = Tier.na
