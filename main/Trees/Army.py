import random

import sc2
from sc2 import Race, Difficulty
from sc2.constants import *
from sc2.player import Bot, Computer

import BehaviourTree
from BehaviourTree import *
import Trees.Defense as defense

hasAttacked = False

# instance represents the bot itself, so we can tell it to do stuff
class Action:
    """A way of passing the variables"""

    def __init__(self, inst):
        self.instance = inst
        self.warpgate_started = False
    async def on_step(self, iteration):
        await self.trainZealots()
        await self.buildCyberneticsCore()

    async def trainZealots(self):
        for gate in self.instance.units(UnitTypeId.GATEWAY).ready:
            if self.instance.can_afford(UnitTypeId.ZEALOT) and gate.noqueue:
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

    async def canAffordStarGate(self):
        return self.instance.can_afford(UnitTypeId.STARGATE)

    async def buildStarGate(self):
        print ("Build StarGate")
        if self.instance.can_afford(UnitTypeId.STARGATE):
            nexus = self.instance.units(UnitTypeId.NEXUS).ready.random
            await self.instance.build(UnitTypeId.STARGATE,
                                      near=nexus.position.towards(self.instance.game_info.map_center, distance=25))
            return True
        return False

    async def shouldBuildCyberneticsCore(self):
        if not self.instance.units(UnitTypeId.CYBERNETICSCORE).exists and not self.instance.already_pending(UnitTypeId.CYBERNETICSCORE):
            return len(self.instance.units(UnitTypeId.ZEALOT)) >= 4
        return False

    async def arleadyHaveCyberCore(self):
        return self.instance.units(UnitTypeId.CYBERNETICSCORE).ready.exists and \
               not self.instance.already_pending(UnitTypeId.CYBERNETICSCORE)

    async def arleadyHaveAllGates(self):
        return self.instance.units(UnitTypeId.GATEWAY).ready.amount >= 4

    async def arleadyHaveEnoughStarGate(self):
        return self.instance.units(UnitTypeId.STARGATE).amount > 3

    async def buildSeveralGateways(self):
        if self.instance.units(UnitTypeId.GATEWAY).amount > 4:
            return False
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

    async def hasAttackedBase(self):
        print ("Has Attacked Base ", hasAttacked, "-----")
        return hasAttacked

    async def rushEnemyBaseWithEverything(self):
        global hasAttacked
        hasAttacked = True
        for stalker in self.instance.units(UnitTypeId.STALKER):
            await self.instance.do(stalker.attack(self.instance.enemy_start_locations[0]))
        for zealot in self.instance.units(UnitTypeId.ZEALOT):
            await self.instance.do(zealot.attack(self.instance.enemy_start_locations[0]))
        for vr in self.instance.units(UnitTypeId.VOIDRAY):
            await self.instance.do(vr.attack(self.instance.enemy_start_locations[0]))
        return True

    async def doNothing(self):
        return True

    async def applyDefenseTree(self):
        defense.defAction(self.instance)
        await defense.runTree()


action = Action(None)


def defAction(instance):
    global action
    action.instance = instance


#TREE
s2 = Selector(
    Conditional(action.arleadyHaveCyberCore, #Do we arleady have one?
        Selector(
            Conditional(action.arleadyHaveAllGates,
                Selector(
                    Conditional(action.hasAttackedBase,
                        ConditionalElse(action.arleadyHaveEnoughStarGate,
                            Atomic(action.trainVR),
                            Atomic(action.buildStarGate)
                        )
                    ),
                    Conditional(action.haveEnoughStalkers, #stop if we arleady have enough stalkers
                        Sequence(
                            Atomic(action.rushEnemyBaseWithEverything)
                            #ConditionalElse(action.arleadyHaveEnoughStarGate,
                            #                Atomic(action.trainVR),
                            #                Atomic(action.buildStarGate))
                        )
                    ),
                    ConditionalElse(action.haveResourcesForStalker,
                        Atomic(action.trainStalkers), #Train stalkers
                        Atomic(action.doNothing) #Save resources for later
                    )
                )
            ),
            Atomic(action.buildSeveralGateways)

            #Atomic(action.researchAirAmor),
            #Atomic(action.researchAirWeapon)
            #Atomic(action.doWarpGateResearch)
        ) #Build more gateways
    ),
    Conditional(action.shouldBuildCyberneticsCore, #Should we have one?
                Atomic(action.buildCyberneticsCore)), #Build one then
    Atomic(action.trainZealots), #Train the zealots then
)

s1 = DoAllSequence(
    Selector(
        ConditionalElse(action.haveEnoughStalkers, #do we have to attack? TODO -> needs to be swithced with something a bit more complex
            Atomic(action.rushEnemyBaseWithEverything), # TODO -> change for the attacker version MAYBE THE CONDITION AND THE ATTACK TREE SHOULD BE IN THE SAME PLACE
            Atomic(action.applyDefenseTree)
        ),
        s2
    )
)

async def runTree():
    global action
    if action is not None:
        await s1.run()
    else:
        return False
    return True
