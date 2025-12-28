# Five Crowns Card Game

A complete Python implementation of the Five Crowns card game with meld validation, AI opponents, and interactive gameplay.

## What is Five Crowns?

Five Crowns is a rummy-style card game played over 11 rounds. Players try to form their cards into valid melds (books and runs) to minimize their score.

**Key features:**
- **5 suits** instead of 4: Spades (♠), Hearts (♥), Clubs (♣), Diamonds (♦), and Stars (★)
- **Ranks 3-K** (no Aces or 2s)
- **11 rounds** with escalating hand sizes (3 cards in round 1, up to 13 cards in round 11)
- **Rotating wild cards**: 3s are wild in round 1, 4s in round 2, etc.
- **Jokers** are always wild

## Meld Types

### Book (Set)
Three or more cards of the **same rank** with **different suits**.

Examples:
- Valid: 7♥, 7♠, 7♣
- Invalid: 7♥, 7♥, 7♠ (duplicate suit)

### Run (Sequence)
Three or more **consecutive cards** of the **same suit**.

Examples:
- Valid: 5♥, 6♥, 7♥
- Valid with wild: 5♠, wild, 7♠ (wild fills the 6 spot)
- Invalid: 5♥, 6♠, 7♥ (mixed suits)

## Installation

No external dependencies required - just Python 3.7+.

```bash
git clone <repository-url>
cd 5Crowns
```

## Quick Start - Play the Game!

Play Five Crowns against computer opponents:

```bash
python3 play_game.py
```

The game features:
- **Interactive CLI gameplay** - play against 1-3 computer opponents
- **Smart AI opponents** - AI evaluates card usefulness and makes strategic decisions
- **11 rounds** - complete game from round 1 (3s wild) through round 11 (Ks wild)
- **Automatic meld detection** - the game will show you when you can go out
- **Score tracking** - lowest score wins after all rounds

## Usage for Library/Validation

### Basic Validation

```python
from five_crowns import MeldValidator, create_card, create_joker

# Create cards
cards = [
    create_card('7', 'H'),  # 7 of Hearts
    create_card('7', 'S'),  # 7 of Spades
    create_card('7', 'C')   # 7 of Clubs
]

# Validate a book (3s are wild in round 1)
is_valid = MeldValidator.is_valid_book(cards, wild_rank='3')
print(f"Valid book: {is_valid}")  # True
```

### Validating Multiple Melds

```python
from five_crowns import MeldValidator, create_card

# Round 3: 5s are wild
melds = [
    # Book of 7s
    [
        create_card('7', 'H'),
        create_card('7', 'S'),
        create_card('7', 'C')
    ],
    # Run 4-5-6 of Diamonds (5 is wild)
    [
        create_card('4', 'D'),
        create_card('5', 'D'),  # This 5 is wild
        create_card('6', 'D')
    ]
]

result = MeldValidator.validate_all_melds(melds, wild_card_rank='5')
if result.is_valid:
    print("All melds are valid!")
else:
    print(f"Invalid: {result.error_message}")
```

### Working with Jokers

```python
from five_crowns import create_card, create_joker, MeldValidator

# Jokers are always wild
cards = [
    create_card('9', 'H'),
    create_card('9', 'S'),
    create_joker()  # Wild card
]

is_valid = MeldValidator.is_valid_book(cards, wild_rank='3')
print(f"Valid book with joker: {is_valid}")  # True
```

### Determining Wild Card for a Round

```python
from five_crowns import MeldValidator

# Get the wild card rank for any round (1-11)
wild = MeldValidator.get_wild_card(round_number=1)
print(f"Round 1 wild card: {wild}")  # '3'

wild = MeldValidator.get_wild_card(round_number=5)
print(f"Round 5 wild card: {wild}")  # '7'
```

## Running Tests

```bash
# Run meld validation tests
python3 test_five_crowns.py

# Run game engine and AI tests
python3 test_game_engine.py

# Run all tests with verbose output
python3 test_five_crowns.py -v
python3 test_game_engine.py -v

# Run specific test class
python3 -m unittest test_five_crowns.TestValidBooks

# Run single test
python3 -m unittest test_five_crowns.TestValidBooks.test_simple_book_no_wilds
```

## Project Structure

```
5Crowns/
├── five_crowns.py         # Meld validation logic (core rules)
├── game_engine.py         # Game state, deck, players, turn management
├── meld_finder.py         # Algorithms to find optimal meld combinations
├── ai_player.py           # AI strategy and decision-making
├── play_game.py           # Interactive CLI game (main entry point)
├── test_five_crowns.py    # Meld validation tests (51 tests)
├── test_game_engine.py    # Game engine and AI tests (20 tests)
├── CLAUDE.md              # Development guide for AI assistants
└── README.md              # This file
```

## Key Rules

1. **Minimum meld size**: 3 cards
2. **Wild cards**: Can substitute for any card, but melds must contain at least one non-wild card
3. **Books**: Cannot have duplicate suits (among non-wild cards)
4. **Runs**: Cannot extend below rank 3 or above rank K
5. **When a rank is wild**: ALL cards of that rank become wild (e.g., in round 3, all 5s are wild regardless of suit)

## API Reference

### Core Classes (five_crowns.py)

- **`Card`**: Represents a card with rank and suit
- **`Suit`**: Enum for card suits (SPADES, HEARTS, CLUBS, DIAMONDS, STARS, JOKER)
- **`MeldValidator`**: Static methods for validating melds
- **`ValidationResult`**: Contains validation result and optional error message

### Game Engine Classes (game_engine.py)

- **`Deck`**: Manages the 116-card Five Crowns deck
- **`Player`**: Represents a player (human or AI) with hand and score
- **`GameState`**: Tracks current round, players, deck, and game status
- **`GameEngine`**: Main game controller for turn management

### Meld Finding (meld_finder.py)

- **`MeldFinder`**: Algorithms to find all possible melds and optimal combinations
  - `find_all_books()`: Find all valid books in a hand
  - `find_all_runs()`: Find all valid runs in a hand
  - `find_best_meld_combination()`: Find optimal melds that minimize remaining points
  - `can_go_out()`: Check if hand can form complete melds

### AI Strategy (ai_player.py)

- **`AIStrategy`**: AI decision-making algorithms
  - `evaluate_card_usefulness()`: Score cards based on meld potential
  - `decide_draw_source()`: Choose between deck and discard pile
  - `decide_discard()`: Select least useful card to discard
  - `should_go_out()`: Decide when to attempt going out
- **`AIPlayer`**: Executes complete AI turns

### Validation Functions

- **`MeldValidator.validate_all_melds(melds, wild_card_rank)`**: Validate complete hand
- **`MeldValidator.is_valid_book(cards, wild_rank)`**: Check if cards form valid book
- **`MeldValidator.is_valid_run(cards, wild_rank)`**: Check if cards form valid run
- **`MeldValidator.get_wild_card(round_number)`**: Get wild rank for a round (1-11)
- **`MeldValidator.is_wild(card, wild_rank)`**: Check if card is wild
- **`create_card(rank, suit)`**: Helper to create cards (suit: S/H/C/D/T)
- **`create_joker()`**: Helper to create joker cards

## Examples

### Valid Melds

```python
# Book of Queens
[create_card('Q', 'H'), create_card('Q', 'S'), create_card('Q', 'C')]

# Run with face cards
[create_card('10', 'H'), create_card('J', 'H'), create_card('Q', 'H')]

# Run with wild card filling gap (3s wild)
[create_card('5', 'D'), create_card('3', 'D'), create_card('7', 'D')]
```

### Invalid Melds

```python
# Duplicate suit in book
[create_card('7', 'H'), create_card('7', 'H'), create_card('7', 'S')]

# Mixed suits in run
[create_card('5', 'H'), create_card('6', 'S'), create_card('7', 'H')]

# All wild cards (no real card)
[create_joker(), create_joker(), create_joker()]
```

## License

This project is provided as-is for educational and recreational purposes.
