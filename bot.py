import config
from random import choice
from game import Game, CustomerTile, BurgerTile, FriesTile, HeroTile, SPIKE, AIM


class Bot:
    def move(self, state):
        try:
            print('\n')
            game = Game(state)
            start = (game.me.pos['x'], game.me.pos['y'])
            target = self.get_target(game)
            print('From', start, 'to', target, end=' ')
            return game.board.path_find_to(start=start,
                                           target=target,
                                           hazard_cost=lambda t: self.assess_hazard(game, t)) or 'Stay'
        except Exception as e:
            print(e)
            return choice(['Stay'] + list(AIM.keys()))

    def get_target(self, game):
        """Returns the position we want to head towards"""
        customer = self.easiest_customer(game)

        unowned_nearby_resource_position = self.unowned_nearby_resource_position(game)
        nearby_health_position = self.nearby_health_position(game)

        if nearby_health_position:
            print('Going for nearby health')
            return nearby_health_position
        elif game.me.life < config.CRITICAL_LIFE:
            health_position = self.closest_health_location(game)
            print('Going for health at', health_position)
            return health_position
        elif unowned_nearby_resource_position:
            print('Going for nearby resource')
            return unowned_nearby_resource_position
        elif self.sufficient_resources_for(game, customer):
            print('Sufficient resources for customer', customer.id)
            customer_position = self.find_customer_position(game, customer.id)
            print('Customer is at:', customer_position)
            return customer_position
        else:
            print('Getting resources for customer ' + str(customer.id))
            return self.get_nearest_needed_resource_position(game, customer)

    def assess_hazard(self, game, tile):
        """Get weight for passing through unsafe stuff"""
        if isinstance(tile, HeroTile) and tile.id != game.me.id:
            enemy = next(h for h in game.heroes if h.id == tile.id)
            if enemy.life < game.me.life and game.me.life > config.CRITICAL_LIFE:
                return 1
            else:
                return int(config.HAZARD_FACTOR * 100) - int(config.HAZARD_FACTOR * game.me.life) + 1
        elif tile == SPIKE:
            return int(config.HAZARD_FACTOR * 100) - int(config.HAZARD_FACTOR * game.me.life) + 1
        return 1

    def easiest_customer(self, game):
        """Returns the customer that requires the less resources"""

        customer_positions = dict([(customer.id, self.find_customer_position(game, customer.id)) for customer in game.customers])

        def customer_difficulty(customer):
            customer_pos = customer_positions[customer.id]

            distance = len(game.board.path_find((game.me.pos['x'], game.me.pos['y']), customer_pos)[1])
            base_score = customer.french_fries + customer.burger + distance * config.STEP_COST_VS_RESOURCES
            multiplier = max(0, min(1, (distance - 3) / 10)) if self.sufficient_resources_for(game, customer) else 1

            # print('base_score: ' + str(base_score))
            if multiplier < 0.4:
                print('Low multiplier: ' + str(multiplier))
            # print('total_score: ' + str(base_score * multiplier))

            return base_score * multiplier

        customers = sorted(game.customers, key=customer_difficulty)

        print('Customer to find: ' + str(customers[0].id))

        return customers[0]

    def find_customer_position(self, game, customer_id):
        """The passed customer's position"""

        tiles = game.board.tiles

        for (y, tile_row) in enumerate(tiles):
            for (x, tile_column) in enumerate(tile_row):
                tile = tiles[x][y]

                if isinstance(tile, CustomerTile):
                    if tile.id == customer_id:
                        return (x, y)

    def sufficient_resources_for(self, game, customer):
        """Do we have sufficient resources for the passed customer?"""

        return (game.me.french_fries >= customer.french_fries
                and game.me.burger >= customer.burger)

    def get_nearest_needed_resource_position(self, game, customer):
        """The position of the closest resource necessary for the customer"""

        def distance_to_me(position):
            return abs(game.me.pos['x'] - position[0]) + abs(game.me.pos['y'] - position[1])

        if game.me.french_fries < customer.french_fries:
            pos_of_fries_we_dont_have = [pos for (pos, hero_id) in game.fries_locs.items() if hero_id != game.me.id]
            if len(pos_of_fries_we_dont_have) == 0:
                return random_position(game)
            target_position = sorted(pos_of_fries_we_dont_have, key=distance_to_me)[0]
            print('We need fries! the closest is:', target_position)
        else:
            pos_of_burgers_we_dont_have = [pos for (pos, hero_id) in game.burger_locs.items() if hero_id != game.me.id]
            if len(pos_of_burgers_we_dont_have) == 0:
                return random_position(game)
            target_position = sorted(pos_of_burgers_we_dont_have, key=distance_to_me)[0]
            print('We need burgers! the closest is:', target_position)

        return target_position

    def unowned_nearby_resource_position(self, game):
        x, y = game.me.pos['x'], game.me.pos['y']
        size = len(game.board.tiles)

        tiles_to_check = [((x, y), game.board.tiles[x][y]) for (x, y) in [
            (x+1, y),
            (x-1, y),
            (x, y-1),
            (x, y+1)
        ] if x >= 0 and x < size and y >= 0 and y < size]

        nearby_resource_positions = [(x, y) for ((x, y), t) in tiles_to_check if (isinstance(t, FriesTile) or isinstance(t, BurgerTile)) and t.hero_id != game.me.id]

        if (len(nearby_resource_positions) == 0):
            return None

        return nearby_resource_positions[0]

    def nearby_health_position(self, game):
        if game.me.life > config.MINIMUM_LIFE_BEFORE_HEAL:
            return None

        if game.me.calories < config.HEAL_PRICE:
            return None

        x, y = game.me.pos['x'], game.me.pos['y']
        size = len(game.board.tiles)

        tiles_to_check = [((x, y), game.board.tiles[x][y]) for (x, y) in [
            (x+1, y),
            (x-1, y),
            (x, y-1),
            (x, y+1)
        ] if x >= 0 and x < size and y >= 0 and y < size]

        nearby_health_positions = [(x, y) for ((x, y), t) in tiles_to_check if (x, y) in game.taverns_locs]

        if (len(nearby_health_positions) == 0):
            return None

        return nearby_health_positions[0]

    def closest_health_location(self, game):
        def distance_to_me(position):
            return abs(game.me.pos['x'] - position[0]) + abs(game.me.pos['y'] - position[1])

        return sorted(game.taverns_locs, key=distance_to_me)[0]


def random_position(game):
    return game.board.to((game.me.pos['x'], game.me.pos['y']), choice(AIM.keys()))
