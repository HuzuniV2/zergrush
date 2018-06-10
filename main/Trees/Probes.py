
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
        await self.gotoGas()
        await self.gotoMField

    async def gotoGas(self):
        if self.instance.workers.amount >= 16:
            for assimilator in self.instance.units(UnitTypeId.ASSIMILATOR):
                if assimilator.assigned_harvesters < assimilator.ideal_harvesters:
                    worker = self.instance.workers.closer_than(20, assimilator)
                    if worker.exists:
                        await self.instance.do(worker.random.gather(assimilator))
        return True

    async def gotoMField(self):
        for mfield in self.instance.units(UnitTypeId.MINERALFIELD):
            if mfield.assigned_harvesters < mfield.ideal_harvesters:
                worker = self.instance.workers.closer_than(40, mfield)
                if worker.exists and worker.idle:
                    await self.instance.do(worker.random.gather(mfield))
        return True
action = Action(None)


def defAction(instance):
    global action
    action.instance = instance

s1 = Sequence(
    Atomic(action.gotoGas),
    Atomic(action.gotoMField)
)
        #s1.run()

async def runTree():
    global action
    if(not action is None):
        await s1.run()
    else:
        return False
    return True
