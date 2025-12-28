"""
Five Crowns Card Game - Meld Validation Implementation
"""

from dataclasses import dataclass
from typing import List, Optional, Tuple
from enum import Enum


class Suit(Enum):
    SPADES = "♠"
    HEARTS = "♥"
    CLUBS = "♣"
    DIAMONDS = "♦"
    STARS = "★"  # Five Crowns has 5 suits


@dataclass
class Card:
    rank: str  # '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K'
    suit: Suit
    
    def __repr__(self):
        return f"{self.rank}{self.suit.value}"
    
    def __eq__(self, other):
        return self.rank == other.rank and self.suit == other.suit
    
    def __hash__(self):
        return hash((self.rank, self.suit))


@dataclass
class ValidationResult:
    is_valid: bool
    error_message: Optional[str] = None


class MeldValidator:
    """Validates melds (books and runs) for Five Crowns"""
    
    # Rank ordering for sequences
    RANK_ORDER = ['3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
    RANK_VALUES = {rank: i for i, rank in enumerate(RANK_ORDER)}
    
    @staticmethod
    def get_wild_card(round_number: int) -> str:
        """
        Returns the wild card rank for a given round.
        Round 1: 3s are wild (3 cards dealt)
        Round 2: 4s are wild (4 cards dealt)
        ...
        Round 11: Ks are wild (13 cards dealt)
        """
        if round_number < 1 or round_number > 11:
            raise ValueError(f"Round must be 1-11, got {round_number}")
        return MeldValidator.RANK_ORDER[round_number - 1]
    
    @staticmethod
    def validate_all_melds(melds: List[List[Card]], wild_card_rank: str) -> ValidationResult:
        """
        Validates all melds without helping player optimize.
        Only checks if what they laid down follows rules.
        """
        if not melds:
            return ValidationResult(True, None)
        
        for i, meld in enumerate(melds):
            if len(meld) < 3:
                return ValidationResult(
                    False, 
                    f"Group {i+1} has only {len(meld)} cards (need 3+)"
                )
            
            # Check if it's a valid book OR run
            is_book = MeldValidator.is_valid_book(meld, wild_card_rank)
            is_run = MeldValidator.is_valid_run(meld, wild_card_rank)
            
            if not (is_book or is_run):
                return ValidationResult(
                    False,
                    f"Group {i+1} is neither a valid book nor run"
                )
        
        return ValidationResult(True, None)
    
    @staticmethod
    def is_wild(card: Card, wild_rank: str) -> bool:
        """Check if a card is wild (jokers are always wild, plus the round's wild card)"""
        return card.rank == wild_rank or card.rank == 'Joker'
    
    @staticmethod
    def is_valid_book(cards: List[Card], wild_rank: str) -> bool:
        """
        Book = 3+ cards of same rank (different suits)
        - All non-wild cards must be the same rank
        - No duplicate suits among non-wild cards
        - Must have at least one non-wild card
        """
        if len(cards) < 3:
            return False
        
        # Separate wilds from non-wilds
        non_wilds = [c for c in cards if not MeldValidator.is_wild(c, wild_rank)]
        
        if not non_wilds:
            return False  # Can't be all wilds - need at least one real card
        
        # All non-wilds must be same rank
        target_rank = non_wilds[0].rank
        if not all(c.rank == target_rank for c in non_wilds):
            return False
        
        # Can't have duplicate suits (except wilds can be any suit)
        suits_seen = set()
        for card in non_wilds:
            if card.suit in suits_seen:
                return False  # Duplicate suit
            suits_seen.add(card.suit)
        
        return True
    
    @staticmethod
    def is_valid_run(cards: List[Card], wild_rank: str) -> bool:
        """
        Run = 3+ cards of same suit in sequence
        - All non-wild cards must be the same suit
        - Cards must form a sequence (wilds can fill gaps or extend ends)
        - Must have at least one non-wild card
        """
        if len(cards) < 3:
            return False
        
        # Separate wilds from non-wilds
        non_wilds = [c for c in cards if not MeldValidator.is_wild(c, wild_rank)]
        
        if not non_wilds:
            return False  # Can't be all wilds
        
        # All non-wilds must be same suit
        target_suit = non_wilds[0].suit
        if not all(c.suit == target_suit for c in non_wilds):
            return False
        
        # Check if sequence is possible with wilds filling gaps
        sorted_cards = sorted(non_wilds, key=lambda c: MeldValidator.RANK_VALUES[c.rank])
        wild_count = len(cards) - len(non_wilds)
        
        # Check for duplicate ranks in non-wilds
        ranks_seen = set()
        for card in sorted_cards:
            if card.rank in ranks_seen:
                return False  # Can't have duplicate ranks in a run
            ranks_seen.add(card.rank)
        
        # Calculate minimum wilds needed to fill gaps between non-wild cards
        wilds_needed_for_gaps = 0
        for i in range(len(sorted_cards) - 1):
            gap = MeldValidator.RANK_VALUES[sorted_cards[i+1].rank] - MeldValidator.RANK_VALUES[sorted_cards[i].rank] - 1
            wilds_needed_for_gaps += gap
        
        # Check if we have enough wilds to fill all gaps
        if wilds_needed_for_gaps > wild_count:
            return False
        
        # Remaining wilds can extend either end of the sequence
        remaining_wilds = wild_count - wilds_needed_for_gaps
        
        # Calculate the minimum sequence span (from lowest to highest non-wild card)
        min_span = MeldValidator.RANK_VALUES[sorted_cards[-1].rank] - MeldValidator.RANK_VALUES[sorted_cards[0].rank] + 1
        
        # Total cards should equal min_span plus any wilds extending the ends
        expected_length = min_span + remaining_wilds
        
        if len(cards) != expected_length:
            return False
        
        # Check that we're not extending beyond valid ranks (3-K range)
        # Lowest possible rank if wilds extend downward
        lowest_rank_value = MeldValidator.RANK_VALUES[sorted_cards[0].rank]
        # Highest possible rank if wilds extend upward
        highest_rank_value = MeldValidator.RANK_VALUES[sorted_cards[-1].rank]
        
        # We can't extend below rank 0 (which is '3') or above rank 10 (which is 'K')
        if lowest_rank_value - remaining_wilds < 0:
            # Too many wilds to place at the beginning
            # They must fit at the end
            wilds_at_start = lowest_rank_value
            wilds_at_end = remaining_wilds - wilds_at_start
            if highest_rank_value + wilds_at_end > 10:
                return False
        elif highest_rank_value + remaining_wilds > 10:
            # Too many wilds to place at the end
            # They must fit at the beginning
            wilds_at_end = 10 - highest_rank_value
            wilds_at_start = remaining_wilds - wilds_at_end
            if lowest_rank_value - wilds_at_start < 0:
                return False
        
        return True


def create_card(rank: str, suit: str) -> Card:
    """Helper to create cards more easily"""
    suit_map = {
        'S': Suit.SPADES,
        'H': Suit.HEARTS,
        'C': Suit.CLUBS,
        'D': Suit.DIAMONDS,
        'T': Suit.STARS
    }
    return Card(rank, suit_map[suit])
