# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a complete Python implementation of the Five Crowns card game including:
- **Meld validation engine** - validates books and runs according to game rules
- **Game engine** - manages deck, players, turns, and game state
- **Meld finder** - algorithms to discover all possible melds and optimal combinations
- **AI opponent** - intelligent computer player with strategic decision-making
- **Interactive CLI game** - play against 1-3 computer opponents

Five Crowns is a rummy-style card game with 11 rounds where players form books (sets) and runs (sequences).

## Playing the Game

```bash
# Play Five Crowns against computer opponents
python3 play_game.py
```

## Running Tests

```bash
# Run meld validation tests (51 tests)
python3 test_five_crowns.py

# Run game engine and AI tests (20 tests)
python3 test_game_engine.py

# Run specific test class
python3 -m unittest test_five_crowns.TestValidBooks

# Run single test
python3 -m unittest test_five_crowns.TestValidBooks.test_simple_book_no_wilds
```

## Game Rules Implementation

### Five Crowns Specifics
- **5 suits**: Spades, Hearts, Clubs, Diamonds, and Stars (★)
- **Ranks**: 3 through K (no Aces or 2s)
- **11 rounds**: Round 1 = 3 cards dealt (3s wild), Round 2 = 4 cards (4s wild), ..., Round 11 = 13 cards (Ks wild)
- **Jokers**: Always wild, regardless of round

### Meld Types
1. **Book (Set)**: 3+ cards of same rank with different suits
   - Cannot have duplicate suits among non-wild cards
   - Requires at least one non-wild card
   - Example: 7♥, 7♠, 7♣

2. **Run (Sequence)**: 3+ consecutive cards of same suit
   - All non-wild cards must be same suit
   - Wild cards can fill gaps or extend ends
   - Cannot extend below rank 3 or above rank K
   - Requires at least one non-wild card
   - Example: 5♥, 6♥, 7♥

## Code Architecture

The codebase is organized into distinct modules with clear responsibilities:

### Core Modules

**`five_crowns.py`** - Meld validation (core game rules)
- `Card`: Dataclass representing a card (rank + suit)
- `Suit`: Enum for the 5 suits plus Joker suit
- `MeldValidator`: Static class containing all validation logic
- `ValidationResult`: Return type for validation functions

**`game_engine.py`** - Game state and turn management
- `Deck`: Manages 116-card deck (2 copies × 11 ranks × 5 suits + 6 jokers)
- `Player`: Represents a player with hand, score, and human/AI flag
- `GameState`: Tracks current round, players, deck, turn order
- `GameEngine`: Main controller for game flow (setup, draw, discard, go out)

**`meld_finder.py`** - Meld discovery and optimization
- `MeldFinder`: Algorithms to find all possible melds from a hand
- `find_all_books()`: Discovers all valid book combinations
- `find_all_runs()`: Discovers all valid run combinations
- `find_best_meld_combination()`: Greedy algorithm to minimize remaining points
- `can_go_out()`: Checks if hand can form complete melds (0 remaining points)

**`ai_player.py`** - AI strategy
- `AIStrategy`: Card evaluation and decision-making
- `AIPlayer`: Executes full AI turns (draw, evaluate, discard/go out)

**`play_game.py`** - Interactive CLI game
- `GameUI`: User interface for displaying game state and getting input
- `play_human_turn()`: Handles human player interaction
- `play_round()`: Orchestrates a single round
- `main()`: Complete 11-round game loop

### Key Validation Logic

The validator uses a **non-optimizing approach** - it only checks if player-submitted melds are valid, without suggesting better arrangements.

**`MeldValidator.validate_all_melds(melds, wild_card_rank)`** (five_crowns.py:63)
- Entry point for validating a complete hand
- Checks each meld is either a valid book OR valid run
- Returns `ValidationResult` with error details for first invalid meld

**`MeldValidator.is_valid_book(cards, wild_rank)`** (five_crowns.py:96)
- Validates book formation
- Key constraint: no duplicate suits among non-wilds (five_crowns.py:118-122)

**`MeldValidator.is_valid_run(cards, wild_rank)`** (five_crowns.py:127)
- Validates run formation
- Complex logic for wild card gap-filling (five_crowns.py:159-167)
- Boundary checking prevents extending beyond 3-K range (five_crowns.py:181-221)

### Wild Card Handling

Wild cards are determined per round via `MeldValidator.get_wild_card(round_number)` (five_crowns.py:50). Jokers are always wild.

**Critical rule**: `MeldValidator.is_wild(card, wild_rank)` (five_crowns.py:91)
- Returns True for Jokers OR cards matching the round's wild rank
- When a rank is wild (e.g., 5s in round 3), ALL cards of that rank become wild
- Melds with only wild cards are invalid - at least one non-wild required

### Run Validation Algorithm

The run validator (five_crowns.py:127-223) handles complex scenarios:
1. Separates wilds from non-wilds
2. Sorts non-wilds by rank value
3. Calculates gaps between consecutive non-wild cards
4. Verifies enough wilds exist to fill gaps (five_crowns.py:165-167)
5. Handles excess wilds extending sequence ends
6. Enforces boundary constraints (no extending below 3 or above K)

**Edge case**: When sequence includes K, cannot add wilds at high end (five_crowns.py:212-214). Similarly for sequences starting at 3 (five_crowns.py:215-217).

## AI Strategy Details

The AI opponent uses heuristic evaluation to make decisions:

### Card Usefulness Scoring (ai_player.py:19)
- Wild cards: 100 points (highest priority)
- Cards with same-rank duplicates: +15 per duplicate (book potential)
- Cards near same-suit cards: +20 (adjacent), +10 (one gap), +5 (two gaps)
- High point cards slightly penalized (easier to go out with low points)

### Draw Decision (ai_player.py:54)
- Always takes wilds from discard pile
- Takes cards with usefulness score > 25
- Otherwise draws from deck (unknown card)

### Discard Decision (ai_player.py:65)
- Evaluates usefulness of each card in hand
- Discards least useful card (lowest score)

### Go Out Decision (ai_player.py:76)
- Uses `MeldFinder.can_go_out()` to check if possible
- Currently goes out whenever possible (could be enhanced with strategic delay)

## Meld Finding Algorithm

The `MeldFinder` uses exhaustive search with greedy optimization:

1. **Find all possible melds** - Generates all valid books and runs from hand
2. **Deduplicate** - Removes duplicate meld combinations
3. **Greedy selection** - Iteratively selects melds that save the most points
4. **Backtracking** - Tries different starting melds to find global optimum

This approach works well for the hand sizes in Five Crowns (3-13 cards) but could be slow for larger hands.

## Helper Functions

- `create_card(rank, suit)`: Create cards using short notation (e.g., `create_card('7', 'H')`)
- `create_joker()`: Create a Joker card (always wild)

Suit notation: S=Spades, H=Hearts, C=Clubs, D=Diamonds, T=Stars, J=Joker
