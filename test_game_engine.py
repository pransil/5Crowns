"""
Tests for Game Engine, Meld Finder, and AI Player
"""

import unittest
from game_engine import Deck, Player, GameState, GameEngine
from meld_finder import MeldFinder
from ai_player import AIStrategy
from five_crowns import create_card, create_joker, MeldValidator


class TestDeck(unittest.TestCase):
    """Test deck functionality"""

    def test_deck_initialization(self):
        """Test that deck is initialized with correct number of cards"""
        deck = Deck()
        # 2 copies * 11 ranks * 5 suits + 6 jokers = 116 cards
        self.assertEqual(len(deck.cards), 116)

    def test_deck_shuffle(self):
        """Test that shuffle changes card order"""
        deck = Deck()
        original_order = deck.cards.copy()
        deck.shuffle()
        # Very unlikely to have same order after shuffle (though technically possible)
        self.assertNotEqual(deck.cards, original_order)

    def test_deal_cards(self):
        """Test dealing cards"""
        deck = Deck()
        dealt = deck.deal(5)
        self.assertEqual(len(dealt), 5)
        self.assertEqual(len(deck.cards), 111)  # 116 - 5

    def test_draw_and_discard(self):
        """Test draw and discard functionality"""
        deck = Deck()
        card = deck.draw()
        self.assertEqual(len(deck.cards), 115)

        deck.add_to_discard(card)
        self.assertEqual(len(deck.discard_pile), 1)

        drawn_discard = deck.draw_from_discard()
        self.assertEqual(drawn_discard, card)
        self.assertEqual(len(deck.discard_pile), 0)


class TestPlayer(unittest.TestCase):
    """Test player functionality"""

    def test_player_creation(self):
        """Test creating a player"""
        player = Player(name="Test", is_human=True)
        self.assertEqual(player.name, "Test")
        self.assertTrue(player.is_human)
        self.assertEqual(len(player.hand), 0)
        self.assertEqual(player.score, 0)

    def test_calculate_hand_value(self):
        """Test hand value calculation"""
        player = Player(name="Test")
        player.hand = [
            create_card('5', 'H'),  # 5 points
            create_card('J', 'S'),  # 10 points
            create_card('K', 'C'),  # 10 points
        ]
        # 5s are wild in this test
        value = player.calculate_hand_value(wild_rank='5')
        self.assertEqual(value, 20 + 10 + 10)  # 5 is wild (20), J and K are 10 each

    def test_add_remove_card(self):
        """Test adding and removing cards"""
        player = Player(name="Test")
        card = create_card('7', 'H')

        player.add_card(card)
        self.assertEqual(len(player.hand), 1)

        player.remove_card(card)
        self.assertEqual(len(player.hand), 0)


class TestMeldFinder(unittest.TestCase):
    """Test meld finding algorithms"""

    def test_find_simple_book(self):
        """Test finding a simple book"""
        hand = [
            create_card('7', 'H'),
            create_card('7', 'S'),
            create_card('7', 'C'),
            create_card('5', 'D')
        ]
        books = MeldFinder.find_all_books(hand, '3')
        # Should find at least one book of 7s
        self.assertTrue(any(len(book) == 3 for book in books))

    def test_find_simple_run(self):
        """Test finding a simple run"""
        hand = [
            create_card('5', 'H'),
            create_card('6', 'H'),
            create_card('7', 'H'),
            create_card('9', 'S')
        ]
        runs = MeldFinder.find_all_runs(hand, '3')
        # Should find at least one run
        self.assertTrue(len(runs) > 0)

    def test_can_go_out_true(self):
        """Test detecting when a hand can go out"""
        hand = [
            create_card('7', 'H'),
            create_card('7', 'S'),
            create_card('7', 'C'),
            create_card('5', 'D'),
            create_card('6', 'D'),
            create_card('8', 'D')  # Can use 7 as wild for run
        ]
        can_go, melds = MeldFinder.can_go_out(hand, '7')
        self.assertTrue(can_go)
        self.assertIsNotNone(melds)

    def test_can_go_out_false(self):
        """Test detecting when a hand cannot go out"""
        hand = [
            create_card('3', 'H'),
            create_card('7', 'S'),
            create_card('K', 'C')
        ]
        can_go, melds = MeldFinder.can_go_out(hand, '4')
        self.assertFalse(can_go)

    def test_find_best_meld_combination(self):
        """Test finding best combination of melds"""
        hand = [
            create_card('5', 'H'),
            create_card('6', 'H'),
            create_card('7', 'H'),
            create_card('8', 'S'),
            create_card('8', 'C'),
            create_card('8', 'D')
        ]
        melds, points = MeldFinder.find_best_meld_combination(hand, '3')

        # Should find both a run and a book
        self.assertEqual(len(melds), 2)
        self.assertEqual(points, 0)  # All cards in melds


class TestAIStrategy(unittest.TestCase):
    """Test AI decision-making"""

    def test_evaluate_wild_card(self):
        """Test that wild cards are valued highly"""
        hand = [create_card('7', 'H')]
        wild_card = create_card('5', 'S')
        normal_card = create_card('9', 'C')

        wild_score = AIStrategy.evaluate_card_usefulness(wild_card, hand, '5')
        normal_score = AIStrategy.evaluate_card_usefulness(normal_card, hand, '5')

        self.assertGreater(wild_score, normal_score)

    def test_decide_draw_wild_from_discard(self):
        """Test that AI takes wilds from discard pile"""
        hand = [create_card('7', 'H')]
        wild_discard = create_card('5', 'S')

        should_take = AIStrategy.decide_draw_source(hand, wild_discard, '5')
        self.assertTrue(should_take)

    def test_decide_discard_least_useful(self):
        """Test that AI discards least useful card"""
        hand = [
            create_card('7', 'H'),
            create_card('7', 'S'),  # Useful - pair
            create_card('K', 'C'),  # Less useful - high value, no pairs/sequences
        ]

        to_discard = AIStrategy.decide_discard(hand, '3')
        # Should discard the K (least useful)
        self.assertEqual(to_discard.rank, 'K')


class TestGameEngine(unittest.TestCase):
    """Test game engine"""

    def test_game_initialization(self):
        """Test initializing a game"""
        engine = GameEngine([("Player 1", True), ("Computer", False)])
        self.assertEqual(len(engine.state.players), 2)
        self.assertEqual(engine.state.round_number, 1)

    def test_round_setup(self):
        """Test setting up a round"""
        engine = GameEngine([("Player 1", True), ("Computer", False)])
        engine.setup_round()

        # Check that cards were dealt
        cards_per_hand = engine.state.get_cards_per_hand()
        for player in engine.state.players:
            self.assertEqual(len(player.hand), cards_per_hand)

        # Check that discard pile has one card
        self.assertIsNotNone(engine.state.deck.peek_discard())

    def test_draw_card(self):
        """Test drawing a card"""
        engine = GameEngine([("Player 1", True)])
        engine.setup_round()

        player = engine.state.current_player()
        initial_hand_size = len(player.hand)

        engine.draw_card(from_discard=False)
        self.assertEqual(len(player.hand), initial_hand_size + 1)

    def test_try_go_out_success(self):
        """Test successfully going out"""
        engine = GameEngine([("Player 1", True)])
        engine.setup_round()

        player = engine.state.current_player()

        # Give player a valid hand that can go out
        player.hand = [
            create_card('7', 'H'),
            create_card('7', 'S'),
            create_card('7', 'C')
        ]

        melds = [[
            create_card('7', 'H'),
            create_card('7', 'S'),
            create_card('7', 'C')
        ]]

        success, error = engine.try_go_out(melds)
        self.assertTrue(success)
        self.assertIsNone(error)
        self.assertTrue(engine.state.round_over)

    def test_try_go_out_invalid_melds(self):
        """Test going out with invalid melds"""
        engine = GameEngine([("Player 1", True)])
        engine.setup_round()

        player = engine.state.current_player()
        player.hand = [
            create_card('7', 'H'),
            create_card('8', 'S'),
            create_card('9', 'C')
        ]

        # Invalid meld (not a book or run)
        melds = [[
            create_card('7', 'H'),
            create_card('8', 'S'),
            create_card('9', 'C')
        ]]

        success, error = engine.try_go_out(melds)
        self.assertFalse(success)
        self.assertIsNotNone(error)


if __name__ == '__main__':
    unittest.main(verbosity=2)
