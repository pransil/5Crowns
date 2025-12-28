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
    JOKER = "🃏"  # Joker suit (jokers are always wild)


@dataclass
class Card:
    rank: str  # '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'Joker'
    suit: Suit
    
    def __repr__(self):
        if self.rank == 'Joker':
            return "Joker"
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
        # Check if sequence is at boundaries (considering both wild and non-wild cards)
        has_rank_k = any(c.rank == 'K' for c in cards)
        # Check if we have a 3 that's being used (either as non-wild or as wild representing 3)
        has_rank_3_as_start = False
        if lowest_rank_value == 0:  # Non-wild 3 is the lowest
            has_rank_3_as_start = True
        elif wild_rank == '3':  # 3s are wild this round
            # Check if we have a wild 3 that would be at the start of the sequence
            # This is tricky - we need to see if a wild 3 is being used at position 0
            # For simplicity, if we have any 3 in cards and it's wild, and lowest non-wild is 4,
            # then the sequence effectively starts at 3
            if any(c.rank == '3' for c in cards) and lowest_rank_value == 1:  # 4 is at position 1
                has_rank_3_as_start = True
        
        # If we have remaining wilds, check if they can be placed within bounds
        if remaining_wilds > 0:
            # Calculate how many wilds can be placed at each end
            # Can't extend below position 0 (rank '3')
            max_wilds_at_start = lowest_rank_value
            # Can't extend above position 10 (rank 'K')
            max_wilds_at_end = 10 - highest_rank_value
            
            # Stricter rule: if sequence is at a boundary, we can't add wilds at all
            # This prevents extending sequences that are already at the limits
            if has_rank_k and highest_rank_value == 10:  # Sequence ends at K
                # Can't add wilds - would extend beyond K
                return False
            if has_rank_3_as_start:  # Sequence effectively starts at 3
                # Can't add wilds - would extend below 3
                return False
            
            # For sequences not at boundaries, check if we can place all remaining wilds
            if remaining_wilds > max_wilds_at_start + max_wilds_at_end:
                return False
        
        return True


def create_card(rank: str, suit: str) -> Card:
    """Helper to create cards more easily"""
    suit_map = {
        'S': Suit.SPADES,
        'H': Suit.HEARTS,
        'C': Suit.CLUBS,
        'D': Suit.DIAMONDS,
        'T': Suit.STARS,
        'J': Suit.JOKER  # For jokers, though create_joker() is preferred
    }
    return Card(rank, suit_map[suit])


def create_joker() -> Card:
    """Helper to create a joker card (always wild)"""
    return Card('Joker', Suit.JOKER)
