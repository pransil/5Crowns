#!/usr/bin/env python3
"""
Five Crowns - Main Game Loop
Play Five Crowns against computer opponents
"""

import sys
from typing import List, Optional
from game_engine import GameEngine, Player
from ai_player import AIPlayer, AIStrategy
from meld_finder import MeldFinder
from five_crowns import Card, MeldValidator


class GameUI:
    """User interface for the game"""

    @staticmethod
    def display_hand(player: Player, wild_rank: str):
        """Display a player's hand"""
        print(f"\n{player.name}'s hand:")
        player.sort_hand()

        for i, card in enumerate(player.hand, 1):
            wild_marker = " (WILD)" if MeldValidator.is_wild(card, wild_rank) else ""
            print(f"  {i}. {card}{wild_marker}")

    @staticmethod
    def display_scores(players: List[Player]):
        """Display current scores"""
        print("\n" + "=" * 50)
        print("SCORES:")
        for player in players:
            print(f"  {player.name}: {player.score} points")
        print("=" * 50)

    @staticmethod
    def display_game_state(engine: GameEngine):
        """Display current game state"""
        state = engine.state
        print(f"\n{'='*50}")
        print(f"ROUND {state.round_number} - Wild card: {state.get_wild_rank()}")
        print(f"{'='*50}")

        discard = state.deck.peek_discard()
        if discard:
            wild_marker = " (WILD)" if MeldValidator.is_wild(discard, state.get_wild_rank()) else ""
            print(f"Top of discard pile: {discard}{wild_marker}")
        print(f"Cards in deck: {state.deck.cards_remaining()}")

    @staticmethod
    def get_player_draw_choice(discard_card: Optional[Card], wild_rank: str) -> bool:
        """Ask player where to draw from. Returns True for discard, False for deck."""
        if discard_card is None:
            print("\nDiscard pile is empty. Drawing from deck.")
            return False

        wild_marker = " (WILD)" if MeldValidator.is_wild(discard_card, wild_rank) else ""
        print(f"\nTop of discard pile: {discard_card}{wild_marker}")

        while True:
            choice = input("Draw from (d)eck or (p)ile? ").strip().lower()
            if choice == 'd':
                return False
            elif choice == 'p':
                return True
            else:
                print("Invalid choice. Enter 'd' for deck or 'p' for pile.")

    @staticmethod
    def get_player_discard_choice(player: Player, wild_rank: str) -> Card:
        """Ask player which card to discard"""
        GameUI.display_hand(player, wild_rank)

        while True:
            try:
                choice = input(f"\nWhich card to discard (1-{len(player.hand)})? ").strip()
                idx = int(choice) - 1

                if 0 <= idx < len(player.hand):
                    return player.hand[idx]
                else:
                    print(f"Please enter a number between 1 and {len(player.hand)}")
            except ValueError:
                print("Please enter a valid number")

    @staticmethod
    def ask_go_out(player: Player, wild_rank: str) -> bool:
        """Ask if player wants to try to go out"""
        while True:
            choice = input("\nDo you want to try to go out? (y/n) ").strip().lower()
            if choice == 'y':
                return True
            elif choice == 'n':
                return False
            else:
                print("Please enter 'y' or 'n'")

    @staticmethod
    def display_melds(melds: List[List[Card]], wild_rank: str):
        """Display melds"""
        for i, meld in enumerate(melds, 1):
            cards_str = ", ".join(
                f"{card}{'(W)' if MeldValidator.is_wild(card, wild_rank) else ''}"
                for card in meld
            )
            print(f"  Meld {i}: {cards_str}")

    @staticmethod
    def let_player_arrange_melds(player: Player, wild_rank: str) -> List[List[Card]]:
        """Let player manually arrange their cards into melds"""
        print(f"\n{player.name}, arrange your remaining cards into melds:")

        available_cards = player.hand.copy()
        melds = []

        while True:
            print(f"\nAvailable cards ({len(available_cards)} remaining):")
            for i, card in enumerate(available_cards, 1):
                wild_marker = " (WILD)" if MeldValidator.is_wild(card, wild_rank) else ""
                print(f"  {i}. {card}{wild_marker}")

            if not available_cards:
                print("\nNo cards left!")
                break

            # Show suggestion from computer
            suggestion_melds, suggestion_points = MeldFinder.find_best_meld_combination(available_cards, wild_rank)
            if suggestion_melds:
                print(f"\nSuggestion (leaves {suggestion_points} points):")
                for i, meld in enumerate(suggestion_melds, 1):
                    cards_str = ", ".join(
                        f"{card}{'(W)' if MeldValidator.is_wild(card, wild_rank) else ''}"
                        for card in meld
                    )
                    print(f"  Meld {i}: {cards_str}")

            choice = input("\nEnter card numbers for a meld (e.g., '1 2 3'), or 'done' to finish: ").strip().lower()

            if choice == 'done':
                break

            try:
                indices = [int(x) - 1 for x in choice.split()]

                if not indices:
                    continue

                if any(i < 0 or i >= len(available_cards) for i in indices):
                    print("Invalid card numbers!")
                    continue

                # Get the selected cards
                selected_cards = [available_cards[i] for i in indices]

                # Validate the meld
                is_book = MeldValidator.is_valid_book(selected_cards, wild_rank)
                is_run = MeldValidator.is_valid_run(selected_cards, wild_rank)

                if is_book or is_run:
                    meld_type = "book" if is_book else "run"
                    print(f"✓ Valid {meld_type}!")
                    melds.append(selected_cards)

                    # Remove used cards
                    for i in sorted(indices, reverse=True):
                        available_cards.pop(i)
                else:
                    print("✗ Invalid meld! Must be a valid book (same rank, different suits) or run (consecutive ranks, same suit)")

            except ValueError:
                print("Invalid input! Enter card numbers separated by spaces (e.g., '1 2 3')")

        return melds

    @staticmethod
    def announce_round_end(players: List[Player], wild_rank: str, winner_name: str):
        """Announce round results"""
        print(f"\n{winner_name} went out!")
        print("\nRound scores:")

        for player in players:
            if player.hand:
                # Let human players arrange their own melds
                if player.is_human:
                    melds = GameUI.let_player_arrange_melds(player, wild_rank)
                else:
                    # Computer players use optimal meld finder
                    melds, _ = MeldFinder.find_best_meld_combination(player.hand, wild_rank)

                # Calculate points for remaining cards
                cards_in_melds = set(id(card) for meld in melds for card in meld)
                remaining_cards = [card for card in player.hand if id(card) not in cards_in_melds]

                remaining_points = 0
                for card in remaining_cards:
                    if MeldValidator.is_wild(card, wild_rank):
                        remaining_points += 20
                    elif card.rank in ['J', 'Q', 'K']:
                        remaining_points += 10
                    else:
                        remaining_points += int(card.rank)

                # Add to player's score
                player.score += remaining_points

                print(f"\n  {player.name}: +{remaining_points} points")

                if melds:
                    print(f"    Melds laid down:")
                    for i, meld in enumerate(melds, 1):
                        cards_str = ", ".join(
                            f"{card}{'(W)' if MeldValidator.is_wild(card, wild_rank) else ''}"
                            for card in meld
                        )
                        print(f"      Meld {i}: {cards_str}")

                if remaining_cards:
                    print(f"    Remaining cards:")
                    for card in remaining_cards:
                        wild_marker = " (WILD)" if MeldValidator.is_wild(card, wild_rank) else ""
                        print(f"      {card}{wild_marker}")
            else:
                print(f"  {player.name}: 0 points (went out)")


def play_human_turn(engine: GameEngine, player: Player) -> bool:
    """
    Play a human player's turn.
    Returns True if player went out.
    """
    state = engine.state
    wild_rank = state.get_wild_rank()

    print(f"\n{'*'*50}")
    print(f"{player.name}'s turn")
    print('*'*50)

    # Display hand
    GameUI.display_hand(player, wild_rank)

    # Draw phase
    discard_top = state.deck.peek_discard()
    from_discard = GameUI.get_player_draw_choice(discard_top, wild_rank)

    if from_discard:
        drawn = engine.draw_card(from_discard=True)
        print(f"\nDrew from discard pile: {drawn}")
    else:
        drawn = engine.draw_card(from_discard=False)
        wild_marker = " (WILD)" if MeldValidator.is_wild(drawn, wild_rank) else ""
        print(f"\nDrew from deck: {drawn}{wild_marker}")

    # Check if player wants to go out
    if GameUI.ask_go_out(player, wild_rank):
        can_go_out, melds = MeldFinder.can_go_out(player.hand, wild_rank)
        if can_go_out:
            success, error = engine.try_go_out(melds)
            if success:
                return True
            else:
                print(f"ERROR: Could not go out - {error}")

    # Discard phase
    card_to_discard = GameUI.get_player_discard_choice(player, wild_rank)
    engine.discard_card(card_to_discard)
    print(f"\nDiscarded: {card_to_discard}")

    return False


def play_round(engine: GameEngine) -> str:
    """
    Play a single round.
    Returns the name of the player who went out.
    """
    engine.setup_round()
    GameUI.display_game_state(engine)

    winner_name = None
    going_out_player_index = None

    # Play until someone goes out, then let others finish the round
    while True:
        # Check if round should end (before taking turn)
        # Round ends when we've cycled back to the player who went out
        if going_out_player_index is not None:
            if engine.state.current_player_index == going_out_player_index:
                # We've come full circle - everyone else has had their turn
                break

        current_player = engine.state.current_player()

        if current_player.is_human:
            went_out = play_human_turn(engine, current_player)
        else:
            # AI turn
            print(f"\n{'*'*50}")
            print(f"{current_player.name}'s turn")
            print('*'*50)

            went_out, turn_info = AIPlayer.take_turn(engine, current_player)

            wild_rank = engine.state.get_wild_rank()

            # Show where AI drew from
            if turn_info['draw_source'] == 'discard':
                drew_card = turn_info['drew_card']
                wild_marker = " (WILD)" if MeldValidator.is_wild(drew_card, wild_rank) else ""
                print(f"{current_player.name} drew from discard pile: {drew_card}{wild_marker}")
            else:
                print(f"{current_player.name} drew from the deck")

            if went_out:
                print(f"\n{current_player.name} went out!")
            else:
                # Show what AI discarded
                if turn_info['discarded']:
                    discarded = turn_info['discarded']
                    wild_marker = " (WILD)" if MeldValidator.is_wild(discarded, wild_rank) else ""
                    print(f"{current_player.name} discarded: {discarded}{wild_marker}")

        if went_out and going_out_player_index is None:
            # First player to go out
            winner_name = current_player.name
            going_out_player_index = engine.state.current_player_index
            print(f"\n*** {winner_name} went out! Other players get one more turn. ***")

        # Move to next player
        engine.state.next_player()

    engine.state.round_over = True
    return winner_name


def main():
    """Main game loop"""
    print("=" * 50)
    print("FIVE CROWNS")
    print("=" * 50)

    # Setup players
    print("\nHow many computer opponents? (1-3): ", end="")
    try:
        num_ai = int(input().strip())
        if num_ai < 1 or num_ai > 3:
            print("Invalid number. Using 1 opponent.")
            num_ai = 1
    except ValueError:
        print("Invalid input. Using 1 opponent.")
        num_ai = 1

    # Create players
    player_names = input("\nEnter your name: ").strip() or "Player"
    players = [(player_names, True)]  # Human player

    for i in range(num_ai):
        players.append((f"Computer {i+1}", False))

    # Create game
    engine = GameEngine(players)

    # Play all 11 rounds
    for round_num in range(1, 12):
        engine.state.round_number = round_num

        print(f"\n\n{'#'*50}")
        print(f"STARTING ROUND {round_num}")
        print(f"{'#'*50}")

        winner_name = play_round(engine)

        # Save the wild rank BEFORE ending the round (which increments round_number)
        current_wild_rank = engine.state.get_wild_rank()

        # Let players arrange melds and calculate scores
        GameUI.announce_round_end(engine.state.players, current_wild_rank, winner_name)
        GameUI.display_scores(engine.state.players)

        # Move to next round
        engine.end_round()

        if round_num < 11:
            input("\nPress Enter to continue to next round...")

    # Game over
    engine.state.game_over = True
    winner = engine.get_winner()

    print("\n\n" + "=" * 50)
    print("GAME OVER!")
    print("=" * 50)

    GameUI.display_scores(engine.state.players)

    if winner:
        print(f"\n🏆 {winner.name} WINS with {winner.score} points! 🏆")

    print("\nThanks for playing!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nGame cancelled. Thanks for playing!")
        sys.exit(0)
