#!/usr/bin/env python
#

""" 
Name:       Jesus Hernandez                         Partner:    Zechariah Neak 
Email:      jherna83@ucsc.edu                       Email:      zneak@ucsc.edu
ID:         1420330
Course:     CMPM146 Game AI
Professor:  Daniel G Shapiro

                                \\\\\\\ Program 4 ///////

Description:
    This is a bot that is designed to win at Planet Wars against 5 other bots using
    a behavior tree. The root acts as a Selector composite parent that checks through
    each Sequence composite child top to bottom, and performs the action for whatever
    Sequence child returns true. Each Sequence child only returns true if all its
    checks and actions come out as successful.
                     
"""

"""
// There is already a basic strategy in place here. You can use it as a
// starting point, or you can throw it out entirely and replace it with your
// own.
"""
import logging, traceback, sys, os, inspect
logging.basicConfig(filename=__file__[:-3] +'.log', filemode='w', level=logging.DEBUG)
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from behavior_tree_bot.behaviors import *
from behavior_tree_bot.checks import *
from behavior_tree_bot.bt_nodes import Selector, Sequence, Action, Check

from planet_wars import PlanetWars, finish_turn

# You have to improve this tree or create an entire new one that is capable
# of winning against all the 5 opponent bots
def setup_behavior_tree():

    # Top-down construction of behavior tree
    root = Selector(name='High Level Ordering of Strategies')

    # Define available actions to take.
    colonize = Action(take_defenseless_territory)
    invade = Action(attack_with_no_mercy)
    reinforce = Action(reinforce_with_vengeance)
    retaliate = Action(retaliate_with_fury)

    # *** Begin preliminary suprise invasion over the galaxy. ***
    imperial_ambition = Sequence(name='Expansion Strategy: Manifest Destiny')
    imperial_ambition.child_nodes = [colonize, invade]

    # *** Consolidate and retaliate if under attack by hostiles. ***
    imperial_shield = Sequence(name='Security Strategy: Cereberus')
    danger_check = Check(if_under_attack)
    imperial_shield.child_nodes = [danger_check, reinforce, retaliate]
    
    # *** If the advantage is ours, attack with full force. ***
    imperial_aggression = Sequence(name='Aggressive Strategy: Crush All Remaining Resistance')
    largest_fleet_check = Check(have_largest_fleet)
    imperial_aggression.child_nodes = [largest_fleet_check, invade]

    # Begin selecting strategies. 
    root.child_nodes = [imperial_ambition, imperial_aggression, imperial_shield, invade.copy()]

    logging.info('\n' + root.tree_to_string())
    return root

# You don't need to change this function
def do_turn(state):
    behavior_tree.execute(planet_wars)

if __name__ == '__main__':
    logging.basicConfig(filename=__file__[:-3] + '.log', filemode='w', level=logging.DEBUG)

    behavior_tree = setup_behavior_tree()
    try:
        map_data = ''
        while True:
            current_line = input()
            if len(current_line) >= 2 and current_line.startswith("go"):
                planet_wars = PlanetWars(map_data)
                do_turn(planet_wars)
                finish_turn()
                map_data = ''
            else:
                map_data += current_line + '\n'

    except KeyboardInterrupt:
        print('ctrl-c, leaving ...')
    except Exception:
        traceback.print_exc(file=sys.stdout)
        logging.exception("Error in bot.")
