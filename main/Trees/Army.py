import random

import sc2
from sc2 import Race, Difficulty
from sc2.constants import *
from sc2.player import Bot, Computer

import BehaviourTree
from BehaviourTree import *


# instance represents the bot itself, so we can tell it to do stuff
class Action:
    """A way of passing the variables"""

    def __init__(self, inst):
        self.instance = inst
        self.warpgate_started = False

    async def trainZealots(self):
        if not self.instance.can_afford(UnitTypeId.ZEALOT):
            return False
        for gate in self.instance.units(UnitTypeId.GATEWAY).ready:
            if gate.noqueue:
                await self.instance.do(gate.train(UnitTypeId.ZEALOT))
                return True
        return False

    async def buildCyberneticsCore(self):
        if self.instance.can_afford(UnitTypeId.CYBERNETICSCORE):
            nexus = self.instance.units(UnitTypeId.NEXUS).ready.random
            await self.instance.build(UnitTypeId.CYBERNETICSCORE,
                                      near=nexus.position.towards(self.instance.game_info.map_center, distance=10))
            return True
        return False

    async def shouldBuildCyberneticsCore(self):
        if not self.instance.units(UnitTypeId.CYBERNETICSCORE).exists and not self.instance.already_pending(UnitTypeId.CYBERNETICSCORE):
            return len(self.instance.units(UnitTypeId.ZEALOT)) >= 4
        return False

    async def shouldTrainZealots(self):
        if len(self.instance.units(UnitTypeId.ZEALOT)) < 4 and not self.instance.already_pending(UnitTypeId.ZEALOT):
            return True
        # TODO: check for cybernetics core and gateways, then train 3 more
        # if self.instance.units(UnitTypeId.CYBERNETICSCORE).ready.exists:
        if len(self.instance.units(UnitTypeId.ZEALOT)) < 7 and not self.instance.already_pending(UnitTypeId.ZEALOT):
            return True
        return False

    async def arleadyHaveCyberCore(self):
        return self.instance.units(UnitTypeId.CYBERNETICSCORE).ready.exists and \
               not self.instance.already_pending(UnitTypeId.CYBERNETICSCORE)

    async def arleadyHaveAllGates(self):
        return self.instance.units(UnitTypeId.GATEWAY).ready.amount >= 4

    async def buildGateway(self):
        nexus = self.instance.units(UnitTypeId.NEXUS).ready.random
        if self.instance.can_afford(UnitTypeId.GATEWAY):
            await self.instance.build(UnitTypeId.GATEWAY,
                                      near=nexus.position.towards(self.instance.game_info.map_center, distance=20))
            return True
        return False

    async def doWarpGateResearch(self):
        #abilities = await self.get_available_abilities(ccore)
        if not self.instance.can_afford(AbilityId.RESEARCH_WARPGATE) and self.instance.warpgate_started:
            return False
        ccore = self.instance.units(UnitTypeId.CYBERNETICSCORE).ready.first
        await self.instance.do(ccore(UnitTypeId.RESEARCH_WARPGATE))
        self.warpgate_started = True
        return True

    async def researchAirAmor(self):
        #abilities = await self.get_available_abilities(ccore)
        print ("Research started!!!!!!!!!")
        if not self.instance.can_afford(AbilityId.RESEARCH_PROTOSSAIRARMOR):
            return False
        ccore = self.instance.units(UnitTypeId.CYBERNETICSCORE).ready.first
        await self.instance.do(ccore(AbilityId.RESEARCH_PROTOSSAIRARMOR))
        return True

    async def researchAirWeapon(self):
        #abilities = await self.get_available_abilities(ccore)
        if not self.instance.can_afford(AbilityId.RESEARCH_PROTOSSAIRWEAPONS):
            return False
        ccore = self.instance.units(UnitTypeId.CYBERNETICSCORE).ready.first
        await self.instance.do(ccore(AbilityId.RESEARCH_PROTOSSAIRWEAPONS))
        return True

    async def haveResourcesForStalker(self):
        return self.instance.can_afford(UnitTypeId.STALKER)

    async def haveEnoughStalkers(self):
        return self.instance.units(UnitTypeId.STALKER).amount > 13

    async def trainStalkers(self):
        print ("Train Stalkers")
        for gate in self.instance.units(UnitTypeId.GATEWAY):
            if self.instance.can_afford(UnitTypeId.STALKER) and gate.noqueue:
                await self.instance.do(gate.train(UnitTypeId.STALKER))
                return True
        return False

    async def trainVR(self):
        print("Train vr")
        for gate in self.instance.units(UnitTypeId.STARGATE):
            if self.instance.can_afford(UnitTypeId.VOIDRAY) and gate.noqueue:
                await self.instance.do(gate.train(UnitTypeId.VOIDRAY))
                return True
        return False

    async def rushEnemyBaseWithEverything(self):
        for stalker in self.instance.units(UnitTypeId.STALKER):
            await self.instance.do(stalker.attack(self.instance.enemy_start_locations[0]))
        for zealot in self.instance.units(UnitTypeId.ZEALOT):
            await self.instance.do(zealot.attack(self.instance.enemy_start_locations[0]))
        for vr in self.instance.units(UnitTypeId.VOIDRAY):
            await self.instance.do(vr.attack(self.instance.enemy_start_locations[0]))
        return True

    async def doNothing(self):
        return True


action = Action(None)


def defAction(instance):
    global action
    action.instance = instance


#TREE
s1 = Selector(
    Conditional(action.arleadyHaveCyberCore, #Do we arleady have one?
        Selector(
            Conditional(action.arleadyHaveAllGates,
                Selector(
                    Conditional(action.haveEnoughStalkers,Atomic(action.rushEnemyBaseWithEverything)), #stop if we arleady have enough stalkers
                    ConditionalElse(action.haveResourcesForStalker,
                        Atomic(action.trainStalkers), #Train stalkers
                        Atomic(action.doNothing) #Save resources for later
                    )
                )
            ),
            Atomic(action.buildGateway)

            #Atomic(action.researchAirAmor),
            #Atomic(action.researchAirWeapon)
            #Atomic(action.doWarpGateResearch)
        ) #Build more gateways
    ),
    Conditional(action.shouldBuildCyberneticsCore, #Should we have one?
                Atomic(action.buildCyberneticsCore)), #Build one then
    Conditional(action.shouldTrainZealots,
                Atomic(action.trainZealots)),
)


async def runTree():
    global action
    if action is not None:
        await s1.run()
    else:
        return False
    return True
