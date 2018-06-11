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
        self.closest_enemy = None

    async def enemyUnitsClose(self):
        max_structs = 0
        enemy_units = self.instance.known_enemy_units
        if not enemy_units:
            self.closest_enemy = None
            return False
        MIN_ENEMY_RADIUS = 70
        NEXUS_RADIUS = 20

        defend_nexus = None
        closest_enemy = None
        structures = self.instance.units.structure
        for nexus in self.instance.units(UnitTypeId.NEXUS):
            closest = min([(enemy, enemy.position.distance_to(nexus.position)) for enemy in enemy_units],
                          key=lambda e: e[1])
            if closest[1] < MIN_ENEMY_RADIUS:
                # enemy close to nexus!
                close_structs = len([1 for s in structures if s.position.distance_to(nexus.position) < NEXUS_RADIUS])
                if defend_nexus is None or close_structs > max_structs:
                    defend_nexus = nexus
                    closest_enemy = closest[0]

        if not defend_nexus:
            self.closest_enemy = None
            return False
        self.closest_enemy = closest_enemy
        return True

    async def defendBaseWithAll(self):
        if not self.closest_enemy:
            return False
        print("Defend!")
        for stalker in self.instance.units(UnitTypeId.STALKER).idle:
            await self.instance.do(stalker.attack(self.closest_enemy))
        for zealot in self.instance.units(UnitTypeId.ZEALOT).idle:
            await self.instance.do(zealot.attack(self.closest_enemy))
        for vr in self.instance.units(UnitTypeId.VOIDRAY).idle:
            await self.instance.do(vr.attack(self.closest_enemy))
        self.closest_enemy = None
        return True

    async def returnToBase(self):
        DEFENSE_RADIUS = 60
        defense_base_position = self.instance.start_location.towards(self.instance.game_info.map_center,
                                                                     distance=DEFENSE_RADIUS - 20)
        for unit in [UnitTypeId.STALKER, UnitTypeId.ZEALOT, UnitTypeId.VOIDRAY]:
            for u in list([u for u in self.instance.units(unit)
                           if u.position.distance_to(self.instance.start_location) > DEFENSE_RADIUS]):
                await self.instance.do(u.move(defense_base_position))
        return True

    async def troopsExisting(self):
        for unit in [UnitTypeId.STALKER, UnitTypeId.ZEALOT, UnitTypeId.VOIDRAY]:
            if len(self.instance.units(unit)) > 0:
                return True
        return False


action = Action(None)


def defAction(instance):
    global action
    action.instance = instance


#TREE
s1 = Conditional(action.troopsExisting,
                 Selector(
                     Conditional(action.enemyUnitsClose,
                                 Atomic(action.defendBaseWithAll)),
                     Atomic(action.returnToBase),
                 ),
     )


async def runTree():
    global action
    if action is not None:
        await s1.run()
    else:
        return False
    return True
