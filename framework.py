from __future__ import annotations

import random

from functools import total_ordering
from dataclasses import dataclass
from typing import Iterator, List, Optional, Set, Tuple


@dataclass(order=False)
@total_ordering
class Card:
    name: str
    discard_weight: int
    card_type: str

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, other) -> bool:
        return self.name == other.name

    def __lt__(self, other) -> bool:
        return self.name.__lt__(other.name)

    def __repr__(self) -> str:
        return self.name

    def copy(self) -> Card:
        return self


@dataclass
class Disruption:
    name: str
    point_value: int

    def __repr__(self) -> str:
        return self.name


@dataclass
class CardGroup:
    cards: List[Card]

    def __repr__(self) -> str:
        return ", ".join([repr(card) for card in self.cards])

    def __eq__(self, other) -> bool:
        return sorted(self.cards) == sorted(other.cards)

    def __hash__(self) -> int:
        return hash(sorted(self.cards))

    def __contains__(self, item) -> bool:
        return item in self.cards

    def __len__(self) -> int:
        return len(self.cards)

    def __iter__(self) -> Iterator:
        return self.cards.__iter__()

    def random(self, exclude: List[Card] = []) -> Optional[Card]:
        if not self.cards:
            return None
        selected = random.choice(self.cards)
        while selected in exclude:
            selected = random.choice(self.cards)
        return selected

    def get_any(self, card_list: List[Card]) -> Optional[Card]:
        for card in card_list:
            for item in self.cards:
                if item == card:
                    return item

    def remove(self, card) -> None:
        self.cards.remove(card)

    def add(self, card) -> None:
        self.cards.append(card)

    def copy(self) -> CardGroup:
        return self.__class__([card.copy() for card in self.cards])


class Hand(CardGroup):
    pass


class Deck(CardGroup):
    def __repr__(self) -> str:
        return f"Deck containing {len(self.cards)} cards."

    def shuffle(self) -> None:
        random.shuffle(self.cards)

    def draw(self) -> Card:
        return self.cards.pop(0)

    def add_to_top(self, card: Card) -> None:
        self.cards.insert(0, card)

    def add_to_bottom(self, card: Card) -> None:
        self.cards.append(card)


class Grave(CardGroup):
    pass


class Field(CardGroup):
    pass


class Banished(CardGroup):
    pass


@dataclass
class Game:
    hand: Hand
    deck: Deck
    grave: Grave
    monsters: Field
    backrow: Field
    banished: Banished
    flags: Set[str]
    disruptions: List[Disruption]

    @classmethod
    def build_from_recipe(cls, deck_recipe: Tuple[Tuple[Card, int]]) -> Game:
        game = cls(
            Hand([]), Deck([]), Grave([]), Field([]), Field([]), Banished([]), set(), []
        )
        for (card, count) in deck_recipe:
            for _ in range(count):
                game.deck.add(card)
        game.deck.shuffle()
        for _ in range(5):
            game.draw()
        return game

    def __eq__(self, other) -> bool:
        return (
            (self.hand == other.hand)
            and (self.deck == other.deck)
            and (self.grave == other.grave)
            and (self.monsters == other.monsters)
            and (self.backrow == other.backrow)
            and (self.banished == other.banished)
            and (self.flags == other.flags)
            and (self.disruptions == other.disruptions)
        )

    def __hash__(self) -> int:
        return hash(
            (
                self.hand,
                self.deck,
                self.grave,
                self.monsters,
                self.backrow,
                self.banished,
                self.flags,
                self.disruptions,
            )
        )

    def __repr__(self) -> str:
        parts = [
            f"Hand: {self.hand}",
            f"Monsters: {self.monsters}",
            f"Backrow: {self.backrow}",
            f"Grave: {self.grave}",
            f"Banished: {self.banished}",
            f"Deck: {self.deck}",
        ]
        return "\n".join(parts)

    def copy(self) -> Game:
        return self.__class__(
            self.hand.copy(),
            self.deck.copy(),
            self.grave.copy(),
            self.monsters.copy(),
            self.backrow.copy(),
            self.banished.copy(),
            self.flags.copy(),
            self.disruptions.copy(),
        )

    def reset(self) -> None:
        while self.hand:
            self.deck.add(self.hand.cards.pop())
        while self.monsters:
            self.deck.add(self.monsters.cards.pop())
        while self.backrow:
            self.deck.add(self.backrow.cards.pop())
        while self.banished:
            self.deck.add(self.banished.cards.pop())
        self.deck.shuffle()
        for _ in range(5):
            self.draw()

    def move(self, source: CardGroup, dest: CardGroup, card: Card) -> None:
        source.remove(card)
        dest.add(card)

    def resource_available(self, resource: str) -> bool:
        return f"used:{resource}" not in self.flags

    def use_resource(self, resource: str) -> None:
        self.flags.add(f"used:{resource}")

    def hopt_available(self, card: Card, tag: Optional[str] = "*") -> bool:
        if not tag:
            return not any(
                [flag.startswith(f"hopt-{card.name}") for flag in self.flags]
            )
        return f"hopt-{card.name}-{tag}" not in self.flags

    def use_hopt(self, card: Card, tag: str = "*") -> None:
        self.flags.add(f"hopt-{card.name}-{tag}")

    def add_flag(self, flag: str) -> None:
        self.flags.add(flag)

    def has_flag(self, flag: str) -> bool:
        return flag in self.flags

    def draw(self) -> None:
        self.hand.add(self.deck.cards.pop(0))

    def disruption_report(self) -> str:
        return f"{self.value()} Points: {', '.join([repr(disruption) for disruption in self.disruptions])}"

    def value(self) -> int:
        return sum([disruption.point_value for disruption in self.disruptions])


class Manager:
    def __init__(self, initial_game: Game) -> None:
        self.func_list = [
            getattr(self.__class__, func)
            for func in dir(self.__class__)
            if callable(getattr(self.__class__, func)) and func.startswith("action")
        ]
        self.initial_game = initial_game

    def postprocess(self, game: Game) -> Game:
        return game

    def endphase(self, game: Game) -> Game:
        return game

    @classmethod
    def endphase(cls, end_games: List[Game]) -> str:
        return ""

    def run(self) -> Game:
        start = self.initial_game.copy()
        start.reset()
        state_queue = [(start, 0)]
        end_games = [self.initial_game.copy()]

        while state_queue:
            game, next_action = state_queue.pop(0)

            if next_action == len(self.func_list):
                end_games.append(self.endphase(game))
                continue

            new_game = self.func_list[next_action](self, game.copy())

            if new_game:
                new_game = self.postprocess(new_game)
                state_queue.append((new_game, 0))

            state_queue.append((game, next_action + 1))

        return max(end_games, key=lambda game: game.value())
