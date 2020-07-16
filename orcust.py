import random
import os, os.path

from plotly import graph_objects

from framework import Manager, Card, Game

class OrcustManager(Manager):
    redeployment = Card('Machina Redeployment')
    knightmare = Card('Orcust Knightmare')
    girsu = Card('Orcust Mekk-Knight Girsu')
    cymbal = Card('Orcust Cymbal Skeleton')
    wand = Card('World Legacy - World Wand')
    o_return = Card('Orcustrated Return')
    recycler = Card('Scrap Recycler')
    golem = Card('Scrap Golem')
    jet = Card('Jet Synchron')
    gizmek = Card('Gizmek Orochi, the Serpentron Sky Slasher')
    irradiator = Card('Machina Irradiator')
    megaform = Card('Machina Megaform')
    metalcruncher = Card('Machina Metalcruncher')
    citadel = Card('Machina Citadel')
    foolish = Card('Foolish Burial')
    babel = Card('Orcustrated Babel')
    succession = Card('World Legacy Succession')
    crescendo = Card('Orcust Crescendo')
    nibiru = Card('Nibiru, the Primal Being')
    imperm = Card('Infinite Impermanence')
    ash = Card('Ash Blossom & Joyous Spring')
    drnm = Card('Dark Ruler No More')
    called = Card('Called by the Grave')
    buster = Card('Buster Whelp of the Destruction Swordsman')

    galatea = Card('Galatea, the Orcust Automaton')
    wyvern = Card('Scrap Wyvern')
    lib = Card("Lib the World Key Blademaster")
    bow = Card("Apollousa, Bow of the Goddess")
    ding = Card("Dingirsu, the Orcust of the Evening Star")
    ip = Card("I:P Masquerena")
    linkuriboh = Card('Linkuriboh')
    carrier = Card('Union Carrier')

    deck_recipe = (
        (knightmare, 3),
        (girsu, 3),
        (cymbal, 2),
        (wand, 2),
        (recycler, 3),
        (golem, 1),
        (jet, 1),
        (gizmek, 1),
        (redeployment, 3),
        (irradiator, 1),
        (megaform, 1),
        (metalcruncher, 1),
        (citadel, 1),
        (foolish, 1),
        (o_return, 2),
        (babel, 1),
        (succession, 1),
        (crescendo, 1),
        (nibiru, 3),
        (imperm, 3),
        (ash, 2),
        (drnm, 3),
    )

    orcust_priorities = [knightmare, cymbal, wand, girsu]

    orcust_monsters = [knightmare, cymbal, girsu]

    recycler_priorities = [knightmare, cymbal, wand, girsu, gizmek, citadel, jet]

    hand_traps = [ash]
    
    going_second_cards = [ash, imperm, nibiru, drnm]

    high_priority_discards = [
        knightmare,
        cymbal,
        wand,
        girsu,
        citadel,
        jet,
        gizmek,
        golem,
    ]

    low_priority_discards = [
        crescendo,
        foolish,
        imperm,
        ash,
        babel,
        recycler,
        succession
    ]

    wyvern_fodder = [
        redeployment,
        drnm,
        o_return,
        foolish
    ]

    initial_game = Game.build_from_recipe(deck_recipe)

    def __init__(self):
        super().__init__(self.initial_game)

    def eval(self, game):
        val = 2*len(game.monsters) + 2*len(game.backrow) + sum([game.hand.cards.count(card) for card in self.hand_traps])
        if self.ding in game.monsters:
            val += 2
        return val

    def postprocess(self, game):
        if not game.hopt_available(self.jet) and self.jet in game.grave:
            game.move(game.grave, game.banished, self.jet)

        if game.hopt_available(self.wand, 2) and self.wand in game.grave and self.wand in game.hand:
            game.move(game.hand, game.monsters, self.wand)
            game.use_hopt(self.wand, 2)

        girsu_target = self.select_girsu_send(game)

        if girsu_target and self.girsu in game.monsters and game.hopt_available(self.girsu, 1):
            game.use_hopt(self.girsu, 1)
            game.move(game.deck, game.grave, girsu_target)
        
        return game

    def select_return_discard(self, game):
        front = [card for card in self.orcust_priorities if card not in game.grave]
        back = [card for card in self.orcust_priorities if card in game.grave]
        options = front + back
        return game.hand.get_any(options)

    def select_knightmare_send(self, game):
        front = [card for card in self.orcust_priorities if card not in game.grave]
        back = [card for card in self.orcust_priorities if card in game.grave]
        options = front + back
        options.remove(self.knightmare)
        return game.deck.get_any(options)

    def select_wand_target(self, game):
        front = [card for card in self.orcust_priorities if card not in game.grave]
        back = [card for card in self.orcust_priorities if card in game.grave]
        options = front + back
        options.remove(self.wand)
        return game.banished.get_any(options)

    def select_cymbal_target(self, game):
        front = [card for card in self.orcust_priorities if card not in game.grave]
        back = [card for card in self.orcust_priorities if card in game.grave]
        options = front + back
        options.remove(self.cymbal)
        options.remove(self.wand)
        return game.grave.get_any(options)

    def select_girsu_send(self, game):
        front = [card for card in self.orcust_priorities if card not in game.grave]
        back = [card for card in self.orcust_priorities if card in game.grave]
        options = front + back
        return game.deck.get_any(options)

    def select_generic_discard(self, game):
        if not game.hand:
            return None

        front = [card for card in self.high_priority_discards if card not in game.grave]
        back = [card for card in self.high_priority_discards if card in game.grave]
        high_priority = front + back

        target = game.hand.get_any(high_priority)
        if target:
            return target
        for card in game.hand:
            if card not in self.low_priority_discards:
                return card
        target = game.hand.get_any(self.low_priority_discards)
        if target:
            return target
        return game.hand.random()

    def select_wyvern_fodder(self, game):
        return self.hand.get_any(self.wyvern_fodder)

    def select_carrier_targets(self, game):
        #TODO, kinda hard
        return ()

    def action_use_return(self, game):
        if self.o_return in game.hand and len(game.deck) > 1:
            selected_discard = self.select_return_discard(game)
            if selected_discard:
                game.move(game.hand, game.grave, self.o_return)
                game.move(game.hand, game.grave, selected_discard)
                game.draw()
                game.draw()
                game.use_hopt(self.o_return)
                return game

    def action_use_redeployment(self, game):
        if game.resource_available('orcust lock') and game.hopt_available(self.redeployment) and self.redeployment in game.hand and len(game.hand) > 1:

            if self.irradiator in game.hand and self.megaform in game.hand:
                # don't even bother to use redeployment
                return 

            game.move(game.hand, game.grave, self.redeployment)

            backup_target = game.deck.get_any([self.citadel, self.metalcruncher])
            
            if self.megaform in game.deck and self.irradiator in game.deck:
                target_1 = self.megaform
                target_2 = self.irradiator
                selected_discard = self.select_generic_discard(game)

            elif self.irradiator in game.hand and self.megaform in game.deck:
                if not backup_target:
                    # don't have two targets to search
                    return
                game.hand.remove(self.irradiator)
                selected_discard = self.select_generic_discard(game)
                game.hand.add(self.irradiator)
                target_1 = backup_target
                target_2 = self.megaform

            elif self.megaform in game.hand and self.irradiator in game.deck:
                if not backup_target:
                    # don't have two targets to search
                    return
                game.hand.remove(self.megaform)
                selected_discard = self.select_generic_discard(game)
                game.hand.add(self.megaform)
                target_1 = backup_target
                target_2 = self.irradiator
            
            else:
                # not sure what happened?
                return 

            if not selected_discard:
                # also not sure what happened
                return

            game.move(game.deck, game.hand, target_1)
            game.move(game.deck, game.hand, target_2)
            game.move(game.hand, game.grave, selected_discard)
            game.use_hopt(self.redeployment)
            return game

    def action_machina_combo(self, game):
        if self.irradiator in game.hand and self.megaform in game.hand:
            game.move(game.hand, game.grave, self.irradiator)
            game.move(game.hand, game.monsters, self.megaform)

            if game.deck.cards.count(self.recycler) == 3:
                targets = [self.recycler, self.recycler, self.recycler]
            elif game.deck.cards.count(self.recycler) == 3 and self.citadel in game.deck:
                targets = [self.recycler, self.recycler, self.citadel]
            else:
                # not enough targets to search with metalcruncher
                return game

            game.move(game.monsters, game.grave, self.megaform)

            if self.metalcruncher in game.hand:
                game.move(game.hand, game.monsters, self.metalcruncher)
            elif self.metalcruncher in game.deck:
                game.move(game.deck, game.monsters, self.metalcruncher)
            else:
                # no clue where metalcruncher is lol
                return

            game.move(game.deck, game.hand, random.choice(targets))
            return game

    def action_summon_recycler(self, game):
        if self.recycler in game.hand and game.resource_available('normal summon'):
            game.move(game.hand, game.monsters, self.recycler)
            game.use_resource('normal summon')
            game.add_flag('recycler')

            recycler_target = None

            if len(game.monsters) > 1 and self.citadel in game.deck and self.golem in game.deck:
                # if we have a monster on the field, send citadel
                recycler_target = self.citadel
            elif len(game.hand) > 1 and self.jet in game.deck and self.golem in game.deck:
                # send jet synchron if 
                recycler_target = self.jet
            else:
                # else pick from priorities
                front = [card for card in self.recycler_priorities if card not in game.grave]
                back = [card for card in self.recycler_priorities if card in game.grave]
                options = front + back
                recycler_target = game.deck.get_any(options)

            if recycler_target:
                game.move(game.deck, game.grave, recycler_target)

            return game

    def action_summon_girsu(self, game):
        if self.girsu in game.hand  and game.resource_available('normal summon'):
            game.move(game.hand, game.monsters, self.girsu)
            game.use_resource('normal summon')
            game.add_flag('girsu')

            girsu_target = self.select_girsu_send(game)

            if girsu_target and game.hopt_available(self.girsu, 1):
                game.use_hopt(self.girsu, 1)
                game.move(game.deck, game.grave, girsu_target)

            if len(game.monsters) == 1 and game.hopt_available(self.girsu, 2):
                game.use_hopt(self.girsu, 2)
                game.monsters.add(self.linkuriboh)

            return game

    def action_summon_jet(self, game):
        if game.resource_available('orcust lock') and game.hopt_available(self.jet) and self.jet in game.grave and len(game.hand) > 1:
            selected_discard = self.select_generic_discard(game)
            game.move(game.grave, game.monsters, self.jet)
            game.move(game.hand, game.grave, selected_discard)
            game.use_hopt(self.jet)
            return game

    def action_summon_wyvern(self, game):
        if game.resource_available('orcust lock') and self.recycler in game.monsters and len(game.monsters) > 1 and self.golem in game.deck and game.hopt_available(self.wyvern):
            wyvern_material = game.monsters.random(exclude=[self.recycler])
            game.move(game.monsters, game.grave, wyvern_material)
            game.move(game.deck, game.monsters, self.golem)
            game.use_hopt(self.wyvern)

            if self.citadel in game.grave:
                game.move(game.grave, game.monsters, self.citadel)

            wyvern_fodder = game.hand.get_any(self.wyvern_fodder)
            if wyvern_fodder:
                game.monsters.add(self.wyvern)
                game.move(game.hand, game.grave, wyvern_fodder)
            else:
                #TODO: consider adding a check for extra monsters on board such as world wand summoned from hand
                game.grave.add(self.wyvern)

            front = [card for card in self.recycler_priorities if card not in game.grave]
            back = [card for card in self.recycler_priorities if card in game.grave]
            options = front + back
            recycler_target = game.deck.get_any(options)
            if recycler_target:
                game.move(game.deck, game.grave, recycler_target)
            return game

    def action_use_succession(self, game):
        if game.resource_available('orcust lock') and game.hopt_available(self.succession) and self.recycler in game.monsters and self.golem in game.monsters:
            if self.succession in game.hand:
                game.use_hopt(self.succession)
                game.add_flag('full combo')
                game.monsters.add(self.ip)
                game.move(game.hand, game.grave, self.succession)
            elif self.succession in game.deck:
                game.use_hopt(self.succession)
                game.add_flag('full combo')
                game.monsters.add(self.lib)
                game.move(game.deck, game.grave, self.succession)
            else:
                # must have discarded succession?
                return

            game.use_hopt(self.succession)

            front = [card for card in self.recycler_priorities if card not in game.grave]
            back = [card for card in self.recycler_priorities if card in game.grave]
            options = front + back
            recycler_target = game.deck.get_any(options)
            if recycler_target:
                game.move(game.deck, game.grave, recycler_target)
            return game

    def action_use_knightmare(self, game):
        if game.hopt_available(self.knightmare) and self.knightmare in game.grave and len(game.monsters) > 0:
            knightmare_target = self.select_knightmare_send(game)
            if knightmare_target:
                game.move(game.grave, game.banished, self.knightmare)
                game.use_hopt(self.knightmare)
                game.use_resource('orcust lock')
                game.move(game.deck, game.grave, knightmare_target)
                return game

    def action_use_wand(self, game):
        if game.hopt_available(self.wand, 1) and self.wand in game.grave:
            wand_target = self.select_wand_target(game)
            if wand_target:
                game.move(game.grave, game.banished, self.wand)
                game.use_hopt(self.wand, 1)
                game.use_resource('orcust lock')
                game.move(game.banished, game.monsters, wand_target)
                return game

    def action_use_cymbal(self, game):
        if game.hopt_available(self.cymbal) and self.cymbal in game.grave:
            cymbal_target = self.select_cymbal_target(game)
            if cymbal_target:
                game.move(game.grave, game.banished, self.cymbal)
                game.use_hopt(self.cymbal)
                game.use_resource('orcust lock')
                game.move(game.grave, game.monsters, cymbal_target)
                return game

    def action_summon_gizmek(self, game):
        if game.hopt_available(self.gizmek) and (self.gizmek in game.grave or self.gizmek in game.hand):
            if self.gizmek in game.grave:
                game.move(game.grave, game.monsters, self.gizmek)
            elif self.gizmek in game.hand:
                game.move(game.hand, game.monsters, self.gizmek)

            game.use_hopt(self.gizmek)

            for _ in range(8):
                game.deck.cards.pop(0)

            return game

    def action_summon_galatea(self, game):
        if len([card for card in game.monsters if card in self.orcust_monsters]) > 0 and len(game.monsters) > 1:
            orcust_card = random.choice([card for card in game.monsters.cards if card in self.orcust_monsters])
            game.move(game.monsters, game.grave, orcust_card)
            other_card = game.monsters.random()
            game.move(game.monsters, game.grave, other_card)
            game.monsters.add(self.galatea)
            game.add_flag('basic combo')
            if game.banished:
                to_return = game.banished.random()
                game.use_hopt(self.galatea)
                game.move(game.banished, game.deck, to_return)
                if self.babel in game.deck:
                    game.move(game.deck, game.backrow, self.babel)
                elif self.crescendo in game.deck:
                    game.move(game.deck, game.backrow, self.crescendo)
                elif self.o_return in game.deck:
                    game.move(game.deck, game.backrow, self.o_return)
            return game

    def action_summon_dingirsu(self, game):
        if game.hopt_available(self.ding, 1) and self.galatea in game.monsters:
            game.monsters.remove(self.galatea)
            game.monsters.add(self.ding)
            game.use_hopt(self.ding, 1)
            if game.hopt_available(self.ding, 2):
                if not game.hopt_available(self.girsu, 2):
                    game.use_hopt(self.ding, 2)
                elif len(game.banished) > 0:
                    ding_target = game.banished.random()
                    game.move(game.banished, game.grave, ding_target)
                    game.use_hopt(self.ding, 2)
            return game

    def action_make_carrier(self, game):
        targets = self.select_carrier_targets(game)
        if targets and (self.buster in game.hand or self.buster in game.deck):
            target_1, target_2 = targets
            game.move(game.monsters, game.grave, target_1)
            game.move(game.monsters, game.grave, target_2)
            game.monsters.add(self.carrier)
            if self.buster in game.hand:
                game.move(game.hand, game.backrow, self.buster)
            else:
                game.move(game.deck, game.backrow, self.buster)

    def action_set_backrow(self, game):
        before = len(game.hand)
        if self.babel in game.hand:
            game.move(game.hand, game.backrow, self.babel)
        if self.crescendo in game.hand:
            game.move(game.hand, game.backrow, self.crescendo)
        if self.imperm in game.hand:
            game.move(game.hand, game.backrow, self.imperm)
        if self.called in game.hand:
            game.move(game.hand, game.backrow, self.called)
        after = len(game.hand)
        if before != after:
            return game

def generate_sankey(end_games):
    gs = [[0, 0, 0], [0, 0, 0]]
    combo = [[0, 0, 0], [0, 0, 0]]

    for game in end_games:
        if game.has_flag('going second card'):
            outer_index_gs = 0
        else:
            outer_index_gs = 1

        if game.has_flag('recycler'):
            inner_index_gs = 0
            outer_index_combo = 0
        elif game.has_flag('girsu'):
            inner_index_gs = 1
            outer_index_combo = 1
        else:
            inner_index_gs = 2
            gs[outer_index_gs][inner_index_gs] += 1
            continue
        
        if game.has_flag('full combo'):
            inner_index_combo = 0
        elif game.has_flag('basic combo'):
            inner_index_combo = 1
        else:
            inner_index_combo = 2

        gs[outer_index_gs][inner_index_gs] += 1
        combo[outer_index_combo][inner_index_combo] += 1

    fig = graph_objects.Figure(data=[graph_objects.Sankey(
        node = dict(
        pad = 15,
        thickness = 20,
        line = dict(color = 'black', width = 0.5),
        label = ['Going Second Card Drawn', 'No Going Second Card Drawn', 'Scrap Used', 'Girsu Used', 'Full Combo', 'Basic Combo', 'Brick'],
        #               0                               1                       2           3               4           5             6
        color  = ['green', 'blue', 'brown', 'black', 'green', 'blue', 'red']
        ),
        link = dict(
            source = [0, 0, 0, 1, 1, 1, 2, 2, 2, 3, 3, 3],
            target = [2, 3, 6, 2, 3, 6, 4, 5, 6, 4, 5, 6],
            value = gs[0] + gs[1] + combo[0] + combo[1]
    ))])

    fig.write_html(os.path.join('output', 'orcust.html'))

def run_one():
    return OrcustManager().run()

def run_in_parallel(n):
    import multiprocessing
    with multiprocessing.Pool(multiprocessing.cpu_count()) as pool:
        future_results = [pool.apply_async(run_one) for i in range(n)]
        return [f.get() for f in future_results]

if __name__ == '__main__':
    import time
    start = time.time()
    end_games = run_in_parallel(500)
    generate_sankey(end_games)
    duration = time.time() - start
    print(duration)
