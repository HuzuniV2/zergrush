__author__ = 'fc45701'

game_state = None

def setState(state):
    global game_state
    game_state = state

def getState():
    return game_state