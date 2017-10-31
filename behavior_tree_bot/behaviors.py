import logging, traceback, sys, os, inspect
sys.path.insert(0, '../')
from planet_wars import issue_order
from random import choice


""" 
Name:       Jesus Hernandez                         Partner:    Zechariah Neak 
Email:      jherna83@ucsc.edu                       Email:      zneak@ucsc.edu
ID:         1420330
Course:     CMPM146 Game AI
Professor:  Daniel G Shapiro

                                \\\\\\\ Program 4 ///////

Description:
    All the functions below are behaviors to be used as leaf nodes for the bt_bot's
    behavior tree.
                     
"""

def attack_weakest_enemy_planet(state):
    # (1) If we currently have a fleet in flight, abort plan.
    if len(state.my_fleets()) >= 1:
        return False

    # (2) Find my strongest planet.
    strongest_planet = max(state.my_planets(), key=lambda t: t.num_ships, default=None)

    # (3) Find the weakest enemy planet.
    weakest_planet = min(state.enemy_planets(), key=lambda t: t.num_ships, default=None)

    if not strongest_planet or not weakest_planet:
        # No legal source or destination
        return False
    else:
        # (4) Send half the ships from my strongest planet to the weakest enemy planet.
        return issue_order(state, strongest_planet.ID, weakest_planet.ID, strongest_planet.num_ships / 2)


def spread_to_weakest_neutral_planet(state):
    # (1) If we currently have a fleet in flight, just do nothing.
    if len(state.my_fleets()) >= 1:
        return False

    # (2) Find my strongest planet.
    strongest_planet = max(state.my_planets(), key=lambda p: p.num_ships, default=None)

    # (3) Find the weakest neutral planet.
    weakest_planet = min(state.neutral_planets(), key=lambda p: p.num_ships, default=None)

    if not strongest_planet or not weakest_planet:
        # No legal source or destination
        return False
    else:
        # (4) Send half the ships from my strongest planet to the weakest enemy planet.
        return issue_order(state, strongest_planet.ID, weakest_planet.ID, strongest_planet.num_ships / 2)


def colonize_closest_neutral_planet(state):
    #if len(state.my_fleets()) >= 1:
     #   return False
    
        strongest_planet = max(state.my_planets(), key=lambda p: p.num_ships, default=None)

        distances = []
        for planet in state.neutral_planets():
            distances.append((state.distance(strongest_planet.ID, planet.ID), planet))
        closest_distance, closest_planet = min(distances)
        pioneers = closest_planet.num_ships + 1
        issue_order(state, strongest_planet.ID, closest_planet.ID, pioneers)

    
def invade_closest_enemy_planet(state):
    #if len(state.my_fleets()) >= 1:
    #    return False
    
    for planet in state.my_planets():
        dist_list = []
        for ePlanet in state.enemy_planets():
            dist = state.distance(planet.ID, ePlanet.ID)
            dist_list.append((dist, ePlanet))
        min_dist, target = min(dist_list)

        detachment = target.num_ships + state.distance(planet.ID, target.ID) * target.growth_rate + 1
        issue_order(state, planet.ID, target.ID, detachment)


def retaliate_with_fury(state):
    # (1) Sort our planets from strongest to weakest.
    fortresses = iter(sorted(state.my_planets(), key=lambda p: p.num_ships, reverse=True))

    # (2) Find the weakest hostile planet.
    weakest_target = min(state.enemy_planets(), key=lambda t: t.num_ships, default=None)
    if not fortresses or not weakest_target:
        return False

    # (3) Send in joint invasion force from multiple bases.
    else:
        try:
            our_fortress = next(fortresses)
            #-- determine required force, considering distance to target and its production rate --
            legion_size = weakest_target.num_ships + \
                            state.distance(our_fortress.ID, weakest_target.ID) * weakest_target.growth_rate + 1
            while True:
                #-- if enough available ships on standby, with still enough for defence, deploy --
                detachment = int(our_fortress.num_ships * 0.75)
                if detachment > legion_size:
                    issue_order(state, our_fortress.ID, weakest_target.ID, detachment)
                    break
                #-- otherwise, send 75% of available ships and check next base  --
                else:
                    issue_order(state, our_fortress.ID, weakest_target.ID, detachment)
                    legion_size -= detachment
                    our_fortress = next(fortresses)

        except StopIteration:
            return


def expand_with_strength(state):
    # (1) Sort our planets from strongest to weakest.
    fortresses = iter(sorted(state.my_planets(), key=lambda p: p.num_ships, reverse=True))

    # (2) Identify planets we are not currently attacking.
    targetlist = [planet for planet in state.not_my_planets()
                      if not any(fleet.destination_planet == planet.ID for fleet in state.my_fleets())]

    # (3) Sort new targets from weakest to strongest.                 
    targetlist = iter(sorted(targetlist, key=lambda p: p.num_ships, default=True))

    # (4) Given enough ships for a target, send an invasion force to capture it.
    try:
        our_fortress = next(fortresses)
        our_target = next(targetlist)
        while True:
            #-- if neutral, send more than enough for a sustainable colony --
            if our_target.owner == 0:    
                legion_size = our_target.num_ships + int(our_target.num_ships/10) + 1

            #-- if hostile, send just enough, considering distance to target and its production rate --
            else:   
                legion_size = our_target.num_ships + \
                                 state.distance(our_fortress.ID, our_target.ID) * our_target.growth_rate + 1

            #-- if enough available ships, deploy legion into hyperspace --
            if our_fortress.num_ships > legion_size:
                issue_order(state, our_fortress.ID, our_target.ID, legion_size)
                our_fortress = next(fortresses)
                our_target = next(targetlist)
            #-- otherwise, leave alone until we have built enough strength --
            else:
                our_target = next(targetlist)

    except StopIteration:
        return


def take_defenseless_territory(state):
    # (1) Sort our planets from weakest to strongest.
    fortresses = iter(sorted(state.my_planets(), key=lambda p: p.num_ships))

    # (2) Sort neutral planets from weakest to strongest.
    wishlist = [planet for planet in state.neutral_planets()
                      if not any(fleet.destination_planet == planet.ID for fleet in state.my_fleets())]
    wishlist.sort(key=lambda p: p.num_ships)
    wishlist = iter(wishlist)

    # (3) Given enough ships for a target, send an invasion force to capture it.
    try:
        our_fortress = next(fortresses)
        target = next(wishlist)
        while True:
            legion_size = target.num_ships + 1

            if our_fortress.num_ships > legion_size:
                issue_order(state, our_fortress.ID, target.ID, legion_size)
                our_fortress = next(fortresses)
                target = next(wishlist)
            else:
                our_fortress = next(fortresses)

    except StopIteration:
        return


def attack_with_no_mercy(state):
    # (1) Sort our planets from weakest to strongest.
    fortresses = iter(sorted(state.my_planets(), key=lambda p: p.num_ships))

    # (2) Sort enemy planets from weakest to strongest.
    hostiles = [planet for planet in state.enemy_planets()
                      if not any(fleet.destination_planet == planet.ID for fleet in state.my_fleets())]
    hostiles.sort(key=lambda p: p.num_ships)
    hostiles = iter(hostiles)

    # (3) Given enough ships for a target, send an invasion force to capture it.
    try:
        our_fortress = next(fortresses)
        marked_for_DDay = next(hostiles)
        while True:
            #-- determine required force, considering distance to target and its production rate -- 
            required_ships = marked_for_DDay.num_ships + \
                                 state.distance(our_fortress.ID, marked_for_DDay.ID) * marked_for_DDay.growth_rate + 1

            if our_fortress.num_ships > required_ships:
                issue_order(state, our_fortress.ID, marked_for_DDay.ID, required_ships)
                our_fortress = next(fortresses)
                marked_for_DDay = next(hostiles)
            else:
                our_fortress = next(fortresses)

    except StopIteration:
        return


def reinforce_with_vengeance(state):
    # (1) Identify territory under our control.
    fortresses = [planet for planet in state.my_planets()]
    if not fortresses:
        return

    # (2) Determine strength of a given allied planet, considering friendlies and hostiles en route.
    def strength(fortress):
        return fortress.num_ships \
               + sum(fleet.num_ships for fleet in state.my_fleets() if fleet.destination_planet == fortress.ID) \
               - sum(fleet.num_ships for fleet in state.enemy_fleets() if fleet.destination_planet == fortress.ID)

    # (3) Calculate average strength among all planets, and determine the least-defended from the well-defended.
    avg = sum(strength(planet) for planet in fortresses) / len(fortresses)
    weakpoints = [planet for planet in fortresses if strength(planet) < avg]
    strongpoints = [planet for planet in fortresses if strength(planet) > avg]

    if (not weakpoints) or (not strongpoints):
        return

    # (4) Prioritize checking weakest planets, and see which other planet can provide reinforcements.
    weakpoints = iter(sorted(weakpoints, key=strength))
    strongpoints = iter(sorted(strongpoints, key=strength, reverse=True))

    try:
        weak_base = next(weakpoints)
        strong_base = next(strongpoints)
        while True:
            # -- determine amount of ships a base needs, and how much another base can provide --
            reinforcements = int(avg - strength(weak_base))
            spare_forces = int(strength(strong_base) - avg)

            # -- if enough ships available, deploy to weaker base
            if spare_forces >= reinforcements > 0:
                issue_order(state, strong_base.ID, weak_base.ID, reinforcements)
                weak_base = next(weakpoints)

            # -- if not enough available, go all-in, THIS IS AN EMERGENCY
            elif spare_forces > 0:
                issue_order(state, strong_base.ID, weak_base.ID, spare_forces)
                strong_planet = next(strongpoints)
        
            else:
                strong_planet = next(strongpoints)

    except StopIteration:
        return


