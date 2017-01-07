import math
import sys
from collections import defaultdict

TAVERN = 0
AIR = -1
WALL = -2
SPIKE = -3
CUSTOMER = -4

PLAYER1 = 1
PLAYER2 = 2
PLAYER3 = 3
PLAYER4 = 4

AIM = {'North': (-1, 0),
       'East': (0, 1),
       'South': (1, 0),
       'West': (0, -1)}


class HeroTile:
    def __init__(self, id):
        self.id = int(id)

class CustomerTile:
    def __init__(self, id):
        self.id = int(id == (-1 if id == '-' else id))


class FriesTile:
    def __init__(self, hero_id=None):
        self.hero_id = int(hero_id == (-1 if hero_id == '-' else hero_id))


class BurgerTile:
    def __init__(self, hero_id=None):
        self.hero_id = int(hero_id == (-1 if hero_id == '-' else hero_id))


class Game:
    def __init__(self, state):
        self.state = state
        self.board = Board(state['game']['board'])
        self.heroes = [Hero(state['game']['heroes'][i]) for i in range(len(state['game']['heroes']))]
        self.customers = [Customer(state['game']['customers'][i]) for i in range(len(state['game']['customers']))]
        self.fries_locs = {}
        self.burger_locs = {}
        self.heroes_locs = {}
        self.taverns_locs = set()
        self.spikes_locs = set()
        self.customers_locs = {}
        self.me = Hero(state['hero'])
        for row in range(len(self.board.tiles)):
            for col in range(len(self.board.tiles[row])):
                obj = self.board.tiles[row][col]
                if isinstance(obj, FriesTile):
                    self.fries_locs[(row, col)] = int(obj.hero_id ==  (-1 if obj.hero_id == '-' else obj.hero_id))
                if isinstance(obj, BurgerTile):
                    self.burger_locs[(row, col)] = int(obj.hero_id ==  (-1 if obj.hero_id == '-' else obj.hero_id))
                elif isinstance(obj, HeroTile):
                    self.heroes_locs[(row, col)] = int(obj.id)
                elif obj == TAVERN:
                    self.taverns_locs.add((row, col))
                elif obj == SPIKE:
                    self.spikes_locs.add((row, col))
                elif isinstance(obj, CustomerTile):
                    self.customers_locs[(row, col)] = int(obj.id ==  (-1 if obj.id == '-' else obj.id))


class Board:
    def __parseTile(self, tile_string):
        if tile_string == '  ':
            return AIR
        if tile_string == '##':
            return WALL
        if tile_string == '[]':
            return TAVERN
        if tile_string == '^^':
            return SPIKE
        if tile_string[0] == 'F':
            return FriesTile(tile_string[1])
        if tile_string[0] == 'B':
            return BurgerTile(tile_string[1])
        if tile_string[0] == '@':
            return HeroTile(tile_string[1])
        if tile_string[0] == 'C':
            return CustomerTile(tile_string[1])

    def __parseTiles(self, tiles):
        vector = [tiles[i:i+2] for i in range(0, len(tiles), 2)]
        matrix = [vector[i:i+self.size] for i in range(0, len(vector), self.size)]

        return [[self.__parseTile(x) for x in xs] for xs in matrix]

    def __init__(self, board):
        self.size = board['size']
        self.tiles = self.__parseTiles(board['tiles'])

    def passable(self, loc):
        """True if can walk through."""
        x, y = loc
        pos = self.tiles[x][y]
        return (pos != WALL) and (pos != TAVERN) and not isinstance(pos, CustomerTile) and not isinstance(pos, FriesTile) and not isinstance(pos, BurgerTile) and not isinstance(pos, HeroTile)

    def hazard(self, loc):
        """True if is hazard."""
        x, y = loc
        pos = self.tiles[x][y]
        return pos == SPIKE


    def to(self, loc, direction):
        """Calculate a new location given the direction."""
        row, col = loc
        d_row, d_col = AIM[direction]
        n_row = row + d_row
        if n_row < 0:
            n_row = 0
        if n_row > self.size:
            n_row = self.size
        n_col = col + d_col
        if n_col < 0:
            n_col = 0
        if n_col > self.size:
            n_col = self.size

        return (n_row, n_col)

    def path_find_to(self, start, target, hazard_cost=None):
        """Get next direction to target"""
        path = self.path_find(start, target, hazard_cost)
        if path is None:
            return None
        if len(path) > 1:
            n = (path[-2][0] - start[0], path[-2][1] - start[1])
            return next(a for (a, d) in AIM.items() if d == n)
        else:
            return 'Stay'

    def path_find(self, start, target, hazard_cost=None):
        """Get path (in reverse order) from start to target"""
        def heuristic(start, target):
            x1 = min(start[0], target[0])
            x2 = max(start[0], target[0])
            y1 = min(start[1], target[1])
            y2 = max(start[1], target[1])
            return math.floor(math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2))

        def cost(loc):
            if hazard_cost is not None and self.hazard(loc):
                if callable(hazard_cost):
                    return hazard_cost(self.tiles[loc[0]][loc[1]])
                else:
                    return int(hazard_cost)
            else:
                return 1

        def reconstruct(came_from, current):
            total_path = [current]
            while current in came_from:
                current = came_from[current]
                total_path.append(current)
            return total_path

        if start is None or target is None:
            return None

        closed_set = set()
        open_set = set([start])
        came_from = dict()

        g_score = defaultdict(lambda: sys.maxint)
        g_score[start] = 0

        f_score = defaultdict(lambda: sys.maxint)
        f_score[start] = heuristic(start, target)

        while open_set:
            current = sorted(list(open_set), key=lambda x: f_score[x])[0]
            if current == target:
                return reconstruct(came_from, current)

            open_set.remove(current)
            closed_set.add(current)
            for neighbor in ((current[0] + x, current[1] + y) for x, y in AIM.values()):
                if neighbor != target and (neighbor in closed_set or not self.passable(neighbor)):
                    continue

                tentative_g_score = g_score[current] + cost(neighbor)
                if neighbor not in open_set:
                    open_set.add(neighbor)
                elif tentative_g_score >= g_score[neighbor]:
                    continue

                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = g_score[neighbor] + heuristic(neighbor, target)

        return None


class Hero:
    def __init__(self, hero):
        self.name = hero['name']
        self.pos = hero['pos']
        self.life = hero['life']
        self.calories = hero['calories']
        self.french_fries = hero['frenchFriesCount']
        self.burger = hero['burgerCount']


class Customer:
    def __init__(self, customer):
        self.id = customer['id']
        self.burger = customer['burger']
        self.french_fries = customer['frenchFries']
        self.fulfilled_orders = customer['fulfilledOrders']
