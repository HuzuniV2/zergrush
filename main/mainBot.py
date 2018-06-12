__author__ = 'fc45701'

import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
import random
import time
from threading import Thread

import BehaviourTree
import Trees.WorkerTreeExample

from BehaviourTree import *

from multiprocessing import Process
import MainBehaviorTree

####
#What we know
# Can't use yield
# Need to use async and await
###
#The idea iswe use the same thread for everything
#Ideia: Async the looking up factore in the tree it self, maybe append the functions found by the tree into a list
# and then await them,maybe even just have mini bots that do the thing at the end
class WorkerRushBotTree(sc2.BotAI):

    #removed wait
    async def on_step(self, iteration):
        if iteration == 0:
            await self.chat_send("(glhf)")
        await MainBehaviorTree.startRunning(self)


        #self.mineral_contents

#Example of what we would need to do before, not needed for our project
class OriginalWorkerRushBot(sc2.BotAI):
    async def on_step(self, iteration):
        await self.distribute_workers()
        await self.gather_supplies()

    async def rush_base(self):
        for worker in self.workers:
            if self.minerals > 200:
                await self.do(worker.attack(self.enemy_start_locations[0]))
            else:
                return False
    async def gather_supplies(self):
        for worker in self.workers:
            if self.minerals > 200:
                await self.do(worker.gather(self.state.mineral_field[0]))

def main():
    run_game(maps.get("Abyssal Reef LE"), [
        Bot(Race.Protoss, WorkerRushBotTree()),
        Computer(Race.Zerg, Difficulty.Hard)
    ], realtime=True)
    #MainBehaviorTree.startRunning(1)

if __name__ == '__main__':
    main()