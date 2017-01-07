import re

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
        self.id = id


class FriesTile:
    def __init__(self, hero_id=None):
        self.hero_id = hero_id


class BurgerTile:
    def __init__(self, hero_id=None):
        self.hero_id = hero_id


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
        self.customers_locs = set()
        for row in range(len(self.board.tiles)):
            for col in range(len(self.board.tiles[row])):
                obj = self.board.tiles[row][col]
                if isinstance(obj, FriesTile):
                    self.fries_locs[(row, col)] = obj.hero_id
                if isinstance(obj, BurgerTile):
                    self.burger_locs[(row, col)] = obj.hero_id
                elif isinstance(obj, HeroTile):
                    self.heroes_locs[(row, col)] = obj.id
                elif obj == TAVERN:
                    self.taverns_locs.add((row, col))
                elif obj == SPIKE:
                    self.spikes_locs.add((row, col))
                elif obj == CUSTOMER:
                    self.customers_locs.add((row, col))


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
        match = re.match(r'F([-0-9])', tile_string)
        if match:
            return FriesTile(match.group(1))
        match = re.match(r'B([-0-9])', tile_string)
        if match:
            return BurgerTile(match.group(1))
        match = re.match(r'@([0-9])', tile_string)
        if match:
            return HeroTile(match.group(1))
        match = re.match(r'C([0-9])', tile_string)
        if match:
            return CUSTOMER

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
        return (pos != WALL) and (pos != TAVERN) and (pos != CUSTOMER) and not isinstance(pos, FriesTile) and not isinstance(pos, BurgerTile)

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


class Hero:
    def __init__(self, hero):
        self.name = hero['name']
        self.pos = hero['pos']
        self.life = hero['life']
        self.calories = hero['calories']


class Customer:
    def __init__(self, customer):
        self.id = customer['id']
        self.burger = customer['burger']
        self.french_fries = customer['frenchFries']
        self.fulfilled_orders = customer['fulfilledOrders']
