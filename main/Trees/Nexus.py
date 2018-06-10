
import random

import sc2
from sc2 import Race, Difficulty
from sc2.constants import *
from sc2.player import Bot, Computer

import BehaviourTree
from BehaviourTree import  *

#from mainBot import state

#isntance represents the bot itself, so we can tell it to do stuff
class Action():
    """A way of passing the variables"""
    def __init__(self, inst):
        self.instance = inst

    async def on_step(self, iteration):
        await self.boost()
        await self.buildPylons()
        await self.buildProbes()
        await self.buildAssimilator()
        await self.buildGateway()

    async def boost(self):
        print("Boost struct")
        gateways = []
        for gate in self.instance.units(UnitTypeId.GATEWAY):
            gateways.append(gate)
        nexus = self.instance.units(UnitTypeId.NEXUS).ready.random
        if not nexus.has_buff(BuffId.CHRONOBOOSTENERGYCOST):
            abilities = await self.instance.get_available_abilities(nexus)
            if AbilityId.EFFECT_CHRONOBOOSTENERGYCOST in abilities:
                if self.instance.units(UnitTypeId.PROBE).amount < 15 and not nexus.noqueue :
                    await self.instance.do(nexus(AbilityId.EFFECT_CHRONOBOOSTENERGYCOST, nexus))
                    return True
                elif any(not gate.noqueue for gate in gateways):
                    for gate in gateways:
                        if not gate.noqueue :
                            await self.instance.do(nexus(AbilityId.EFFECT_CHRONOBOOSTENERGYCOST, nexus))
                            break
                    return True
        return False

    async def buildProbes(self):
        nexus = self.instance.units(UnitTypeId.NEXUS).ready.random
        if self.instance.can_afford(UnitTypeId.PROBE):
            if nexus.assigned_harvesters < nexus.ideal_harvesters and nexus.noqueue:
                await self.instance.do(nexus.train(UnitTypeId.PROBE))
        #for nexus in self.instance.units(UnitTypeId.NEXUS):
            #if nexus.assigned_harvesters < nexus.ideal_harvesters:
                #if self.instance.can_afford(UnitTypeId.PROBE) and not self.instance.already_pending(UnitTypeId.PROBE):
                    #await self.instance.do(nexus.train(UnitTypeId.PROBE))
        return True

    async def buildPylons(self):
        nexus = self.instance.units(UnitTypeId.NEXUS).ready.random
        if self.instance.supply_left <= 0:
            if self.instance.can_afford(UnitTypeId.PYLON) and not self.instance.already_pending(UnitTypeId.PYLON):
                await self.instance.build(UnitTypeId.PYLON, near=nexus)
        return True

    async def buildAssimilator(self):
        nexus = self.instance.units(UnitTypeId.NEXUS).ready.random
        if nexus.assigned_harvesters >= 16:
            if self.instance.can_afford(UnitTypeId.ASSIMILATOR) and not self.instance.already_pending(UnitTypeId.ASSIMILATOR):
                builder = self.instance.workers.random
                building_placement = self.instance.state.vespene_geyser.closest_to(builder.position)
                await self.instance.do(builder.build(UnitTypeId.ASSIMILATOR, building_placement))
                return True

    async def buildGateway(self):
        await self.build_structure(UnitTypeId.GATEWAY, 16, 1)

    async def build_structure(self, unit_type, min_workers, desired_units):
        if self.instance.workers.amount >= min_workers:
            nexus = self.instance.units(UnitTypeId.NEXUS).ready.random
            if len(self.instance.units(unit_type)) < desired_units and not self.instance.already_pending(unit_type):
                if self.instance.can_afford(unit_type):
                    await self.instance.build(unit_type, near=nexus)
        return True


action = Action(None)


def defAction(instance):
    global action
    action.instance = instance

s1 = Sequence(
    Atomic(action.boost),
    Atomic(action.buildPylons),
    Atomic(action.buildGateway),
    Atomic(action.buildProbes),
    Atomic(action.buildAssimilator)
)
        #s1.run()

async def runTree():
    global action
    if(not action is None):
        await s1.run()
    else:
        return False
    return True
