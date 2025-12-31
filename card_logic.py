from collections import Counter

RANKS = ['3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A', '2']
SUITS = ['♦', '♣', '♥', '♠']
RANK_ORDER = {r: i for i, r in enumerate(RANKS)}
SUIT_ORDER = {s: i for i, s in enumerate(SUITS)}

class Card:
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit
        self.score = (RANK_ORDER[rank] * 4) + SUIT_ORDER[suit]
        self.rank_val = RANK_ORDER[rank]