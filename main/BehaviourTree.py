__author__ = 'LuisMoniz'


import random
import time
from threading import Thread

from multiprocessing import Process

class Atomic():
    """
    Abstract implementation of an atomic action
    """
    def __init__(self, func):
        self.func = func

    async def run(self):
        #print self.func.__name__
        return await self.func()


class Task(object):
    """ Abstract Task implementation
    """

    def __init__(self):
        super(Task,self).__init__()

    def __init__(self,*children):
        self._children = []
        for child in children:
            self._children.append(child)

    def run(self):
        pass
        #await None


class Selector(Task):
    """   Selector Implementation   """

    async def run(self):
        for c in self._children:
            n = False
            #if isinstance(c, (Conditional)):
            #    n = c.run()
            #else:
            n = await c.run()
            #print (c, " = ", n)
            if n is True:
                return True
        return False

#TODO -< still can't be used
class RandomSelector(Selector):
    """   Random Implementation   """

    def run(self):
        while True :
            if random.choice(self._children).run() :
                return True
        return False


#TODO -< still can't be used
class NonDeterministicSelector(Selector):
    """   NonDeterministicSelector Implementation   """

    def run(self):
        shuffled = random.shuffle(self._children)
        for c in shuffled :
            if c.run() :
                return True
        return False



class Sequence(Task):
    """   Sequence Implementation   """

    async def run(self):
        for c in self._children :
            n = await c.run()
            if n is False:
                return False
        return True

class NonDeterministicSequence(Task):
    """   NonDeterministicSequence Implementation   """

    async def run(self):
        print ("Children: ",self._children)
        shuffled = self._children
        random.shuffle(shuffled)
        print("Children Shuffled: ", shuffled)
        for c in shuffled :
            n = await c.run()
            if n is False:
                return False
        return True


class Decorator(Task):

    def __init__(self,child):
        super(Decorator,self).__init__(self)
        self._child = child

class Conditional(Decorator):
    """ IF condition is true executes all the children
        OtherWise returns True          """

    def __init__(self, func,child):
        super().__init__(child)
        self.func = func
        self.child = child

    async def run(self):
        # print self.func.__name__
        bool = await self.func()
        print(self.func())
        if bool:
            return await self.child.run()
        return False
        #return self.func()

class Limit(Decorator):
    """ Counter Decorator Implementation
    """
    def __init__(self,limit,child):
        super(Limit,self).__init__(child)
        self._runLimit = limit


    async def run(self):
        if self._runLimit > 0:
            self._runLimit -= 1
            return await self._child.run()
        return False

class UntilFail(Decorator):
    """ UntilFail Decorator Implementation
    """

    async def run(self):
        #while self._child.run():
        passed = True
        while passed:
            n = await self._child.run() #returns more than just True or False
            passed = (n is False)
            print (passed)
        #while self._child.run():
        #    pass
        return True

#TODO -< still can't be used
class Wait(Decorator):
    """ Wait implementation
    """
    def __init__(self,duration,child):
        super(Wait,self).__init__(child)
        self._duration = duration

    def run(self):
        time.sleep(self._duration)
        return self._child.run()


class Inverter(Decorator):
    """ Inverter implementation
    """
    def __init__(self,child):
        super(Inverter,self).__init__(child)


    async def run(self):
        bool = await self._child.run()
        return not bool



#Definicao de acoes atomicas (devem ter todas o run() booleano)
#Examples
def a1():
    print ("xxx")
    time.sleep(0.1)
    return True

def a2():
    print ("aaa")
    time.sleep(0.1)
    return True

def a3():
    print ("DOD")
    time.sleep(0.1)
    return True

def a4():
    print ("OPO")
    time.sleep(0.1)
    return True

def a5():
    print ("XXX")
    time.sleep(0.1)
    return True

def a6():
    print ("AAA")
    return True




#if __name__ == '__main__':
#    s1 = Parallel(
#            UntilFail(
#                Limit(5,
#                      Sequence(
#                          Atomic(a1),
#                          Atomic(a2)))),
#            UntilFail(
#                Limit(5,
#                      Sequence(
#                          Atomic(a3),
#                          Atomic(a4)))),
#            Sequence(
#                Atomic(a5),
#                Wait(5,
#                     Atomic(a6))))
#    s1.run()
