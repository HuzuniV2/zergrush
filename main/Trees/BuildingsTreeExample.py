
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

    async def expand(self):
        print ("called")
        if not self.instance.units(PYLON).exists and not self.instance.already_pending(PYLON):
            if self.instance.can_afford(PYLON):
                await self.instance.build(PYLON, near=nexus)

action = Action(None)


def defAction(instance):
    global action
    action.instance = instance

s1 = Sequence(
    Atomic(action.expand)
)
        #s1.run()

async def runTree():
    print ("called")
    global action
    if(not action is None):
        await s1.run()
    else:
        return False
    return True
