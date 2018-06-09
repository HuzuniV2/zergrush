import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer

import BehaviourTree
from BehaviourTree import  *

import sc2
from sc2.constants import *
#from mainBot import state

#isntance represents the bot itself, so we can tell it to do stuff
class Action():
    """A way of passing the variables"""

    def __init__(self):
        self.instance = None

    def __init__(self,inst):
        self.instance = inst

    async def rush_enemy_base(self):
        """Gets all the workers to rush the enemy base"""
        if self.instance.workers.amount == self.instance.units(UnitTypeId.NEXUS).amount*15:
            #for worker in self.instance.workers.idle:
            for worker in self.instance.workers:
                await self.instance.do(worker.attack(self.instance.enemy_start_locations[0]))
        return True

    #not needed
    async def gather_supplies(self):
        """make idols Gathers supplies """
        for worker in self.instance.workers.idle: #better possibility
        #for worker in self.instance.workers:
            mf = self.instance.state.mineral_field.closest_to(worker)
            await self.instance.do(worker.gather(mf))
        return True

action = Action(None)


def defAction(instance):
    global action
    action.instance = instance

s1 = Sequence(
    Atomic(action.gather_supplies),
    Atomic(action.rush_enemy_base)
)
        #s1.run()

async def runTree():
    global action
    if(not action is None):
        await s1.run()
    else:
        return False
    return True

