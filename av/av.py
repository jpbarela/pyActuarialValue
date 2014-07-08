from av.continuancetable import ContinuanceTable
from av.database import connection

from healthplan.tier import Tier

def __calculate_coinsurance(session, table, deductible, moop, coinsurance):
    if coinsurance == 1:
        member_slice = 0
    else:
        high_value = (moop - deductible)/(1-coinsurance) + deductible
        total_slice = table.slice(session, high_value, deductible)
        preventive_care_slice = table.slice(session, high_value, deductible, "preventive_care_value")
        coinsurance_slice = total_slice - preventive_care_slice
        member_slice = coinsurance_slice * (1-coinsurance)
    return member_slice

def __calculate_deductible(session, table, deductible):
    deductible_slice = table.slice(session, deductible)
    preventive_care_slice = table.slice(session, deductible, column="preventive_care_value")
    return deductible_slice - preventive_care_slice

def __set_tier(av):
    if av == None:
        tier = None
    else:
        if av > .85:
            tier = Tier.platinum
        elif av > .75:
            tier = Tier.gold
        elif av > .65:
            tier = Tier.silver
        else:
            tier = Tier.bronze
    return tier

def __set_table(session, tier):
    if tier == Tier.bronze:
        table = ContinuanceTable.find(session, "BronzeIntegrated")
    elif tier == Tier.silver:
        table = ContinuanceTable.find(session, "SilverIntegrated")
    elif tier == Tier.gold:
        table = ContinuanceTable.find(session, "GoldIntegrated")
    else:
        table = ContinuanceTable.find(session, "PlatinumIntegrated")
    return table

def __determine_av(session, table, health_plan):
    member_deductible = __calculate_deductible(session, table, health_plan.deductible)
    member_coinsurance = __calculate_coinsurance(session, table, health_plan.deductible, health_plan.moop, health_plan.coinsurance)
    member_percent = (member_deductible + member_coinsurance)/table.avg_cost
    return round(1 - member_percent, 3)

def calculate_av(health_plan):
    session = connection.Session()
    tier = __set_tier(health_plan.av)
    table = __set_table(session, tier)
    av = __determine_av(session, table, health_plan)
    check_tier = __set_tier(av)
    if tier == check_tier:
        health_plan.av = av
    else:
        table = __set_table(session, check_tier)
        health_plan.av = __determine_av(session, table, health_plan)