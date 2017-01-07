#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import requests

from bot import RandomBot

TIMEOUT = 15
BASE_URL = "http://game.blitz.codes:8080"


def get_new_game_state(session, server_url, key, mode='training', game_id=''):
    """Get a JSON from the server containing the current state of the game.

    Args:
        session: A request session.
        server_url (str): The URL of the API.
        key (str): A valid key.
        mode (str): 'training' or 'competition'.
        game_id (str): A valide game id.

    Returns:
        dict: The new game state.

    """
    if mode == 'training':
        # Don't pass the 'map' parameter if you want a random map
        # params = { 'key': key, 'map': 'm1'}
        params = {'key': key}
        api_endpoint = '/api/training'
    elif mode == 'competition':
        params = {'key': key}
        api_endpoint = '/api/arena?gameId='+game_id

    # Wait for 10 minutes
    print(server_url + api_endpoint)
    r = session.post(server_url + api_endpoint, params, timeout=10*60)

    if r.status_code == 200:
        return r.json()
    else:
        print("Error when creating the game")
        print(r.text)


def move(session, url, direction):
    """Send a move to the server.

    Args:
        session: A request session.
        url: The url where to post the move.
        direction: The direction to send to the server. One of 'Stay', 'North', 'South', 'East' or 'West'.

    Returns:
        dict: A dictionary containing the game state.

    """
    try:
        r = session.post(url, {'dir': direction}, timeout=TIMEOUT)

        if r.status_code == 200:
            return r.json()
        else:
            print("Error HTTP %d\n%s\n" % (r.status_code, r.text))
            return {'game': {'finished': True}}

    except requests.exceptions.RequestException as e:
        print(e)
        return {'game': {'finished': True}}


def is_finished(state):
    """Verify if a game is finished or not.

    Args:
        state (dict): A game state.

    """
    return state['game']['finished']


def start(server_url, key, mode, game_id, bot):
    """Start a game with all the required parameters.

    Args:
        server_url (str): The server's URL.
        key (str): A valid API key.
        mode (str): The game mode, "training" or "competition".
        game_id (str): a valid game id, when playing in competition mode.
        bot (Bot): The bot that will play the game.

    """
    # Create a requests session that will be used throughout the game
    session = requests.session()

    if mode == 'arena':
        print(u'Connected and waiting for other players to join…')
    # Get the initial state
    state = get_new_game_state(session, server_url, key, mode, game_id)
    print("Playing at: " + state['viewUrl'])

    while not is_finished(state):
        # Choose a move
        direction = bot.move(state)
        sys.stdout.write("Going to {}.\n".format(direction))
        sys.stdout.flush()

        # Send the move and receive the updated game state
        url = state['playUrl']
        state = move(session, url, direction)

    # Clean up the session
    session.close()


def main():
    if len(sys.argv) < 3:
        print("Usage: %s <key> <[training|competition]> [gameId]" % (sys.argv[0]))
        print('Example: %s mySecretKey competition myGameId' % (sys.argv[0]))
        print('Example: %s mySecretKey training' % (sys.argv[0]))
    else:
        key = sys.argv[1]
        mode = sys.argv[2]
        if len(sys.argv) == 4:
            game_id = sys.argv[3]
        else:
            game_id = ""

        if mode != "training" and mode != "competition":
            print("Invalid game mode. Please use 'training' or 'competition'.")
        else:
            start(BASE_URL, key, mode, game_id, RandomBot())
            print("\nGame finished!")


if __name__ == "__main__":
    main()
