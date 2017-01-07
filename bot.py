import requests
from random import choice
from game import Game

def path_find(game, start, target):
    try:
        r = requests.get('http://game.blitz.codes:8081/pathfinding/direction',
                         params={'map': game.state['game']['board']['tiles'],
                                 'size': game.state['game']['board']['size'],
                                 'start': '(%d,%d)' % start,
                                 'target': '(%d,%d)' % target})
        json = r.json()
        return json.get('direction', None)
    except e:
        print('Pathfinder as a Service failed')
        return None


class Bot:
    pass


class RandomBot(Bot):
    def move(self, state):
        game = Game(state)
        dirs = ['Stay', 'North', 'South', 'East', 'West']
        return choice(dirs)
