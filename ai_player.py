"""
AI Player - Intelligent computer opponent for Five Crowns
"""

from typing import List, Tuple, Optional
from five_crowns import Card, MeldValidator
from meld_finder import MeldFinder
from game_engine import Player, GameState


class AIStrategy:
    """AI strategy for playing Five Crowns"""

    @staticmethod
    def evaluate_card_usefulness(card: Card, hand: List[Card], wild_rank: str) -> float:
        """
        Evaluate how useful a card is (higher = more useful).
        Considers:
        - Wild cards are very useful
        - Cards that fit into potential melds
        - Cards with duplicates (for books)
        - Cards in sequence (for runs)
        """
        score = 0.0

        # Wild cards are extremely useful
        if MeldValidator.is_wild(card, wild_rank):
            return 100.0

        # Count duplicates of same rank (useful for books)
        same_rank = sum(1 for c in hand if c.rank == card.rank and c != card)
        score += same_rank * 15  # Each duplicate adds value

        # Count cards of same suit (useful for runs)
        same_suit = [c for c in hand if c.suit == card.suit and c != card and not MeldValidator.is_wild(c, wild_rank)]

        if same_suit:
            # Sort to check for sequences
            same_suit_sorted = sorted(same_suit, key=lambda c: MeldValidator.RANK_VALUES[c.rank])
            card_rank_value = MeldValidator.RANK_VALUES[card.rank]

            # Check if card is adjacent to or near other cards of same suit
            for other in same_suit_sorted:
                other_rank_value = MeldValidator.RANK_VALUES[other.rank]
                distance = abs(card_rank_value - other_rank_value)

                if distance == 1:  # Adjacent cards
                    score += 20
                elif distance == 2:  # One card away (could fill with wild)
                    score += 10
                elif distance == 3:  # Two cards away
                    score += 5

        # Lower value cards are slightly less useful (easier to go out with low points)
        card_points = AIStrategy._get_card_points(card, wild_rank)
        score -= card_points * 0.5

        return score

    @staticmethod
    def _get_card_points(card: Card, wild_rank: str) -> int:
        """Get point value of a card"""
        if MeldValidator.is_wild(card, wild_rank):
            return 20
        elif card.rank in ['J', 'Q', 'K']:
            return 10
        else:
            return int(card.rank)

    @staticmethod
    def decide_draw_source(hand: List[Card], discard_top: Optional[Card], wild_rank: str) -> bool:
        """
        Decide whether to draw from discard pile or deck.
        Returns True to draw from discard, False to draw from deck.
        """
        if discard_top is None:
            return False  # Must draw from deck

        # Always take wilds from discard
        if MeldValidator.is_wild(discard_top, wild_rank):
            return True

        # Check if discard card is useful
        discard_usefulness = AIStrategy.evaluate_card_usefulness(discard_top, hand, wild_rank)

        # Take from discard if usefulness is high
        # Threshold: if usefulness > 25, it's worth taking
        return discard_usefulness > 25

    @staticmethod
    def decide_discard(hand: List[Card], wild_rank: str) -> Card:
        """
        Decide which card to discard from hand.
        Discards the least useful card.
        """
        if not hand:
            raise ValueError("Cannot discard from empty hand")

        # Evaluate usefulness of each card
        card_scores = []
        for card in hand:
            usefulness = AIStrategy.evaluate_card_usefulness(card, hand, wild_rank)
            card_scores.append((card, usefulness))

        # Sort by usefulness (ascending) and discard least useful
        card_scores.sort(key=lambda x: x[1])
        return card_scores[0][0]

    @staticmethod
    def should_go_out(hand: List[Card], wild_rank: str, game_state: GameState) -> Tuple[bool, Optional[List[List[Card]]]]:
        """
        Decide if AI should attempt to go out.
        Returns (should_go_out, melds)
        """
        # Check if we can go out
        can_go_out, melds = MeldFinder.can_go_out(hand, wild_rank)

        if not can_go_out:
            return False, None

        # If we can go out, decide if we should
        # Strategy: Go out if:
        # 1. We can use all cards (no remaining points)
        # 2. OR it's late in the game (round 8+)
        # 3. OR we have high point cards we want to get rid of

        # Check if any opponent is close to going out (has few cards)
        # For now, always go out if possible
        return True, melds

    @staticmethod
    def play_turn(player: Player, game_state: GameState) -> Tuple[str, Optional[List[List[Card]]]]:
        """
        Execute a full AI turn.
        Returns (action, melds_if_going_out)
        action can be: 'continue', 'go_out'
        """
        wild_rank = game_state.get_wild_rank()
        discard_top = game_state.deck.peek_discard()

        # Step 1: Decide whether to draw from discard or deck
        from_discard = AIStrategy.decide_draw_source(player.hand, discard_top, wild_rank)

        # Step 2: Draw card (this is handled externally by game engine)
        # For now, return the decision
        draw_source = "discard" if from_discard else "deck"

        # After drawing (assumed to be done by caller), decide what to discard
        # This is also handled externally

        # Step 3: Check if we can/should go out
        should_go, melds = AIStrategy.should_go_out(player.hand, wild_rank, game_state)

        if should_go:
            return 'go_out', melds

        return 'continue', None


class AIPlayer:
    """Wrapper for AI player actions"""

    @staticmethod
    def take_turn(game_engine, player: Player) -> Tuple[bool, dict]:
        """
        Execute a complete AI turn using the game engine.
        Returns (went_out, turn_info)
        where turn_info contains: {'draw_source': str, 'drew_card': Card, 'discarded': Card or None}
        """
        from game_engine import GameEngine

        state = game_engine.state
        wild_rank = state.get_wild_rank()
        turn_info = {}

        # Step 1: Draw a card
        discard_top = state.deck.peek_discard()
        from_discard = AIStrategy.decide_draw_source(player.hand, discard_top, wild_rank)

        # Draw the card
        if from_discard and game_engine.can_draw_from_discard():
            drawn_card = game_engine.draw_card(from_discard=True)
            turn_info['draw_source'] = 'discard'
        else:
            drawn_card = game_engine.draw_card(from_discard=False)
            turn_info['draw_source'] = 'deck'

        turn_info['drew_card'] = drawn_card

        # Step 2: Check if we can go out
        can_go_out, melds = MeldFinder.can_go_out(player.hand, wild_rank)

        if can_go_out:
            # Try to go out (lay down all cards)
            success, error = game_engine.try_go_out(melds)
            if success:
                turn_info['discarded'] = None
                return True, turn_info
            # If failed for some reason, continue with discard

        # Step 3: Can't go out, so discard a card and end turn
        card_to_discard = AIStrategy.decide_discard(player.hand, wild_rank)
        game_engine.discard_card(card_to_discard)
        turn_info['discarded'] = card_to_discard

        return False, turn_info
