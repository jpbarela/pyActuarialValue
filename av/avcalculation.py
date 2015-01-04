class AVCalculation():
    def __init__(self, session, health_plan):
        self.__session = session
        self.__health_plan = health_plan

    def __eq__(self, other):
        return ((self.__class__ == other.__class__) and
                (self.__session == other.__session) and
                (self.__health_plan == other.__health_plan))
