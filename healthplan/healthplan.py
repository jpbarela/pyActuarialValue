import json
from healthplan.tier import Tier

def valid_json(json_string):
    values = json.loads(json_string)
    required_keys = ['deductible', 'coinsurance', 'moop']
    for key in required_keys:
        if not (key in values):
            return False
    return True

class HealthPlan:

    def __init__(self):
        self.deductible     = None
        self.coinsurance    = None
        self.moop           = None
        self._av            = None
        self.tier           = None

    def parseJSON(self, json_string):
        if valid_json(json_string):
            values = json.loads(json_string)
            self.deductible     = values['deductible']
            self.coinsurance    = values['coinsurance']
            self.moop           = values['moop']

    @property
    def av(self):
        return self._av

    @av.setter
    def av(self, value):
        self._av = value
        self.__determine_tier__()

    def __determine_tier__(self):
        if (self.av < .92) and (self.av > .88):
            self.tier = Tier.platinum
        elif (self.av < .82) and (self.av > .78):
            self.tier = Tier.gold
        elif (self.av < .72) and (self.av > .68):
            self.tier = Tier.silver
        elif (self.av < .62) and (self.av > .58):
            self.tier = Tier.bronze
        else:
            self.tier = Tier.na
