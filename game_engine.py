"""
Five Crowns Game Engine - Deck, Game State, and Turn Management
"""

import random
from dataclasses import dataclass, field
from typing import List, Optional, Set, Tuple
from five_crowns import Card, Suit, MeldValidator, create_card, create_joker


class Deck:
    """Manages the deck of cards for Five Crowns"""

    def __init__(self):
        self.cards: List[Card] = []
        self.discard_pile: List[Card] = []
        self._initialize_deck()

    def _initialize_deck(self):
        """
        Initialize a Five Crowns deck:
        - 2 copies of each card (ranks 3-K in 5 suits) = 2 * 11 * 5 = 110 cards
        - 6 jokers
        Total: 116 cards
        """
        ranks = ['3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
        suits = [Suit.SPADES, Suit.HEARTS, Suit.CLUBS, Suit.DIAMONDS, Suit.STARS]

        # Add 2 copies of each card
        for _ in range(2):
            for rank in ranks:
                for suit in suits:
                    self.cards.append(Card(rank, suit))

        # Add 6 jokers
        for _ in range(6):
            self.cards.append(create_joker())

    def shuffle(self):
        """Shuffle the deck"""
        random.shuffle(self.cards)

    def deal(self, num_cards: int) -> List[Card]:
        """Deal specified number of cards from the deck"""
        if len(self.cards) < num_cards:
            raise ValueError(f"Not enough cards in deck: {len(self.cards)} < {num_cards}")

        dealt_cards = []
        for _ in range(num_cards):
            dealt_cards.append(self.cards.pop())
        return dealt_cards

    def draw(self) -> Card:
        """Draw a single card from the deck"""
        if not self.cards:
            raise ValueError("Deck is empty")
        return self.cards.pop()

    def add_to_discard(self, card: Card):
        """Add a card to the discard pile"""
        self.discard_pile.append(card)

    def draw_from_discard(self) -> Card:
        """Draw the top card from the discard pile"""
        if not self.discard_pile:
            raise ValueError("Discard pile is empty")
        return self.discard_pile.pop()

    def peek_discard(self) -> Optional[Card]:
        """Look at the top card of the discard pile without removing it"""
        return self.discard_pile[-1] if self.discard_pile else None

    def cards_remaining(self) -> int:
        """Return number of cards left in deck"""
        return len(self.cards)


@dataclass
class Player:
    """Represents a player in the game"""
    name: str
    hand: List[Card] = field(default_factory=list)
    score: int = 0
    is_human: bool = True

    def add_card(self, card: Card):
        """Add a card to the player's hand"""
        self.hand.append(card)

    def remove_card(self, card: Card):
        """Remove a card from the player's hand"""
        self.hand.remove(card)

    def calculate_hand_value(self, wild_rank: str) -> int:
        """
        Calculate the point value of cards remaining in hand.
        - 3-10: face value
        - J, Q, K: 10 points each
        - Wilds and Jokers: 20 points each
        """
        total = 0
        for card in self.hand:
            if MeldValidator.is_wild(card, wild_rank):
                total += 20
            elif card.rank in ['J', 'Q', 'K']:
                total += 10
            else:
                total += int(card.rank)
        return total

    def sort_hand(self):
        """Sort hand by suit then rank for easier viewing"""
        suit_order = {
            Suit.SPADES: 0,
            Suit.HEARTS: 1,
            Suit.CLUBS: 2,
            Suit.DIAMONDS: 3,
            Suit.STARS: 4,
            Suit.JOKER: 5
        }

        self.hand.sort(key=lambda c: (
            suit_order.get(c.suit, 99),
            MeldValidator.RANK_VALUES.get(c.rank, -1)
        ))


@dataclass
class GameState:
    """Tracks the current state of the game"""
    round_number: int  # 1-11
    players: List[Player]
    deck: Deck
    current_player_index: int = 0
    round_over: bool = False
    game_over: bool = False

    def get_wild_rank(self) -> str:
        """Get the wild card rank for current round"""
        return MeldValidator.get_wild_card(self.round_number)

    def get_cards_per_hand(self) -> int:
        """Get number of cards dealt in current round (round 1 = 3 cards, round 11 = 13 cards)"""
        return self.round_number + 2

    def current_player(self) -> Player:
        """Get the current player"""
        return self.players[self.current_player_index]

    def next_player(self):
        """Move to the next player"""
        self.current_player_index = (self.current_player_index + 1) % len(self.players)

    def start_new_round(self):
        """Initialize a new round"""
        if self.round_number > 11:
            self.game_over = True
            return

        # Reset deck
        self.deck = Deck()
        self.deck.shuffle()

        # Clear hands
        for player in self.players:
            player.hand = []

        # Deal cards
        cards_to_deal = self.get_cards_per_hand()
        for player in self.players:
            player.hand = self.deck.deal(cards_to_deal)
            player.sort_hand()

        # Flip one card to start discard pile
        self.deck.add_to_discard(self.deck.draw())

        # Reset round state
        self.round_over = False
        self.current_player_index = 0


class GameEngine:
    """Main game controller"""

    def __init__(self, player_names: List[Tuple[str, bool]]):
        """
        Initialize game with players.
        player_names: List of (name, is_human) tuples
        """
        players = [Player(name=name, is_human=is_human) for name, is_human in player_names]
        self.state = GameState(
            round_number=1,
            players=players,
            deck=Deck()
        )

    def setup_round(self):
        """Setup a new round"""
        self.state.start_new_round()

    def can_draw_from_deck(self) -> bool:
        """Check if player can draw from deck"""
        return self.state.deck.cards_remaining() > 0

    def can_draw_from_discard(self) -> bool:
        """Check if player can draw from discard pile"""
        return self.state.deck.peek_discard() is not None

    def draw_card(self, from_discard: bool = False) -> Card:
        """
        Draw a card for the current player.
        Returns the drawn card.
        """
        if from_discard:
            card = self.state.deck.draw_from_discard()
        else:
            card = self.state.deck.draw()

        self.state.current_player().add_card(card)
        return card

    def discard_card(self, card: Card):
        """
        Discard a card from current player's hand.
        """
        player = self.state.current_player()
        player.remove_card(card)
        self.state.deck.add_to_discard(card)

    def try_go_out(self, melds: List[List[Card]]) -> Tuple[bool, Optional[str]]:
        """
        Attempt to go out with the given melds.
        Returns (success, error_message)
        """
        player = self.state.current_player()
        wild_rank = self.state.get_wild_rank()

        # Check that all cards are accounted for
        cards_in_melds = sum(len(meld) for meld in melds)
        if cards_in_melds != len(player.hand):
            return False, f"Melds use {cards_in_melds} cards but hand has {len(player.hand)}"

        # Check that all cards in melds are from player's hand
        meld_cards = set()
        for meld in melds:
            for card in meld:
                meld_cards.add(card)

        hand_cards = set(player.hand)
        if meld_cards != hand_cards:
            return False, "Melds contain cards not in hand"

        # Validate the melds
        validation_result = MeldValidator.validate_all_melds(melds, wild_rank)
        if not validation_result.is_valid:
            return False, validation_result.error_message

        # Success - player goes out
        # Clear their hand since they laid down all cards
        player.hand = []
        self.state.round_over = True
        return True, None

    def end_round(self):
        """
        End the current round.
        Note: Scores are calculated in announce_round_end() after players arrange melds.
        This just increments the round number.
        """
        # Move to next round
        self.state.round_number += 1

    def get_winner(self) -> Optional[Player]:
        """Get the winner (lowest score) after all rounds complete"""
        if not self.state.game_over:
            return None

        return min(self.state.players, key=lambda p: p.score)
