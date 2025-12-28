"""
Meld Finder - Discovers all valid melds and optimal meld combinations
"""

from typing import List, Set, Tuple, Optional, FrozenSet
from itertools import combinations
from five_crowns import Card, Suit, MeldValidator


class MeldFinder:
    """Finds all possible valid melds in a hand"""

    @staticmethod
    def find_all_books(hand: List[Card], wild_rank: str) -> List[List[Card]]:
        """
        Find all valid books (sets) that can be formed from the hand.
        Returns a list of all possible books.
        """
        books = []

        # Group cards by rank
        rank_groups = {}
        wilds = []

        for card in hand:
            if MeldValidator.is_wild(card, wild_rank):
                wilds.append(card)
            else:
                if card.rank not in rank_groups:
                    rank_groups[card.rank] = []
                rank_groups[card.rank].append(card)

        # For each rank, try to form books using different combinations
        for rank, cards_of_rank in rank_groups.items():
            # Try all combinations of this rank (3+) with various numbers of wilds
            for num_cards in range(3, len(cards_of_rank) + 1):
                for combo in combinations(cards_of_rank, num_cards):
                    book = list(combo)
                    if MeldValidator.is_valid_book(book, wild_rank):
                        books.append(book)

                    # Try adding wilds to this combination
                    for num_wilds in range(1, len(wilds) + 1):
                        if len(book) + num_wilds < 3:
                            continue
                        for wild_combo in combinations(wilds, num_wilds):
                            book_with_wilds = book + list(wild_combo)
                            if MeldValidator.is_valid_book(book_with_wilds, wild_rank):
                                books.append(book_with_wilds)

        # Also try books that are mostly wilds (with at least one real card)
        for rank, cards_of_rank in rank_groups.items():
            for card in cards_of_rank[:1]:  # Just need one card of this rank
                for num_wilds in range(2, len(wilds) + 1):
                    for wild_combo in combinations(wilds, num_wilds):
                        book = [card] + list(wild_combo)
                        if MeldValidator.is_valid_book(book, wild_rank):
                            books.append(book)

        return books

    @staticmethod
    def find_all_runs(hand: List[Card], wild_rank: str) -> List[List[Card]]:
        """
        Find all valid runs (sequences) that can be formed from the hand.
        Returns a list of all possible runs.
        """
        runs = []

        # Group cards by suit
        suit_groups = {}
        wilds = []

        for card in hand:
            if MeldValidator.is_wild(card, wild_rank):
                wilds.append(card)
            else:
                if card.suit not in suit_groups:
                    suit_groups[card.suit] = []
                suit_groups[card.suit].append(card)

        # For each suit, try to form runs
        for suit, cards_of_suit in suit_groups.items():
            # Sort by rank
            sorted_cards = sorted(cards_of_suit, key=lambda c: MeldValidator.RANK_VALUES[c.rank])

            # Try all combinations of cards from this suit
            for combo_size in range(3, len(sorted_cards) + 1):
                for combo in combinations(sorted_cards, combo_size):
                    run = list(combo)

                    # Try without wilds
                    if MeldValidator.is_valid_run(run, wild_rank):
                        runs.append(run)

                    # Try with different numbers of wilds
                    for num_wilds in range(1, len(wilds) + 1):
                        for wild_combo in combinations(wilds, num_wilds):
                            run_with_wilds = run + list(wild_combo)
                            if MeldValidator.is_valid_run(run_with_wilds, wild_rank):
                                runs.append(run_with_wilds)

        # Also try runs that are mostly wilds (with at least one real card)
        for suit, cards_of_suit in suit_groups.items():
            for combo_size in range(1, min(3, len(cards_of_suit) + 1)):
                for combo in combinations(cards_of_suit, combo_size):
                    for num_wilds in range(3 - combo_size, len(wilds) + 1):
                        for wild_combo in combinations(wilds, num_wilds):
                            run = list(combo) + list(wild_combo)
                            if len(run) >= 3 and MeldValidator.is_valid_run(run, wild_rank):
                                runs.append(run)

        return runs

    @staticmethod
    def find_all_melds(hand: List[Card], wild_rank: str) -> List[List[Card]]:
        """Find all possible melds (both books and runs) from hand"""
        books = MeldFinder.find_all_books(hand, wild_rank)
        runs = MeldFinder.find_all_runs(hand, wild_rank)
        return books + runs

    @staticmethod
    def _cards_to_frozenset(cards: List[Card]) -> FrozenSet[Tuple]:
        """Convert list of cards to hashable frozenset for deduplication"""
        return frozenset((c.rank, c.suit) for c in cards)

    @staticmethod
    def find_best_meld_combination(hand: List[Card], wild_rank: str) -> Tuple[List[List[Card]], int]:
        """
        Find the best combination of non-overlapping melds that minimizes remaining cards.
        Returns (list_of_melds, remaining_points)

        Uses greedy algorithm:
        1. Find all possible melds
        2. Try combinations that don't overlap
        3. Return combination that leaves minimum points
        """
        if not hand:
            return [], 0

        all_melds = MeldFinder.find_all_melds(hand, wild_rank)

        # Remove duplicate melds
        unique_melds = []
        seen = set()
        for meld in all_melds:
            meld_set = MeldFinder._cards_to_frozenset(meld)
            if meld_set not in seen:
                seen.add(meld_set)
                unique_melds.append(meld)

        # Try to find best combination of non-overlapping melds
        best_melds = []
        best_remaining_points = MeldFinder._calculate_hand_value(hand, wild_rank)

        # Use backtracking to find best combination
        MeldFinder._find_best_combination_recursive(
            hand, unique_melds, wild_rank, [], 0, best_remaining_points,
            lambda melds, points: (
                setattr(locals(), 'best_melds', melds),
                setattr(locals(), 'best_remaining_points', points)
            )
        )

        # Simpler greedy approach: try each meld as starting point
        for i, start_meld in enumerate(unique_melds):
            result = MeldFinder._greedy_meld_selection(hand, unique_melds, wild_rank, [start_meld])
            remaining_points = MeldFinder._calculate_remaining_points(hand, result, wild_rank)

            if remaining_points < best_remaining_points:
                best_remaining_points = remaining_points
                best_melds = result

        # Also try without any starting meld
        result = MeldFinder._greedy_meld_selection(hand, unique_melds, wild_rank, [])
        remaining_points = MeldFinder._calculate_remaining_points(hand, result, wild_rank)

        if remaining_points < best_remaining_points:
            best_remaining_points = remaining_points
            best_melds = result

        return best_melds, best_remaining_points

    @staticmethod
    def _greedy_meld_selection(hand: List[Card], all_melds: List[List[Card]],
                               wild_rank: str, current_melds: List[List[Card]]) -> List[List[Card]]:
        """
        Greedy algorithm to select melds.
        Repeatedly adds the meld that reduces remaining points the most.
        """
        used_cards = set()
        for meld in current_melds:
            for card in meld:
                used_cards.add(id(card))

        result = current_melds.copy()

        while True:
            best_meld = None
            best_points_saved = 0

            for meld in all_melds:
                # Check if meld overlaps with used cards
                if any(id(card) in used_cards for card in meld):
                    continue

                # Calculate points saved by this meld
                points_saved = sum(
                    MeldFinder._card_value(card, wild_rank) for card in meld
                )

                if points_saved > best_points_saved:
                    best_points_saved = points_saved
                    best_meld = meld

            if best_meld is None:
                break

            # Add this meld
            result.append(best_meld)
            for card in best_meld:
                used_cards.add(id(card))

        return result

    @staticmethod
    def _find_best_combination_recursive(hand: List[Card], all_melds: List[List[Card]],
                                        wild_rank: str, current_melds: List[List[Card]],
                                        start_idx: int, best_score: int,
                                        update_best) -> int:
        """Recursive helper for finding best meld combination (with pruning)"""
        # Calculate current score
        current_score = MeldFinder._calculate_remaining_points(hand, current_melds, wild_rank)

        if current_score < best_score:
            best_score = current_score
            # Update best found (this is a simplified approach)

        # If we've used all cards, we're done
        if current_score == 0:
            return 0

        # Try adding more melds
        used_cards = set(id(card) for meld in current_melds for card in meld)

        for i in range(start_idx, len(all_melds)):
            meld = all_melds[i]

            # Skip if meld overlaps with used cards
            if any(id(card) in used_cards for card in meld):
                continue

            # Recursively try with this meld added
            new_melds = current_melds + [meld]
            MeldFinder._find_best_combination_recursive(
                hand, all_melds, wild_rank, new_melds, i + 1, best_score, update_best
            )

        return best_score

    @staticmethod
    def _calculate_remaining_points(hand: List[Card], melds: List[List[Card]], wild_rank: str) -> int:
        """Calculate points from cards not in any meld"""
        used_cards = set(id(card) for meld in melds for card in meld)
        remaining = [card for card in hand if id(card) not in used_cards]
        return MeldFinder._calculate_hand_value(remaining, wild_rank)

    @staticmethod
    def _calculate_hand_value(cards: List[Card], wild_rank: str) -> int:
        """Calculate point value of cards"""
        total = 0
        for card in cards:
            total += MeldFinder._card_value(card, wild_rank)
        return total

    @staticmethod
    def _card_value(card: Card, wild_rank: str) -> int:
        """Get point value of a single card"""
        if MeldValidator.is_wild(card, wild_rank):
            return 20
        elif card.rank in ['J', 'Q', 'K']:
            return 10
        else:
            return int(card.rank)

    @staticmethod
    def can_go_out(hand: List[Card], wild_rank: str) -> Tuple[bool, Optional[List[List[Card]]]]:
        """
        Check if the hand can go out (all cards in valid melds).
        Returns (can_go_out, melds_or_none)
        """
        melds, remaining_points = MeldFinder.find_best_meld_combination(hand, wild_rank)

        if remaining_points == 0:
            return True, melds
        return False, None
