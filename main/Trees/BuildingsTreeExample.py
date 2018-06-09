
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
    def __init__(self,inst):
        self.instance = inst

    async def on_step(self,iteration):
        await self.expand()
        await self.buildPylons()
        await self.buildProbe()

    async def expand(self):
        print("expand")
        nexus = self.instance.units(UnitTypeId.NEXUS).ready.random
        if not nexus.has_buff(BuffId.CHRONOBOOSTENERGYCOST):
            abilities = await self.instance.get_available_abilities(nexus)
            if AbilityId.EFFECT_CHRONOBOOSTENERGYCOST in abilities:
                await self.instance.do(nexus(AbilityId.EFFECT_CHRONOBOOSTENERGYCOST, nexus))
                return True
        return False

    async def buildProbs(self):
        nexus = self.instance.units(UnitTypeId.NEXUS).ready.random
        if self.instance.workers.amount < self.instance.units(UnitTypeId.NEXUS).amount*15 and nexus.noqueue:
            if self.instance.can_afford(UnitTypeId.PROBE):
                await self.instance.do(nexus.train(UnitTypeId.PROBE))
        return True

    async def buildPylons(self):
        nexus = self.instance.units(UnitTypeId.NEXUS).ready.random
        if not self.instance.units(UnitTypeId.PYLON).exists and not self.instance.already_pending(UnitTypeId.PYLON):
            if self.instance.can_afford(UnitTypeId.PYLON):
                await self.instance.build(UnitTypeId.PYLON, near=nexus)
        return True

action = Action(None)


def defAction(instance):
    global action
    action.instance = instance

s1 = Sequence(
    Atomic(action.expand),
    Atomic(action.buildPylons),
    Atomic(action.buildProbs)
)
        #s1.run()

async def runTree():
    global action
    if(not action is None):
        await s1.run()
    else:
        return False
    return True
