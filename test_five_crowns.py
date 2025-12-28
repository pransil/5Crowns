"""
Tests for Five Crowns Meld Validation
"""

import unittest
from five_crowns import Card, Suit, MeldValidator, ValidationResult, create_card, create_joker


class TestWildCardRounds(unittest.TestCase):
    """Test that wild cards are correct for each round"""
    
    def test_round_wild_cards(self):
        self.assertEqual(MeldValidator.get_wild_card(1), '3')
        self.assertEqual(MeldValidator.get_wild_card(2), '4')
        self.assertEqual(MeldValidator.get_wild_card(3), '5')
        self.assertEqual(MeldValidator.get_wild_card(4), '6')
        self.assertEqual(MeldValidator.get_wild_card(5), '7')
        self.assertEqual(MeldValidator.get_wild_card(6), '8')
        self.assertEqual(MeldValidator.get_wild_card(7), '9')
        self.assertEqual(MeldValidator.get_wild_card(8), '10')
        self.assertEqual(MeldValidator.get_wild_card(9), 'J')
        self.assertEqual(MeldValidator.get_wild_card(10), 'Q')
        self.assertEqual(MeldValidator.get_wild_card(11), 'K')


class TestValidBooks(unittest.TestCase):
    """Test valid book (set) formations"""
    
    def test_simple_book_no_wilds(self):
        """Three 7s of different suits"""
        cards = [
            create_card('7', 'H'),
            create_card('7', 'S'),
            create_card('7', 'C')
        ]
        self.assertTrue(MeldValidator.is_valid_book(cards, '3'))
    
    def test_book_with_wild(self):
        """Two 9s plus a wild 5"""
        cards = [
            create_card('9', 'H'),
            create_card('9', 'S'),
            create_card('5', 'C')  # Wild card in round 3
        ]
        self.assertTrue(MeldValidator.is_valid_book(cards, '5'))
    
    def test_book_four_cards(self):
        """Four Jacks"""
        cards = [
            create_card('J', 'H'),
            create_card('J', 'S'),
            create_card('J', 'C'),
            create_card('J', 'D')
        ]
        self.assertTrue(MeldValidator.is_valid_book(cards, '3'))
    
    def test_book_five_suits(self):
        """All five suits of 8s"""
        cards = [
            create_card('8', 'H'),
            create_card('8', 'S'),
            create_card('8', 'C'),
            create_card('8', 'D'),
            create_card('8', 'T')  # Stars
        ]
        self.assertTrue(MeldValidator.is_valid_book(cards, '3'))


class TestInvalidBooks(unittest.TestCase):
    """Test invalid book formations"""
    
    def test_book_duplicate_suits(self):
        """Two hearts - invalid"""
        cards = [
            create_card('7', 'H'),
            create_card('7', 'H'),  # Duplicate suit
            create_card('7', 'S')
        ]
        self.assertFalse(MeldValidator.is_valid_book(cards, '3'))
    
    def test_book_mixed_ranks(self):
        """Mix of 7s and 8s - invalid"""
        cards = [
            create_card('7', 'H'),
            create_card('8', 'S'),  # Different rank
            create_card('7', 'C')
        ]
        self.assertFalse(MeldValidator.is_valid_book(cards, '3'))
    
    def test_book_all_wilds(self):
        """All wild cards - invalid (need at least one real card)"""
        cards = [
            create_card('5', 'H'),
            create_card('5', 'S'),
            create_card('5', 'C')
        ]
        self.assertFalse(MeldValidator.is_valid_book(cards, '5'))
    
    def test_book_too_few_cards(self):
        """Only 2 cards - invalid"""
        cards = [
            create_card('7', 'H'),
            create_card('7', 'S')
        ]
        self.assertFalse(MeldValidator.is_valid_book(cards, '3'))


class TestValidRuns(unittest.TestCase):
    """Test valid run (sequence) formations"""
    
    def test_simple_run_no_wilds(self):
        """5-6-7 of hearts"""
        cards = [
            create_card('5', 'H'),
            create_card('6', 'H'),
            create_card('7', 'H')
        ]
        self.assertTrue(MeldValidator.is_valid_run(cards, '3'))
    
    def test_run_with_wild_filling_gap(self):
        """5-wild-7 of spades (wild is 3)"""
        cards = [
            create_card('5', 'S'),
            create_card('3', 'S'),  # Wild filling the 6 spot
            create_card('7', 'S')
        ]
        self.assertTrue(MeldValidator.is_valid_run(cards, '3'))
    
    def test_run_long_sequence(self):
        """7-8-9-10-J of clubs"""
        cards = [
            create_card('7', 'C'),
            create_card('8', 'C'),
            create_card('9', 'C'),
            create_card('10', 'C'),
            create_card('J', 'C')
        ]
        self.assertTrue(MeldValidator.is_valid_run(cards, '3'))
    
    def test_run_with_multiple_wilds(self):
        """5-wild-wild-8 of hearts (wilds are 3s)"""
        cards = [
            create_card('5', 'H'),
            create_card('3', 'H'),  # Represents 6
            create_card('3', 'D'),  # Represents 7
            create_card('8', 'H')
        ]
        self.assertTrue(MeldValidator.is_valid_run(cards, '3'))
    
    def test_run_wild_at_end(self):
        """5-6-wild of diamonds"""
        cards = [
            create_card('5', 'D'),
            create_card('6', 'D'),
            create_card('4', 'D')  # Wild representing 7
        ]
        self.assertTrue(MeldValidator.is_valid_run(cards, '4'))


class TestInvalidRuns(unittest.TestCase):
    """Test invalid run formations"""
    
    def test_run_mixed_suits(self):
        """5H-6S-7H - different suits"""
        cards = [
            create_card('5', 'H'),
            create_card('6', 'S'),  # Wrong suit
            create_card('7', 'H')
        ]
        self.assertFalse(MeldValidator.is_valid_run(cards, '3'))
    
    def test_run_gap_too_large(self):
        """5-6-9 with no wilds - gap too large"""
        cards = [
            create_card('5', 'H'),
            create_card('6', 'H'),
            create_card('9', 'H')
        ]
        self.assertFalse(MeldValidator.is_valid_run(cards, '3'))
    
    def test_run_not_enough_wilds_for_gap(self):
        """5-wild-9 (need 2 wilds to fill 6,7,8 but only have 1)"""
        cards = [
            create_card('5', 'H'),
            create_card('3', 'H'),  # Only one wild
            create_card('9', 'H')
        ]
        self.assertFalse(MeldValidator.is_valid_run(cards, '3'))
    
    def test_run_duplicate_ranks(self):
        """5-5-6 - duplicate rank"""
        cards = [
            create_card('5', 'H'),
            create_card('5', 'H'),  # Duplicate
            create_card('6', 'H')
        ]
        self.assertFalse(MeldValidator.is_valid_run(cards, '3'))
    
    def test_run_all_wilds(self):
        """All wild cards - invalid"""
        cards = [
            create_card('3', 'H'),
            create_card('3', 'S'),
            create_card('3', 'C')
        ]
        self.assertFalse(MeldValidator.is_valid_run(cards, '3'))
    
    def test_run_too_few_cards(self):
        """Only 2 cards"""
        cards = [
            create_card('5', 'H'),
            create_card('6', 'H')
        ]
        self.assertFalse(MeldValidator.is_valid_run(cards, '3'))


class TestFullMeldValidation(unittest.TestCase):
    """Test validation of complete hands with multiple melds"""
    
    def test_valid_multiple_melds(self):
        """Two valid melds"""
        melds = [
            # Book of 7s
            [
                create_card('7', 'H'),
                create_card('7', 'S'),
                create_card('7', 'C')
            ],
            # Run 5-6-7 of diamonds
            [
                create_card('5', 'D'),
                create_card('6', 'D'),
                create_card('7', 'D')
            ]
        ]
        result = MeldValidator.validate_all_melds(melds, '3')
        self.assertTrue(result.is_valid)
        self.assertIsNone(result.error_message)
    
    def test_invalid_meld_in_group(self):
        """One valid, one invalid meld"""
        melds = [
            # Valid book
            [
                create_card('7', 'H'),
                create_card('7', 'S'),
                create_card('7', 'C')
            ],
            # Invalid - only 2 cards
            [
                create_card('5', 'D'),
                create_card('6', 'D')
            ]
        ]
        result = MeldValidator.validate_all_melds(melds, '3')
        self.assertFalse(result.is_valid)
        self.assertIn("Group 2", result.error_message)
        self.assertIn("only 2 cards", result.error_message)
    
    def test_neither_book_nor_run(self):
        """Meld that's neither valid book nor run"""
        melds = [
            [
                create_card('5', 'H'),
                create_card('6', 'S'),  # Different suits
                create_card('8', 'D')   # Different ranks
            ]
        ]
        result = MeldValidator.validate_all_melds(melds, '3')
        self.assertFalse(result.is_valid)
        self.assertIn("neither a valid book nor run", result.error_message)
    
    def test_empty_melds_list(self):
        """Empty melds list should be valid"""
        result = MeldValidator.validate_all_melds([], '3')
        self.assertTrue(result.is_valid)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and complex scenarios"""
    
    def test_high_card_run(self):
        """Run with face cards: 10-J-Q-K"""
        cards = [
            create_card('10', 'H'),
            create_card('J', 'H'),
            create_card('Q', 'H'),
            create_card('K', 'H')
        ]
        self.assertTrue(MeldValidator.is_valid_run(cards, '3'))
    
    def test_book_with_wild_that_matches_rank(self):
        """Book of 5s when 5 is wild"""
        cards = [
            create_card('5', 'H'),  # This 5 is wild
            create_card('5', 'S'),  # This 5 is also wild
            create_card('5', 'C')   # All wilds!
        ]
        # Should be invalid - all wilds
        self.assertFalse(MeldValidator.is_valid_book(cards, '5'))
    
    def test_run_with_wild_at_both_ends(self):
        """Wild-6-7-wild of clubs (round 1, 3s wild)"""
        cards = [
            create_card('3', 'C'),  # Wild for 5
            create_card('6', 'C'),
            create_card('7', 'C'),
            create_card('3', 'H')   # Wild for 8
        ]
        self.assertTrue(MeldValidator.is_valid_run(cards, '3'))
    
    def test_minimum_run_length(self):
        """Exactly 3 cards in sequence"""
        cards = [
            create_card('3', 'H'),
            create_card('4', 'H'),
            create_card('5', 'H')
        ]
        self.assertTrue(MeldValidator.is_valid_run(cards, 'K'))
    
    def test_minimum_book_size(self):
        """Exactly 3 cards of same rank"""
        cards = [
            create_card('Q', 'H'),
            create_card('Q', 'S'),
            create_card('Q', 'C')
        ]
        self.assertTrue(MeldValidator.is_valid_book(cards, '3'))


class TestRealGameScenarios(unittest.TestCase):
    """Test scenarios that might occur in real games"""
    
    def test_player_tries_duplicate_suit_in_book(self):
        """Common mistake: two cards of same suit in a book"""
        cards = [
            create_card('8', 'H'),
            create_card('8', 'H'),  # Oops, duplicate!
            create_card('8', 'S')
        ]
        self.assertFalse(MeldValidator.is_valid_book(cards, '3'))
    
    def test_player_confuses_run_and_book(self):
        """Cards that might look like they work but don't"""
        cards = [
            create_card('5', 'H'),
            create_card('6', 'S'),  # Different suit
            create_card('7', 'C')   # Different suit
        ]
        # Not a book (different ranks) and not a run (different suits)
        self.assertFalse(MeldValidator.is_valid_book(cards, '3'))
        self.assertFalse(MeldValidator.is_valid_run(cards, '3'))
    
    def test_complex_hand_round_5(self):
        """Complete hand from round 5 (7s wild, 8 cards)"""
        melds = [
            # Book of Jacks
            [
                create_card('J', 'H'),
                create_card('J', 'S'),
                create_card('J', 'C')
            ],
            # Run 4-5-6-wild(7)-8 of diamonds
            [
                create_card('4', 'D'),
                create_card('5', 'D'),
                create_card('6', 'D'),
                create_card('7', 'D'),  # Wild
                create_card('8', 'D')
            ]
        ]
        result = MeldValidator.validate_all_melds(melds, '7')
        self.assertTrue(result.is_valid)
    
    def test_trying_to_use_wrong_wild(self):
        """Player tries to use 5 as wild when it's round 3 (5s wild)"""
        # This should work - 5 is wild in round 3
        cards = [
            create_card('8', 'H'),
            create_card('8', 'S'),
            create_card('5', 'C')  # Wild
        ]
        self.assertTrue(MeldValidator.is_valid_book(cards, '5'))
        
        # But in round 4, 5 is not wild
        self.assertFalse(MeldValidator.is_valid_book(cards, '6'))


class TestJokerCards(unittest.TestCase):
    """Test joker cards as wild cards"""
    
    def test_joker_creation(self):
        """Test that jokers can be created"""
        joker = create_joker()
        self.assertEqual(joker.rank, 'Joker')
        self.assertEqual(joker.suit, Suit.JOKER)
        self.assertEqual(str(joker), 'Joker')
    
    def test_joker_is_always_wild(self):
        """Jokers should be wild regardless of round"""
        joker = create_joker()
        # Jokers are wild in any round
        self.assertTrue(MeldValidator.is_wild(joker, '3'))
        self.assertTrue(MeldValidator.is_wild(joker, '5'))
        self.assertTrue(MeldValidator.is_wild(joker, 'K'))
    
    def test_book_with_joker(self):
        """Book with a joker as wild card"""
        cards = [
            create_card('7', 'H'),
            create_card('7', 'S'),
            create_joker()  # Joker as wild
        ]
        self.assertTrue(MeldValidator.is_valid_book(cards, '3'))
    
    def test_book_with_joker_and_round_wild(self):
        """Book with both joker and round wild card"""
        cards = [
            create_card('9', 'H'),
            create_joker(),  # Joker
            create_card('5', 'S')  # Round 3 wild (5s are wild)
        ]
        self.assertTrue(MeldValidator.is_valid_book(cards, '5'))
    
    def test_book_multiple_jokers(self):
        """Book with multiple jokers"""
        cards = [
            create_card('8', 'H'),
            create_joker(),
            create_joker()
        ]
        self.assertTrue(MeldValidator.is_valid_book(cards, '3'))
    
    def test_book_all_jokers_invalid(self):
        """All jokers - invalid (need at least one real card)"""
        cards = [
            create_joker(),
            create_joker(),
            create_joker()
        ]
        self.assertFalse(MeldValidator.is_valid_book(cards, '3'))
    
    def test_run_with_joker_filling_gap(self):
        """Run with joker filling a gap"""
        cards = [
            create_card('5', 'H'),
            create_joker(),  # Filling the 6 spot
            create_card('7', 'H')
        ]
        self.assertTrue(MeldValidator.is_valid_run(cards, '3'))
    
    def test_run_with_joker_at_end(self):
        """Run with joker extending the end"""
        cards = [
            create_card('5', 'D'),
            create_card('6', 'D'),
            create_joker()  # Representing 7
        ]
        self.assertTrue(MeldValidator.is_valid_run(cards, '3'))
    
    def test_run_with_joker_at_start(self):
        """Run with joker extending the beginning"""
        cards = [
            create_joker(),  # Representing 4
            create_card('5', 'C'),
            create_card('6', 'C')
        ]
        self.assertTrue(MeldValidator.is_valid_run(cards, '3'))
    
    def test_run_with_multiple_jokers(self):
        """Run with multiple jokers filling gaps"""
        cards = [
            create_card('5', 'H'),
            create_joker(),  # 6
            create_joker(),  # 7
            create_card('8', 'H')
        ]
        self.assertTrue(MeldValidator.is_valid_run(cards, '3'))
    
    def test_run_joker_and_round_wild(self):
        """Run with both joker and round wild card"""
        cards = [
            create_card('4', 'D'),
            create_joker(),  # 5
            create_card('6', 'D'),
            create_card('7', 'D')  # Round 5 wild (7s are wild)
        ]
        self.assertTrue(MeldValidator.is_valid_run(cards, '7'))
    
    def test_run_all_jokers_invalid(self):
        """All jokers - invalid (need at least one real card)"""
        cards = [
            create_joker(),
            create_joker(),
            create_joker()
        ]
        self.assertFalse(MeldValidator.is_valid_run(cards, '3'))
    
    def test_joker_in_complex_meld(self):
        """Joker in a complex multi-meld hand"""
        melds = [
            # Book of 10s with joker
            [
                create_card('10', 'H'),
                create_card('10', 'S'),
                create_joker()
            ],
            # Run 6-7-8-9 with joker filling gap
            [
                create_card('6', 'C'),
                create_joker(),  # 7
                create_card('8', 'C'),
                create_card('9', 'C')
            ]
        ]
        result = MeldValidator.validate_all_melds(melds, '3')
        self.assertTrue(result.is_valid)
    
    def test_joker_suit_doesnt_matter_in_run(self):
        """Joker suit doesn't matter in runs (they're wild)"""
        # Joker can have any suit, but it's still wild
        cards = [
            create_card('5', 'H'),
            create_card('Joker', 'D'),  # Joker with diamond suit (doesn't matter)
            create_card('7', 'H')
        ]
        # This should work - joker is wild regardless of suit
        self.assertTrue(MeldValidator.is_valid_run(cards, '3'))
    
    def test_joker_suit_doesnt_matter_in_book(self):
        """Joker suit doesn't matter in books (they're wild)"""
        cards = [
            create_card('8', 'H'),
            create_card('8', 'S'),
            create_card('Joker', 'C')  # Joker with club suit (doesn't matter)
        ]
        self.assertTrue(MeldValidator.is_valid_book(cards, '3'))
    
    def test_joker_with_face_cards(self):
        """Joker in run with face cards"""
        cards = [
            create_card('10', 'H'),
            create_joker(),  # J
            create_card('Q', 'H'),
            create_card('K', 'H')
        ]
        self.assertTrue(MeldValidator.is_valid_run(cards, '3'))
    
    def test_joker_extending_high_end(self):
        """Joker extending beyond K should be invalid"""
        cards = [
            create_card('J', 'H'),
            create_card('Q', 'H'),
            create_card('K', 'H'),
            create_joker()  # Can't extend beyond K
        ]
        self.assertFalse(MeldValidator.is_valid_run(cards, '3'))
    
    def test_joker_extending_low_end(self):
        """Joker extending below 3 should be invalid"""
        cards = [
            create_joker(),  # Can't extend below 3
            create_card('3', 'H'),
            create_card('4', 'H')
        ]
        self.assertFalse(MeldValidator.is_valid_run(cards, '3'))


if __name__ == '__main__':
    # Run all tests
    unittest.main(verbosity=2)
