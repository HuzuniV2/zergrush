import random

import sc2
from sc2 import Race, Difficulty
from sc2.constants import *
from sc2.player import Bot, Computer

import BehaviourTree
from BehaviourTree import  *
import sharedInfo
#from mainBot import state

import Trees.Army as army
# instance represents the bot itself, so we can tell it to do stuff
class Action:
    """A way of passing the variables"""
    def __init__(self, inst):
        self.instance = inst

    async def boost(self):
        prioritize_nexus = self.instance.units(UnitTypeId.PROBE).amount < 15
        for nexus in self.instance.units(UnitTypeId.NEXUS).ready:
            if not nexus.has_buff(BuffId.CHRONOBOOSTENERGYCOST):
                abilities = await self.instance.get_available_abilities(nexus)
                if AbilityId.EFFECT_CHRONOBOOSTENERGYCOST in abilities:
                    if not prioritize_nexus:
                        for gate in self.instance.units(UnitTypeId.GATEWAY).ready:
                            if not gate.noqueue:
                                await self.instance.do(nexus(AbilityId.EFFECT_CHRONOBOOSTENERGYCOST, gate))
                                return True
                    if not nexus.noqueue:
                        await self.instance.do(nexus(AbilityId.EFFECT_CHRONOBOOSTENERGYCOST, nexus))
                        return True
        return True

    async def has_crono_buff(self):
        """True if it has crono buff"""
        nexus = self.instance.units(UnitTypeId.NEXUS).ready.random
        bool = nexus.has_buff(BuffId.CHRONOBOOSTENERGYCOST)
        return bool

    async def exists_crono_buff(self):
        """True if it has crono buff"""
        nexus = self.instance.units(UnitTypeId.NEXUS).ready.random
        abilities = await self.instance.get_available_abilities(nexus)
        return AbilityId.EFFECT_CHRONOBOOSTENERGYCOST in abilities

    async def should_boost(self):
        """True if it has crono buff"""
        nexus = self.instance.units(UnitTypeId.NEXUS).ready.random
        return self.instance.units(UnitTypeId.PROBE).amount < 15 and not nexus.noqueue

    async def otherwise(self):
        gateways = []
        nexus = self.instance.units(UnitTypeId.NEXUS).ready.random
        for gate in self.instance.units(UnitTypeId.GATEWAY):
            gateways.append(gate)
        for gate in gateways:
            if not gate.noqueue:
                await self.instance.do(nexus(AbilityId.EFFECT_CHRONOBOOSTENERGYCOST, gate))
                return True
        return True

    async def do_chrono_boost(self):
        nexus = self.instance.units(UnitTypeId.NEXUS).ready.random
        if self.instance.units(UnitTypeId.PROBE).amount < 15 and not nexus.noqueue:
            await self.instance.do(nexus(AbilityId.EFFECT_CHRONOBOOSTENERGYCOST, nexus))
            return True
        return False

    async def buildProbes(self):
        nexus = self.instance.units(UnitTypeId.NEXUS).ready.random
        if self.instance.can_afford(UnitTypeId.PROBE):
            if nexus.assigned_harvesters < nexus.ideal_harvesters and nexus.noqueue:
                await self.instance.do(nexus.train(UnitTypeId.PROBE))
        return True


    async def lowOnResources(self):
        return self.instance.supply_left <= 2

    async def canBuildPylons(self):
        return self.instance.can_afford(UnitTypeId.PYLON) and not self.instance.already_pending(UnitTypeId.PYLON)

    async def buildPylons(self):
        nexus = self.instance.units(UnitTypeId.NEXUS).ready.random
        #if self.instance.supply_left <= 2:
        #if self.instance.can_afford(UnitTypeId.PYLON) and not self.instance.already_pending(UnitTypeId.PYLON):
        await self.instance.build(UnitTypeId.PYLON,
            near=nexus.position.towards(self.instance.game_info.map_center, distance=5))
        return True

    async def buildAssimilator(self):
        for nexus in self.instance.units(UnitTypeId.NEXUS).ready:
            gaisers = self.instance.state.vespene_geyser.closer_than(10.0, nexus)
            for gaiser in gaisers:
                if self.instance.can_afford(UnitTypeId.ASSIMILATOR) and not self.instance.already_pending(UnitTypeId.ASSIMILATOR):
                    builder = self.instance.select_build_worker(gaiser.position)
                    if not self.instance.units(UnitTypeId.ASSIMILATOR).closer_than(1.0, gaiser).exists:
                        await self.instance.do(builder.build(UnitTypeId.ASSIMILATOR, gaiser))
        return True

    async def buildExpansion(self):
        if self.instance.units(UnitTypeId.NEXUS).amount < 2 and not self.instance.already_pending(UnitTypeId.NEXUS):
            if self.instance.units(UnitTypeId.ZEALOT).amount >= 2 and self.instance.can_afford(UnitTypeId.NEXUS):
                #await self.instance.expand_now()
                location = await self.instance.get_next_expansion()
                await self.instance.build(UnitTypeId.NEXUS, near=location, placement_step=1)
                return True

    async def haveNoGateway(self):
        return self.instance.units(UnitTypeId.GATEWAY).amount == 0

    async def needMoreGate(self):
        return self.instance.units(UnitTypeId.GATEWAY).amount + self.instance.already_pending(UnitTypeId.GATEWAY)< 4

    async def haveResourcesForGateway(self):
        return self.instance.can_afford(UnitTypeId.GATEWAY)

    async def buildGateway(self):
        await self.build_structure(UnitTypeId.GATEWAY, 16, 1)

    async def build_structure(self, unit_type, min_workers, desired_units):
        if self.instance.workers.amount >= min_workers:
            nexus = self.instance.units(UnitTypeId.NEXUS).ready.random
            if len(self.instance.units(unit_type)) < desired_units and not self.instance.already_pending(unit_type):
                if self.instance.can_afford(unit_type):
                    await self.instance.build(unit_type, near=nexus)
        return True

    async def shouldBuildStarGate(self):
        return self.instance.units(UnitTypeId.STARGATE).ready.amount + self.instance.already_pending(UnitTypeId.STARGATE) < 3

    async def buildStarGate(self):
        if self.instance.can_afford(UnitTypeId.STARGATE):
            print("Build StarGate")
            nexus = self.instance.units(UnitTypeId.NEXUS).ready.random
            await self.instance.build(UnitTypeId.STARGATE,
                                      near=nexus.position.towards(self.instance.game_info.map_center, distance=25))
            return True
        return False

    async def arleadyHaveCyberCore(self):
        return self.instance.units(UnitTypeId.CYBERNETICSCORE).ready.exists and \
               not self.instance.already_pending(UnitTypeId.CYBERNETICSCORE)

    async def shouldBuildCyberneticsCore(self):
        if not self.instance.units(UnitTypeId.CYBERNETICSCORE).exists and not self.instance.already_pending(UnitTypeId.CYBERNETICSCORE):
            return len(self.instance.units(UnitTypeId.ZEALOT)) >= 3
        return False

    async def canBuildCyberneticCore(self):
        return self.instance.can_afford(UnitTypeId.CYBERNETICSCORE)

    async def buildCyberneticsCore(self):
        if self.instance.can_afford(UnitTypeId.CYBERNETICSCORE):
            nexus = self.instance.units(UnitTypeId.NEXUS).ready.random
            await self.instance.build(UnitTypeId.CYBERNETICSCORE,
                                      near=nexus.position.towards(self.instance.game_info.map_center, distance=10))
            return True
        return False

    async def buildSeveralGateways(self):
        if self.instance.units(UnitTypeId.GATEWAY).amount > 4:
            return False
        nexus = self.instance.units(UnitTypeId.NEXUS).ready.random
        if self.instance.can_afford(UnitTypeId.GATEWAY):
            await self.instance.build(UnitTypeId.GATEWAY,
                                      near=nexus.position.towards(self.instance.game_info.map_center, distance=20))
            return True
        return False

    async def shouldBuildForge(self):
        if not self.instance.units(UnitTypeId.FORGE).exists and not self.instance.already_pending(UnitTypeId.FORGE):
            return len(self.instance.units(UnitTypeId.ZEALOT)) >= 3
        return False

    async def canBuildForge(self):
        return self.instance.can_afford(UnitTypeId.FORGE)

    async def buildForge(self):
        nexus = self.instance.units(UnitTypeId.NEXUS).ready.random
        await self.instance.build(UnitTypeId.FORGE,
                                  near=nexus.position.towards(self.instance.game_info.map_center, distance=10))
        return True

    async def shouldBuildRoboticsFacility(self):
        if self.instance.units(UnitTypeId.ROBOTICSFACILITY).exists or self.instance.already_pending(UnitTypeId.ROBOTICSFACILITY):
            return False
        return self.instance.units(UnitTypeId.STARGATE).exists or self.instance.already_pending(UnitTypeId.STARGATE)

    async def canBuildRoboticsFacility(self):
        return self.instance.can_afford(UnitTypeId.ROBOTICSFACILITY)

    async def buildRoboticsFacility(self):
        nexus = self.instance.units(UnitTypeId.NEXUS).ready.random
        await self.instance.build(UnitTypeId.ROBOTICSFACILITY,
                                  near=nexus.position.towards(self.instance.game_info.map_center, distance=15))
        return True


action = Action(None)


def defAction(instance):
    global action
    action.instance = instance


#Initial one
s1 =DoAllSequence(
    Atomic(action.boost),
    Conditional(action.lowOnResources,
        Conditional(action.canBuildPylons,
            Atomic(action.buildPylons)
        )
    ),
    ConditionalElse(action.arleadyHaveCyberCore, #If we have a cybercore we need more gateways
        Conditional(action.needMoreGate,
                    Atomic(action.buildSeveralGateways)
        ),
        Conditional(action.haveNoGateway, #Other wise we only need one
            Conditional(action.haveResourcesForGateway,
                Atomic(action.buildGateway)
            )
        )
    ),
    #Atomic(action.buildGateway),
    Atomic(action.buildProbes),
    Atomic(action.buildAssimilator),
    Atomic(action.buildExpansion),
    Conditional(action.shouldBuildCyberneticsCore,#Should we have one?
        Conditional(action.canBuildCyberneticCore,
            Atomic(action.buildCyberneticsCore),
        ),
    ),
    # Conditional(action.shouldBuildForge,#Should we have one?
    #     Conditional(action.canBuildForge,
    #         Atomic(action.buildForge),
    #     ),
    # ),
    Conditional(army.action.hasAttackedBase,
        Conditional(action.shouldBuildStarGate,
            Atomic(action.buildStarGate)
        ),
    ),
    Conditional(action.shouldBuildRoboticsFacility,  #Should we have one?
        Conditional(action.canBuildRoboticsFacility,
            Atomic(action.buildRoboticsFacility)
        ),
    ),
)


async def runTree():
    global action
    if action is not None:
        await s1.run()
    else:
        return False
    return True
