__author__ = 'fc45701'

import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
import random
import time
from threading import Thread

import BehaviourTree
import Trees.WorkerTreeExample as worker
import Trees.BuildingsTreeExample as builder

from BehaviourTree import *

from multiprocessing import Process


#Add your tree here
s1 = Sequence(
    Atomic(worker.runTree), #run worker tree -> is not running the next atomic
    Atomic(builder.runTree)
)
        #s1.run()

#We have to pass the variable here
async def startRunning(self):
    #print ("Start running")
    worker.defAction(self)
    builder.defAction(self)
    await s1.run()

