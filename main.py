import yaml
import random

STARTING_HAND_SIZE = 5

def read_config_file(filename: str):
    with open(filename, 'r') as stream:
        deck_specification, resources, rules = yaml.safe_load_all(stream)
    return deck_specification['deck'], resources['resources'], rules['rules']

class Rule():
    def __init__(self, name, paths, next_rule=None):
        self.name = name
        self.paths = paths
        self.next = next_rule

    @classmethod
    def build(cls, rule_from_yaml):
        return cls(rule_from_yaml['name'], rule_from_yaml['paths'], cls.build(rule_from_yaml['next']) if 'next' in rule_from_yaml else None)
    
    def __eq__(self, other):
        return (self.__class__ == other.__class__) and (self.name == other.name)
    
    def __hash__(self):
        return hash(self.name)

    def copy(self):
        return Rule(self.name, self.paths[:], self.next.copy() if self.next else None)

class Card():
    def __init__(self, name, tags=None, used=False):
        self.name = name
        self.tags = tags if tags else []
        self.used = used
    
    def __eq__(self, other):
        return (self.__class__ == other.__class__) and (self.name == other.name)
    
    def __hash__(self):
        return hash(self.name)

    def __repr__(self):
        return self.name

    def matches(self, condition):
        if condition.startswith('@'):
            return condition[1:] in self.tags
        else:
            return self.name == condition

class CardGroup():
    def __init__(self, cards):
        self.cards = cards

    def __repr__(self):
        return ', '.join([repr(card) for card in self.cards])

    def __eq__(self):
        return (self.__class__ == other.__class__) and (self.cards == other.cards)
    
    def __hash__(self):
        return hash(self.cards)
        
    def _copy(self):
        return self.__class__([Card(card.name, card.tags, card.used) for card in self.cards])
    
    def use(self, condition):
        copy = self._copy()
        for card in copy.cards:
            if card.used:
                continue
            if card.matches(condition):
                card.used = True
                return copy
        return None

class Hand(CardGroup):
    pass

class Deck(CardGroup):
    def __repr__(self):
        return f'Deck containing {self.cards.length} cards.'

    def shuffle(self):
        random.shuffle(self.cards)
    
    def draw(self, num):
        return [self.cards.pop(0) for _ in range(num)]

class Game():
    def __init__(self, hand, deck):
        self.hand = hand
        self.deck = deck

    @classmethod
    def build_from_spec(cls, deck_specification):
        deck = []

        for card in deck_specification:
            if 'tags' in card:
                for _ in range(card['count']):
                    deck.append(Card(card['name'], card['tags']))
            else:
                for _ in range(card['count']):
                    deck.append(Card(card['name']))

        deck = Deck(deck)
        deck.shuffle()
        hand = Hand(deck.draw(STARTING_HAND_SIZE))
        return cls(hand, deck)

    def match_resource(self, resource):
        if not resource:
            return self
        
        item = resource.pop(0)

        if 'hand-contains' in item:
            result = self.hand.use(item['hand-contains'])
            if result:
                copy = Game(result, self.deck)
                return copy.match_resource(resource)

        if 'deck-contains' in item:
            result = self.deck.use(item['deck-contains'])
            if result:
                copy = Game(self.hand, result)
                return copy.match_resource(resource)

        return None
        
    def match_path(self, resources, path):
        if not path:
            return self

        path_component = path.pop(0)
        resource = [item for item in resources[path_component]]
        result = self.match_resource(resource)
        if result:
            return self.match_path(resources, path)
        return None

    def match_rule(self, resources, rule, last_rule=None, depth=0):
        if not rule.paths:
            # No path of this rule succeeded. 
            return self, last_rule, depth
        path = rule.paths.pop(0).split(' & ')
        result = self.match_path(resources, path)
        if result:
            if rule.next:
                return self.match_rule(resources, rule.next.copy(), last_rule=rule.name, depth=depth+1)
            else:
                return self, rule.name, depth+1
        else:
            return self.match_rule(resources, rule, last_rule=last_rule, depth=depth)
        
if __name__ == '__main__':
    deck_specification, resources, rules = read_config_file('machina_nekroz.yml')
    game = Game.build_from_spec(deck_specification)
    print(game.hand)
    for base_rule in rules:
        result, final_rule, final_depth = game.match_rule(resources, Rule.build(base_rule))
        if final_depth:
            break
    print(final_rule)
