import random

import sc2
from sc2 import Race, Difficulty
from sc2.constants import *
from sc2.player import Bot, Computer

import BehaviourTree
from BehaviourTree import  *
import sharedInfo
#from mainBot import state

hasUpgradedGroundWeapon = False
hasUpgradedGroundArmor = False
hasUpgradedShields = False

# instance represents the bot itself, so we can tell it to do stuff
class Action:
    """A way of passing the variables"""
    def __init__(self, inst):
        self.instance = inst

    async def hasForge(self):
        return self.instance.units(UnitTypeId.FORGE).ready.exists

    async def canAffordGroundArmor(self):
        return self.instance.can_afford(AbilityId.RESEARCH_PROTOSSGROUNDARMOR)

    async def upgradeGroundAmor(self):
        forge = self.instance.units(UnitTypeId.FORGE).ready.first
        await self.instance.do(forge(AbilityId.RESEARCH_PROTOSSGROUNDARMOR))
        return True

    async def canAffordGroundWeapon(self):
        return self.instance.can_afford(AbilityId.RESEARCH_PROTOSSGROUNDWEAPONS)

    async def upgradeGroundWeapon(self):
        forge = self.instance.units(UnitTypeId.FORGE).ready.first
        await self.instance.do(forge(AbilityId.RESEARCH_PROTOSSGROUNDWEAPONS))
        return True

    async def canAffordShields(self):
        return self.instance.can_afford(AbilityId.RESEARCH_PROTOSSSHIELDS)

    async def upgradeShields(self):
        forge = self.instance.units(UnitTypeId.FORGE).ready.first
        await self.instance.do(forge(AbilityId.RESEARCH_PROTOSSSHIELDS))
        return True

action = Action(None)


def defAction(instance):
    global action
    action.instance = instance


#Initial one
s1 =Sequence(
    Atomic(action.hasForge), #Check if we havea forge
    OptionalConditional(action.canAffordGroundArmor,Atomic(action.upgradeGroundAmor)),
    OptionalConditional(action.canAffordGroundWeapon,Atomic(action.upgradeGroundWeapon)),
    OptionalConditional(action.canAffordShields,Atomic(action.upgradeShields)),
)


async def runTree():
    global action
    if action is not None:
        await s1.run()
    else:
        return False
    return True
