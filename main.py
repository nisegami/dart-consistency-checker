import yaml
import random

STARTING_HAND_SIZE = 5
NUM_ITERATIONS = 100000

def read_config_file(filename):
    with open(filename, 'r') as stream:
        deck_specification, resources, rules = yaml.safe_load_all(stream)
    return deck_specification['deck'], resources['resources'], [Rule.build(rule) for rule in  rules['rules']]

def generate_statistics(filename):
    deck_specification, resources, rules = read_config_file(filename)
    game = Game.build_from_spec(deck_specification)
    data = {}
    for i in range(NUM_ITERATIONS):
        if not (i%500): print(i)
        _, rule, report = game.simulate(resources, [rule.copy() for rule in rules])
        report = str(report)
        if rule not in data:
            data[rule] = {}
        if report not in data[rule]:
            data[rule][report] = 0
        data[rule][report] += 1
        game.reset()
    return game, data

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
    def __init__(self, name, hopt=False, tags=None, report_as=None, used=False):
        self.name = name
        self.hopt = hopt
        self.tags = tags if tags else []
        self.report_as = report_as
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
        return self.__class__([Card(card.name, card.hopt, card.tags, card.used) for card in self.cards])
    
    def use(self, condition, hopt_tracker=None):
        copy = self._copy()
        for card in copy.cards:
            if card.used or (card.hopt and card in hopt_tracker):
                continue
            if card.matches(condition):
                card.used = True
                hopt_tracker.append(card)
                return copy
        return None

class Hand(CardGroup):
    def report(self):
        report_data = {}
        for card in self.cards:
            if card.report_as:
                if card.report_as not in report_data:
                    report_data[card.report_as] = 0
                report_data[card.report_as] += 1
        return report_data

class Deck(CardGroup):
    def __repr__(self):
        return f'Deck containing {len(self.cards)} cards.'

    def shuffle(self):
        random.shuffle(self.cards)
    
    def draw(self, num):
        return [self.cards.pop(0) for _ in range(num)]

class Game():
    def __init__(self, hand, deck, hopt_tracker=[]):
        self.hand = hand
        self.deck = deck
        self.hopt_tracker = hopt_tracker

    @classmethod
    def build_from_spec(cls, deck_specification):
        deck = []

        for card in deck_specification:
            tags = card['tags'] if 'tags' in card else None
            report_as = card['report-as'] if 'report-as' in card else None
            hopt = card['hopt'] if 'hopt' in card else False
            for _ in range(card['count']):
                deck.append(Card(card['name'], hopt, tags, report_as))

        deck = Deck(deck)
        print(f'Deck constructed with {len(deck.cards)} cards.')
        deck.shuffle()
        hand = Hand(deck.draw(STARTING_HAND_SIZE))
        return cls(hand, deck)

    def match_resource(self, resource):
        if not resource:
            return self
        
        item = resource.pop(0)

        if 'hand-contains' in item:
            result = self.hand.use(item['hand-contains'], self.hopt_tracker)
            if result:
                copy = Game(result, self.deck, self.hopt_tracker)
                return copy.match_resource(resource)

        if 'deck-contains' in item:
            result = self.deck.use(item['deck-contains'], self.hopt_tracker)
            if result:
                copy = Game(self.hand, result, self.hopt_tracker)
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

    def match_rules(self, resources, rules):
        deepest_result = self
        deepest_rule = None
        max_depth = 0
        for rule in rules:
            result, final_rule, final_depth = self.match_rule(resources, rule)
            if final_depth > max_depth:
                deepest_result = result
                deepest_rule = final_rule
        return deepest_result, deepest_rule

    def simulate(self, resources, rules):
        result, rule = self.match_rules(resources, rules)
        report = self.hand.report()
        return result, rule, report

    def reset(self):
        self.hopt_tracker.clear()
        while self.hand.cards:
            self.deck.cards.append(self.hand.cards.pop())
        for card in self.deck.cards:
            card.used = False
        self.deck.shuffle()
        self.hand = Hand(self.deck.draw(STARTING_HAND_SIZE))
        
if __name__ == '__main__':
    game, data = generate_statistics('machina_nekroz.yml')
    for rule, report_counts in data.items():
        count = sum([count for _, count in report_counts.items()])
        print(rule, 100 * count / float(NUM_ITERATIONS))