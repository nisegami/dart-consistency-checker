from typing import List, Optional, Tuple, Dict
from framework import Disruption, Manager, Card, Game


class InvokedDogmaManager(Manager):
    aleister = Card("Aleister the Invoker", 0, "M")
    invocation = Card("Invocation", 0, "S")
    meltdown = Card("Magical Meltdown", 0, "S")
    terraforming = Card("Terraforming", 10, "S")
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

    almiraj = Card("Salamangreat Almiraj", 0, "ED")
    gardna = Card("Secure Gardna", 0, "ED")
    mechaba = Card("Invoked Mechaba", 0, "ED")
    titaniklad = Card("Titaniklad the Ash Dragon", 0, "ED")
    apkalone = Card("El Shaddoll Apkalone", 0, "ED")
    winda = Card("El Shaddoll Winda", 0, "ED")
    construct = Card("El Shaddoll Construct", 0, "ED")
    omega = Card("Psy-framelord Omega", 0, "ED")

    default_decklist = (
        (aleister, 3),
        (invocation, 3),
        (meltdown, 3),
        (ecclesia, 3),
        (maximus, 2),
        (fleur, 2),
        (punishment, 2),
        (servant, 3),
        (schism, 1),
        (desires, 3),
        (upstart, 1),
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
            ["Mechaba", cls.percent_with_flags(end_games, ["mechaba"])],
            ["Both", cls.percent_with_flags(end_games, ["winda", "mechaba"])],
            [">2 Disruptions", cls.percent_with_flags(end_games, [">2 disruptions"])],
            ["Bricks (<3 Disruptions and no Winda)", cls.percent_with_flags(
                end_games, ["brick"]
            )],
        ]

    @classmethod
    def generate_sankey_data(
        cls, end_games: List[Game]
    ) -> Tuple[List[str], List[str], List[int], List[int], List[int]]:
        results = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]

        for game in end_games:
            if cls.pinpoint in game.backrow:
                if game.hopt_available(cls.pinpoint):
                    # pinpoint live but not used
                    outer_index = 1
                else:
                    # pinpoint live and used
                    outer_index = 2
            else:
                # pinpoint not drawn
                outer_index = 0

            inner_index = 0

            if game.has_flag("winda"):
                inner_index += 2

            if game.has_flag(">2 disruptions"):
                inner_index += 1

            results[outer_index][inner_index] += 1

        label = [
            "Pinpoint Landing Not Drawn",  # 0
            "Pinpoint Landing Drawn But Not Used",  # 1
            "Pinpoint Landing Drawn And Used",  # 2
            "Brick",  # 3
            "3 Or More Disruptions",  # 4
            "Winda",  # 5
            "Winda & 3 Or More Disruptions",  # 6
        ]
        color = ["red", "red", "green", "red", "blue", "purple", "green"]

        source = [0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2]
        target = [3, 4, 5, 6, 3, 4, 5, 6, 3, 4, 5, 6]
        value = results[0] + results[1] + results[2]

        return label, color, source, target, value

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

        if self.mechaba in game.monsters:
            types_to_discard = set([card.card_type for card in game.hand])
            if types_to_discard:
                game.add_flag("mechaba")
                pure_distruptions += 1
                game.disruptions.append(
                    Disruption(
                        f"{repr(self.mechaba)} ({', '.join(types_to_discard)})",
                        len(types_to_discard),
                    ),
                )

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

        if self.aleister in game.hand:
            game.disruptions.append(Disruption(repr(self.aleister), 0))

        if pure_distruptions >= 3:
            game.add_flag(">2 disruptions")

        if game.value() < 3 and not game.has_flag("winda"):
            game.add_flag("brick")

        return game

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
        else:
            # we dumped apkalone with maximus
            options = [entry[0] for entry in self.deck_recipe]
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
                self.almiraj,
                self.construct,
                self.mechaba,
                self.apkalone,
                self.gardna,
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

    def action_use_terraforming(self, game: Game) -> Optional[Game]:
        if (
            self.terraforming in game.hand
            and self.meltdown in game.deck
            and game.hopt_available(self.terraforming)
        ):
            game.move(game.hand, game.grave, self.terraforming)
            game.move(game.deck, game.hand, self.meltdown)
            game.use_hopt(self.terraforming)
            return game

    def action_use_meltdown(self, game: Game) -> Optional[Game]:
        if self.meltdown in game.hand and game.hopt_available(self.meltdown):
            game.move(game.hand, game.backrow, self.meltdown)
            game.use_hopt(self.meltdown)
            if self.aleister in game.deck:
                game.move(game.deck, game.hand, self.aleister)
            return game

    def action_summon_aleister(self, game: Game) -> Optional[Game]:
        if self.aleister in game.hand and game.resource_available("normal summon"):
            game.move(game.hand, game.monsters, self.aleister)
            game.use_resource("normal summon")
            if self.invocation in game.deck:
                game.move(game.deck, game.hand, self.invocation)
                game.use_hopt(self.aleister)
            return game

    def action_summon_almiraj(self, game: Game) -> Optional[Game]:
        if self.aleister in game.monsters and game.resource_available("extra deck"):
            game.move(game.monsters, game.grave, self.aleister)
            game.monsters.add(self.almiraj)
            return game

    def action_summon_gardna(self, game: Game) -> Optional[Game]:
        if self.almiraj in game.monsters and game.resource_available("extra deck"):
            game.move(game.monsters, game.grave, self.almiraj)
            game.monsters.add(self.gardna)
            return game

    def action_summon_mechaba(self, game: Game) -> Optional[Game]:
        if self.invocation in game.hand and game.resource_available("extra deck"):
            if self.gardna in game.grave:
                game.move(game.grave, game.banished, self.gardna)
            elif self.gardna in game.monsters:
                game.move(game.monsters, game.banished, self.gardna)
            elif self.veiler in game.grave:
                game.move(game.grave, game.banished, self.veiler)
            elif self.veiler in game.hand:
                game.move(game.hand, game.grave, self.veiler)
            elif self.ogre in game.grave:
                game.move(game.grave, game.banished, self.ogre)
            elif self.ogre in game.hand:
                game.move(game.hand, game.grave, self.ogre)
            else:
                return None

            if self.aleister in game.grave:
                game.move(game.grave, game.banished, self.aleister)
            elif self.aleister in game.monsters:
                game.move(game.monsters, game.banished, self.aleister)
            elif self.aleister in game.hand:
                game.move(game.hand, game.grave, self.aleister)
            else:
                return None

            game.move(game.hand, game.grave, self.invocation)
            game.use_hopt(self.invocation, "summon")
            game.monsters.add(self.mechaba)
            return game

    def action_recycle_aleister(self, game: Game) -> Optional[Game]:
        if self.invocation in game.grave and self.aleister in game.banished:
            game.move(game.grave, game.deck, self.invocation)
            game.move(game.banished, game.hand, self.aleister)
            game.deck.shuffle()
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
