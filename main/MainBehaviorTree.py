b__author__ = 'fc45701'

import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
import random
import time
from threading import Thread

import BehaviourTree
import Trees.WorkerTreeExample as worker
import Trees.BuildingsTreeExample as builder
import Trees.Nexus as nexus
import Trees.Probes as probes
import Trees.Army as army
import Trees.Defense as defense

from BehaviourTree import *
import sharedInfo
from multiprocessing import Process


#Add your tree here
s1 = Sequence(
    Atomic(worker.runTree), #run worker tree -> is not running the next atomic
    Atomic(nexus.runTree),
    Atomic(probes.runTree),
    Atomic(army.runTree),
   # Atomic(defense.runTree),
)


# We have to pass the variable here
async def startRunning(self):
    # print ("Start running")
    # sharedInfo.setState(self)
    worker.defAction(self)
    nexus.defAction(self)
    probes.defAction(self)
    army.defAction(self)
    #defense.defAction(self)
    await s1.run()
