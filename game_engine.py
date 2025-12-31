import random
from collections import Counter
from card_logic import Card, RANKS, SUITS

class GameEngine:
    @staticmethod
    def get_combo_info(cards):
        if not cards: return None
        n = len(cards)
        if n == 1: return ("Single", cards[0].score)
        if n == 2 and cards[0].rank == cards[1].rank: return ("Pair", cards[1].score)
        if n == 5:
            r = sorted([c.rank_val for c in cards])
            s = [c.suit for c in cards]
            c_counts = Counter(r)
            counts = sorted(c_counts.values())
            is_st = all(r[i] == r[0] + i for i in range(5))
            is_fl = len(set(s)) == 1
            if is_st and is_fl: return ("Straight Flush", r[-1] + 1000)
            if counts == [1, 4]: return ("Four of a Kind", r[2] + 800)
            if counts == [2, 3]: return ("Full House", r[2] + 600)
            if is_fl: return ("Flush", max([c.score for c in cards]))
            if is_st: return ("Straight", r[-1])
        return None

    @staticmethod
    def validate_move(table_cards, table_type, new_info):
        if not table_cards: return True
        # BOM Logic
        if table_type[0] == "Single" and table_cards[0].rank == '2':
            if new_info[0] in ["Four of a Kind", "Straight Flush"]: return True
        if new_info[0] != table_type[0]: return False
        return new_info[1] > table_type[1]