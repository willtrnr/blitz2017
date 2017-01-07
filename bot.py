from game import Game


class Bot:
    def move(self, state):
        game = Game(state)
        target = self.get_target(game)
        start = (game.me.pos['x'], game.me.pos['y'])
        return game.board.path_find(start, target)

    def get_target(self, game):
        "Returns the position we want to head towards"
        customer = self.easiest_customer(game)

        if (self.sufficient_resources_for(game, customer)):
            return self.find_customer_position(game, customer)
        else:
            return self.get_nearest_needed_resource_position(game, customer)

    def easiest_customer(self, game):
        "Returns the customer that requires the less resources"

        def customer_difficulty(customer):
            return customer.french_fries + customer.burger

        return sorted(game.customers, key=customer_difficulty)[0]

    def find_customer_position(self, game, customer_id):
        "The passed customer's position"

        tiles = game.board.tiles

        for (y, tile_row) in enumerate(tiles):
            x = tile_row.index("C" + str(customer_id))

            if y is not None:
                return (x, y)

    def sufficient_resources_for(self, game, customer):
        "Do we have sufficient resources for the passed customer?"

        return game.me.french_fries >= customer.french_fries and game.me.burger >= customer.burger

    def get_nearest_needed_resource_position(self, game, customer):
        "The position of the closest resource necessary for the customer"

        def distance_to_me(position):
            return abs(game.me.pos['x'] - position[0]) + abs(game.me.pos['y'] - position[1])

        if game.me.french_fries < customer.french_fries:
            target_position = sorted(game.fries_locs.keys(), key=distance_to_me)[0]
            print('we need fries! the closest is: ' + str(target_position))
        else:
            target_position = sorted(game.burger_locs.keys(), key=distance_to_me)[0]
            print('we need burgers! the closest is: ' + str(target_position))

        return target_position
