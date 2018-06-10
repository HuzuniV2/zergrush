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

    async def shouldBuildCyberneticsCore(self):
        if not self.instance.units(UnitTypeId.CYBERNETICSCORE).exists and not self.instance.already_pending(UnitTypeId.CYBERNETICSCORE):
            return len(self.instance.units(UnitTypeId.ZEALOT)) >= 4
        return False


action = Action(None)


def defAction(instance):
    global action
    action.instance = instance


s1 = Selector(
    Conditional(action.shouldBuildCyberneticsCore,
                Atomic(action.buildCyberneticsCore)),
    Atomic(action.trainZealots),
)


async def runTree():
    global action
    if action is not None:
        await s1.run()
    else:
        return False
    return True
