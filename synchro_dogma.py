from typing import List, Optional, Tuple, Dict
from framework import Disruption, Manager, Card, Game


class SynchroDogmaManager(Manager):
    righty = Card("Righty Driver", 5, "M")
    lefty = Card("Lefty Driver", 10, "M")
    jet = Card("Jet Synchron", 5, "M")
    tuning = Card("Tuning", 5, "S")
    deskbot = Card("Deskbot 001", 20, "M")
    o_lion = Card("Mecha Phantom Beast O-Lion", 10, "M")
    ecclesia = Card("Dogmatika Eccelsia, the Virtuous", 0, "M")
    maximus = Card("Dogmatika Maximus", 5, "M")
    fleur = Card("Dogmatika Fleurdelis, the Knighted", 0, "M")
    punishment = Card("Dogmatika Punishment", 0, "T")
    servant = Card("Nadir Servant", 0, "S")
    schism = Card("Shaddoll Schism", 5, "T")
    desires = Card("Pot of Desires", 10, "S")
    upstart = Card("Upstart Goblin", 10, "S")
    pinpoint = Card("Pinpoint Landing", 12, "S")

    nibiru = Card("Nibiru, the Primal Being", 0, "M")
    imperm = Card("Infinite Impermanence", 0, "T")
    ash = Card("Ash Blossom & Joyous Spring", 0, "M")
    called = Card("Called by the Grave", 0, "S")
    droplet = Card("Forbidden Droplet", 0, "S")
    ogre = Card("Ghost Ogre & Snow Rabbit", 0, "M")
    veiler = Card("Effect Veiler", 0, "M")

    titaniklad = Card("Titaniklad the Ash Dragon", 0, "ED")
    apkalone = Card("El Shaddoll Apkalone", 0, "ED")
    winda = Card("El Shaddoll Winda", 0, "ED")
    construct = Card("El Shaddoll Construct", 0, "ED")
    omega = Card("Psy-framelord Omega", 0, "ED")
    linkuriboh = Card("Linkuriboh", 0, "ED")
    linkross = Card("Linkross", 0, "ED")
    halq = Card("Crystron Halquifibrax", 0, "ED")
    carrier = Card("Union Carrier", 0, "ED")
    formula = Card("Formula Synchron", 0, "ED")
    auroradon = Card("Mecha Phantom Beast Auroradon", 0, "ED")
    savage = Card("Borreload Savage Dragon", 0, "ED")
    herald = Card("Herald of the Arc Light", 0, "ED")

    default_decklist = (
        (tuning, 2),
        (jet, 3),
        (o_lion, 2),
        (deskbot, 1),
        (righty, 3),
        (lefty, 1),
        (ecclesia, 3),
        (maximus, 2),
        (fleur, 2),
        (punishment, 1),
        (servant, 3),
        (schism, 1),
        (desires, 3),
        (imperm, 3),
        (ash, 3),
        (called, 3),
        (droplet, 1),
        (ogre, 3),
    )

    hand_traps = (ash, ogre, veiler, imperm)
    going_second_cards = (ash, ogre, veiler, imperm, droplet, nibiru)
    backrow = (droplet, called, imperm, punishment)

    @classmethod
    def generate_stats(cls, end_games: List[Game]) -> List[List[str]]:
        return [
            ["Winda", cls.percent_with_flags(end_games, ["winda"])],
            ["Herald", cls.percent_with_flags(end_games, ["herald"])],
            ["Savage", cls.percent_with_flags(end_games, ["savage"])],
            [">2 Disruptions", cls.percent_with_flags(end_games, [">2 disruptions"])],
            [">2 Disruptions and Winda", cls.percent_with_flags(
                end_games, [">2 disruptions", "winda"]
            )],
            ["Bricks (<3 Disruptions and no Winda)", cls.percent_with_flags(
                end_games, ["brick"]
            )],
        ]

    def postprocess(self, game: Game):
        if self.apkalone in game.grave and game.hopt_available(self.apkalone):
            game.use_hopt(self.apkalone)
            if self.schism in game.deck:
                game.move(game.deck, game.hand, self.schism)
                discard = self.select_schism_discard(game)
                game.move(game.hand, game.grave, discard)

        if self.construct in game.grave and game.hopt_available(self.construct):
            game.use_hopt(self.construct)
            if self.schism in game.grave:
                game.move(game.grave, game.hand, self.schism)

        return game

    def endphase(self, game: Game):
        for card in game.hand:
            if card in self.backrow:
                game.move(game.hand, game.backrow, card)

        if self.titaniklad in game.grave and game.hopt_available(self.titaniklad):
            target = self.select_titaniklad_search_target(game)
            if (
                target
                and target == self.ecclesia
                and game.hopt_available(self.ecclesia, "search")
            ):
                game.use_hopt(self.titaniklad)
                game.move(game.deck, game.monsters, target)
                second_target = self.select_ecclesia_search_target(game)
                if second_target:
                    game.move(game.deck, game.hand, second_target)
                    game.use_hopt(self.ecclesia, "search")
            elif target:
                game.use_hopt(self.titaniklad)
                game.move(game.deck, game.hand, target)

        if self.schism in game.hand:
            game.move(game.hand, game.backrow, self.schism)

        # Process Disruptions

        if (
            self.schism in game.backrow
            and len(
                [
                    card in game.grave
                    for card in [self.apkalone, self.construct, self.titaniklad]
                ]
            )
            >= 2
        ):
            game.add_flag("winda")
            game.disruptions.append(Disruption(repr(self.winda), 3))

        pure_distruptions = 0

        if self.herald in game.monsters:
            game.add_flag("herald")
            pure_distruptions += 1
            game.disruptions.append(Disruption(repr(self.herald), 1))

        if self.savage in game.monsters:
            game.add_flag("savage")
            pure_distruptions += 1
            game.disruptions.append(Disruption(repr(self.savage), 1))

        if self.fleur in game.hand and any(
            [
                card in [self.ecclesia, self.maximus, self.fleur]
                for card in game.monsters
            ]
        ):
            game.add_flag("fleur")
            pure_distruptions += 1
            game.disruptions.append(Disruption(repr(self.fleur), 1))

        for card in self.hand_traps:
            if card in game.hand:
                pure_distruptions += 1
                game.disruptions.append(Disruption(repr(card), 1))

        for card in self.backrow:
            if card in game.backrow:
                pure_distruptions += 1
                game.disruptions.append(Disruption(repr(card), 1))

        if pure_distruptions >= 3:
            game.add_flag(">2 disruptions")

        if game.value() < 3 and not game.has_flag("winda"):
            game.add_flag("brick")

        return game

    def select_aurorodan_trap(self, game: Game) -> Optional[Card]:
        return game.grave.get_any([self.schism, self.punishment, self.imperm])

    def select_jet_discard(self, game: Game) -> Optional[Card]:
        # dump jet for combo if in hand
        if self.deskbot in game.hand:
            return self.deskbot

        options = [entry[0] for entry in self.decklist]
        # prefer cards that have been used already
        front = [card for card in options if not game.hopt_available(card, tag=None)]
        back = [card for card in options if game.hopt_available(card, tag=None)]

        front.sort(key=lambda card: card.discard_weight, reverse=True)
        back.sort(key=lambda card: card.discard_weight, reverse=True)
        options = front + back
        return game.hand.get_any(options)

    def select_ecclesia_search_target(self, game: Game) -> Optional[Card]:
        if not game.hopt_available(self.titaniklad):
            # search during end phase
            if self.fleur in game.hand:
                game.deck.get_any([self.maximus, self.fleur, self.punishment])
            else:
                game.deck.get_any([self.fleur, self.maximus, self.punishment])
        else:
            # search during main phase
            if self.maximus in game.hand:
                return game.deck.get_any([self.punishment, self.fleur, self.maximus])
            else:
                return game.deck.get_any([self.maximus, self.punishment, self.fleur])

    def select_titaniklad_search_target(self, game: Game) -> Optional[Card]:
        if self.ecclesia in game.deck and game.hopt_available(self.ecclesia, "search"):
            return self.ecclesia
        else:
            options = [self.fleur, self.maximus, self.ecclesia]
            options = [card for card in options if card not in game.hand] + options
            return game.deck.get_any(options)

    def select_nadir_search_target(self, game: Game) -> Optional[Card]:
        options = [self.ecclesia, self.maximus, self.fleur]
        options = [card for card in options if card not in game.hand] + options
        return game.deck.get_any(options)

    def select_nadir_send_target(self, game: Game) -> Optional[Card]:
        if self.schism in game.deck and (
            self.maximus in game.deck or self.maximus in game.hand
        ):
            return self.apkalone
        elif self.schism in game.grave:
            return self.construct
        elif self.titaniklad not in game.grave:
            return self.titaniklad
        else:
            return self.omega

    def select_schism_discard(self, game: Game) -> Optional[Card]:
        if self.servant in game.grave and (
            self.maximus in game.deck or self.maximus in game.hand
        ):
            # we dumped apkalone with nadir servant
            # will use max and add schism back with construct
            return self.schism

        elif self.auroradon in game.monsters and game.hopt_available(
            self.auroradon, "tribute"
        ):
            # we can add back scism with aurorodan
            return self.schism
        else:
            # we dumped apkalone with maximus
            options = [entry[0] for entry in self.decklist]
            if len(game.hand) > 1:
                # keep schism if we can
                options.remove(self.schism)

            # prefer cards that have been used already
            front = [
                card for card in options if not game.hopt_available(card, tag=None)
            ]
            back = [card for card in options if game.hopt_available(card, tag=None)]

            front.sort(key=lambda card: card.discard_weight, reverse=True)
            back.sort(key=lambda card: card.discard_weight, reverse=True)
            options = front + back
            return game.hand.get_any(options)

    def select_maximus_banish(self, game: Game) -> Optional[Card]:
        return game.grave.get_any(
            [
                self.linkross,
                self.halq,
                self.carrier,
                self.formula,
                self.auroradon,
                self.savage,
                self.herald,
                self.linkuriboh,
                self.construct,
                self.apkalone,
                self.titaniklad,
            ]
        )

    def select_maximus_sends(self, game: Game) -> Tuple[Optional[Card], Optional[Card]]:
        if self.schism in game.grave:
            return (self.titaniklad, self.construct)
        else:
            return (self.titaniklad, self.apkalone)

    def action_activate_pinpoint(self, game: Game) -> Optional[Game]:
        if self.pinpoint not in game.backrow and self.pinpoint in game.hand:
            game.move(game.hand, game.backrow, self.pinpoint)
            return game

    def action_use_upstart(self, game: Game) -> Optional[Game]:
        if self.upstart in game.hand and len(game.deck) > 1:
            game.move(game.hand, game.grave, self.upstart)
            game.draw()
            return game

    def action_use_desires(self, game: Game) -> Optional[Game]:
        if (
            self.desires in game.hand
            and len(game.deck) > 1
            and game.hopt_available(self.desires)
        ):
            game.move(game.hand, game.grave, self.desires)
            game.use_hopt(self.desires)
            for _ in range(10):
                game.deck.cards.pop(0)
            game.draw()
            game.draw()
            return game

    def action_use_tuning(self, game: Game) -> Optional[Game]:
        if self.tuning in game.hand and self.jet in game.deck:
            game.move(game.hand, game.grave, self.tuning)
            game.move(game.deck, game.hand, self.jet)
            mill = game.deck.cards.pop(0)
            if self.herald in game.monsters and mill.card_type == "M":
                # random edge case
                game.banished.add(mill)
            else:
                game.grave.add(mill)
            return game

    def action_use_jet(self, game: Game) -> Optional[Game]:
        if self.jet in game.hand and game.resource_available("normal summon"):
            game.move(game.hand, game.monsters, self.jet)
            game.use_resource("normal summon")
            if game.resource_available("extra deck"):
                game.move(game.monsters, game.grave, self.jet)
                game.monsters.add(self.linkuriboh)
                discard = self.select_jet_discard(game)
                if discard:
                    game.move(game.hand, game.grave, discard)
                    game.move(game.grave, game.banished, self.jet)
                    game.use_hopt(self.jet)
                    game.move(game.monsters, game.grave, self.linkuriboh)
                    game.monsters.add(self.halq)
            return game

    def action_use_righty_driver(self, game: Game) -> Optional[Game]:
        if (
            self.righty in game.hand
            and self.lefty in game.deck
            and game.resource_available("normal summon")
        ):
            game.move(game.hand, game.monsters, self.righty)
            game.move(game.deck, game.monsters, self.lefty)
            game.use_hopt(self.righty)
            game.use_resource("normal summon")
            if game.resource_available("extra deck"):
                game.move(game.monsters, game.grave, self.righty)
                game.move(game.monsters, game.grave, self.lefty)
                game.monsters.add(self.halq)
            return game

    def action_use_righty_driver_into_herald(self, game: Game) -> Optional[Game]:
        if (
            self.righty in game.hand
            and self.lefty in game.deck
            and game.resource_available("normal summon")
        ):
            game.move(game.hand, game.monsters, self.righty)
            game.move(game.deck, game.monsters, self.lefty)
            game.use_hopt(self.righty)
            game.use_resource("normal summon")
            if game.resource_available("extra deck"):
                game.move(game.monsters, game.grave, self.righty)
                game.move(game.monsters, game.grave, self.lefty)
                game.monsters.add(self.herald)
            return game

    def action_halq(self, game: Game) -> Optional[Game]:
        if self.halq in game.monsters and game.hopt_available(self.halq):
            if self.deskbot in game.deck:
                game.move(game.deck, game.monsters, self.deskbot)
                halq_tuner = self.deskbot
            elif self.deskbot in game.hand:
                game.move(game.hand, game.monsters, self.deskbot)
                halq_tuner = self.deskbot
            elif self.deskbot in game.grave and self.righty in game.deck:
                game.move(game.deck, game.monsters, self.righty)
                halq_tuner = self.righty
            elif self.deskbot in game.grave and self.righty in game.hand:
                game.move(game.hand, game.monsters, self.righty)
                halq_tuner = self.righty
            else:
                return None

            game.use_hopt(self.halq)

            if self.linkuriboh in game.grave:
                # formula play
                game.move(game.monsters, game.grave, self.halq)
                game.move(game.monsters, game.grave, halq_tuner)
                game.grave.add(self.linkross)
                game.grave.add(self.carrier)
                game.grave.add(self.formula)
                game.use_hopt(self.linkuriboh)
                game.use_hopt(self.linkross)
                game.draw()
            else:
                # skip formula
                game.move(game.monsters, game.grave, self.halq)
                game.move(game.monsters, game.grave, halq_tuner)

            if self.o_lion in game.deck:
                game.use_hopt(self.auroradon, "tokens")
                game.use_hopt(self.auroradon, "tribute")
                game.use_hopt(self.o_lion)
                game.grave.add(self.auroradon)
                game.move(game.deck, game.grave, self.o_lion)
                game.monsters.add(self.savage)
                game.monsters.add(self.herald)
            else:
                game.use_hopt(self.auroradon, "tokens")
                game.monsters.add(self.auroradon)
                game.monsters.add(self.herald)

            return game

    def action_recover_trap(self, game: Game) -> Optional[Game]:
        if (
            self.auroradon in game.monsters
            and game.hopt_available(self.auroradon, "tribute")
            and any([card.card_type == "T" for card in game.grave])
        ):
            target = self.select_aurorodan_trap(game)
            game.move(game.monsters, game.grave, self.auroradon)
            game.use_hopt(self.auroradon, "tribute")
            game.move(game.grave, game.hand, target)
            return game

    def action_use_nadir(self, game: Game) -> Optional[Game]:
        if self.servant in game.hand and game.hopt_available(self.servant):
            search_target = self.select_nadir_search_target(game)
            if not search_target:
                return None
            send_target = self.select_nadir_send_target(game)
            if not send_target:
                return None
            game.grave.add(send_target)
            game.move(game.deck, game.hand, search_target)
            game.move(game.hand, game.grave, self.servant)
            game.use_hopt(self.servant)
            game.use_resource("extra deck")
            return game

    def action_summon_ecclesia(self, game: Game) -> Optional[Game]:
        if self.ecclesia in game.hand:
            if any(
                [monster.card_type == "ED" for monster in game.monsters]
            ) and game.hopt_available(self.ecclesia, "summon"):
                game.use_hopt(self.ecclesia, "summon")
                if self.pinpoint in game.backrow and game.hopt_available(self.pinpoint):
                    game.draw()
                    game.use_hopt(self.pinpoint)
                game.use_resource("extra deck")
            elif game.resource_available("normal summon"):
                game.use_resource("normal summon")
            else:
                return None

            game.move(game.hand, game.monsters, self.ecclesia)
            search_target = self.select_ecclesia_search_target(game)
            if game.hopt_available(self.ecclesia, "search") and search_target:
                game.move(game.deck, game.hand, search_target)
                game.use_hopt(self.ecclesia, "search")
                game.use_resource("extra deck")
            return game

    def action_summon_maximus(self, game: Game) -> Optional[Game]:
        if self.maximus in game.hand and game.hopt_available(self.maximus):
            banish = self.select_maximus_banish(game)
            if not banish:
                return None
            game.use_resource("extra deck")
            game.use_hopt(self.maximus)
            game.move(game.grave, game.banished, banish)
            send_1, send_2 = self.select_maximus_sends(game)
            game.grave.add(send_1)
            game.grave.add(send_2)
            if self.pinpoint in game.backrow and game.hopt_available(self.pinpoint):
                game.draw()
                game.use_hopt(self.pinpoint)
            return game
